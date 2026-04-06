import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mlkit_face_mesh_detection/google_mlkit_face_mesh_detection.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../data/models/color_analysis_response.dart';
import '../../../ar_tryon/data/models/ar_shade_model.dart';
import '../../../ar_tryon/data/models/ar_tryon_state.dart';
import '../../../ar_tryon/presentation/providers/ar_tryon_provider.dart';
import '../widgets/ar_top_product_banner.dart';
import '../widgets/ar_swatch_bottom_panel.dart';
import '../widgets/coordinate_translator.dart';
import '../widgets/lip_mesh_extractor.dart';
import '../widgets/lipstick_painter.dart';



class ArTryonScreen extends ConsumerStatefulWidget {
  /// Session ID passed from the SCA flow (SCA entry).
  final int? sessionId;

  /// Full list of products passed from the Dashboard (Dashboard entry).
  final List<ProductRecommendation>? dashboardProducts;

  /// The ID of the specific product tapped on the Dashboard.
  final int? selectedDashboardId;

  const ArTryonScreen({
    super.key,
    this.sessionId,
    this.dashboardProducts,
    this.selectedDashboardId,
  });

  @override
  ConsumerState<ArTryonScreen> createState() => _ArTryonScreenState();
}

class _ArTryonScreenState extends ConsumerState<ArTryonScreen>
    with WidgetsBindingObserver {
  // ── Camera & ML Kit ───────────────────────────────────────────────────────
  CameraController?  _cameraController;
  late final FaceMeshDetector _faceMeshDetector;
  bool _isBusy = false;

  // ── Lipstick controller ───────────────────────────────────────────────────
  // Drives repaints of the LipstickPainter WITHOUT setState / widget rebuilds.
  late final LipstickController _lipController;

  // ── UI State (infrequent – setState is fine) ──────────────────────────────
  bool _cameraReady = false;

  // ── EWMA smoothing factor (0 = frozen, 1 = raw) ───────────────────────────
  static const double _kSmoothingAlpha = 0.8;

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    _lipController = LipstickController();

    _faceMeshDetector = FaceMeshDetector(
      option: FaceMeshDetectorOptions.faceMesh,
    );

    _initCamera();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(arTryonProvider.notifier).init(
        sessionId: widget.sessionId,
        dashboardProducts: widget.dashboardProducts,
        selectedDashboardId: widget.selectedDashboardId,
      );
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final controller = _cameraController;
    if (controller == null || !controller.value.isInitialized) return;
    if (state == AppLifecycleState.inactive) {
      _stopStream();
    } else if (state == AppLifecycleState.resumed) {
      _startStream(controller);
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _stopStream();
    _cameraController?.dispose();
    _faceMeshDetector.close();
    _lipController.dispose();
    super.dispose();
  }

  // Proactively stop the stream before the navigator tears down the widget.
  // This prevents the CameraX LiveData observer from firing into a dead
  // PlatformChannel and causing the fatal ObserverProxyApi crash.
  Future<bool> _onPopInvoked() async {
    _stopStream();
    // Small pause so CameraX can finish its last observer notification
    // before Flutter destroys the method channel.
    await Future<void>.delayed(const Duration(milliseconds: 150));
    return true; // allow the pop
  }

  // ── Camera Helpers ────────────────────────────────────────────────────────

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    if (cameras.isEmpty) return;

    final frontCamera = cameras.firstWhere(
      (c) => c.lensDirection == CameraLensDirection.front,
      orElse: () => cameras.first,
    );

    // ResolutionPreset.low ≈ 320×240 — smaller image means:
    //   • ~44 % fewer NV21 bytes to compose on the isolate
    //   • ML Kit face mesh runs ~40 % faster
    //   • Coordinate translator still uses screen-space math so accuracy
    //     is unaffected; only the input image is smaller.
    final controller = CameraController(
      frontCamera,
      ResolutionPreset.high,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.nv21,
    );

    await controller.initialize();
    if (!mounted) return;
    _cameraController = controller;
    setState(() => _cameraReady = true);
    _startStream(controller);
  }

  void _startStream(CameraController controller) {
    if (controller.value.isStreamingImages) return;
    controller.startImageStream((CameraImage image) async {
      if (_isBusy) return;
      _isBusy = true;
      try {
        await _processFrame(image);
      } finally {
        _isBusy = false;
      }
    });
  }

  void _stopStream() {
    final controller = _cameraController;
    if (controller == null) return;
    if (controller.value.isStreamingImages) controller.stopImageStream();
  }

  // ── Frame Processing ──────────────────────────────────────────────────────

  Future<void> _processFrame(CameraImage image) async {
    final controller = _cameraController;
    if (controller == null) return;

    final cameraDescription = controller.description;
    final deviceRotation    = controller.value.deviceOrientation.rawValue;

    // Read MediaQuery BEFORE any async gap (use_build_context_synchronously).
    final screenSize = MediaQuery.of(context).size;
    final isMirrored =
        cameraDescription.lensDirection == CameraLensDirection.front;

    // ── NV21 composition ─────────────────────────────────────────────────
    final inputImage = convertCameraImageToInputImage(
      image,
      cameraDescription,
      deviceRotation,
    );
    if (inputImage == null) return;

    // ── ML Kit face mesh ─────────────────────────────────────────────────
    final meshes = await _faceMeshDetector.processImage(inputImage);
    if (meshes.isEmpty) {
      // Clear overlay without setState — controller notifies the painter only.
      _lipController.updateContours(null);
      return;
    }

    // ── BoxFit.cover-aware coordinate dimensions ─────────────────────────
    final sensorOrientation = cameraDescription.sensorOrientation;
    final int rotationCompensation =
        cameraDescription.lensDirection == CameraLensDirection.front
            ? (sensorOrientation + deviceRotation) % 360
            : (sensorOrientation - deviceRotation + 360) % 360;

    final bool swapDims =
        rotationCompensation == 90 || rotationCompensation == 270;
    final int effectiveImageWidth  = swapDims ? image.height : image.width;
    final int effectiveImageHeight = swapDims ? image.width  : image.height;

    final translator = CoordinateTranslator(
      imageWidth:        effectiveImageWidth,
      imageHeight:       effectiveImageHeight,
      screenWidth:       screenSize.width,
      screenHeight:      screenSize.height,
      isPainterMirrored: isMirrored,
    );

    final rawContours = LipMeshExtractor(
      translateX: translator.translateX,
      translateY: translator.translateY,
    ).extract(meshes.first);

    if (rawContours == null) return;

    // ── EWMA temporal smoothing ───────────────────────────────────────────
    final prev = _lipController.lipContours;
    final smoothed = prev == null
        ? rawContours
        : LipContours(
            outer: _smoothPoints(prev.outer, rawContours.outer),
            inner: _smoothPoints(prev.inner, rawContours.inner),
          );

    // ── Push to painter — no setState, no widget rebuild ─────────────────
    _lipController.updateContours(smoothed);
  }

  List<Offset> _smoothPoints(List<Offset> prev, List<Offset> next) {
    if (prev.length != next.length) return next;
    return List<Offset>.generate(next.length, (i) => Offset(
      prev[i].dx + _kSmoothingAlpha * (next[i].dx - prev[i].dx),
      prev[i].dy + _kSmoothingAlpha * (next[i].dy - prev[i].dy),
    ));
  }

  // ── Shade → Color helpers ─────────────────────────────────────────────────

  Color _hexToColor(String hex) {
    try {
      final s = hex.replaceFirst('#', '');
      return Color(int.parse(s.length == 6 ? 'FF$s' : s, radix: 16));
    } catch (_) {
      return const Color(0xFF982A2A);
    }
  }

  ArShadeModel? _resolveShade(ArTryonState state) {
    final id = state.selectedShadeId;
    if (id == null) return null;
    return state.allShades.cast<ArShadeModel?>().firstWhere(
      (s) => s?.id == id,
      orElse: () => null,
    );
  }

  void _syncColor(ArTryonState state) {
    final shade = _resolveShade(state);
    _lipController.updateColor(
      shade != null ? _hexToColor(shade.colorHex) : const Color(0xFF982A2A),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final arState = ref.watch(arTryonProvider);

    // Keep controller color in sync whenever the selected shade changes.
    // ref.listen is called in build() per Riverpod convention.
    ref.listen<ArTryonState>(arTryonProvider, (_, next) => _syncColor(next));
    // Sync for the current build (first render or hot-restart).
    _syncColor(arState);

    // Banner still needs the shade object for display text.
    final selectedShade = _resolveShade(arState);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        final canPop = await _onPopInvoked();
        if (canPop && mounted) {
          Navigator.of(context).pop();
        }
      },
      child: Scaffold(
        backgroundColor: Colors.black,
        body: Stack(
          fit: StackFit.expand,
          children: [
            _buildArCameraLayer(),
            Positioned(
              top: 0, left: 0, right: 0,
              child: ArTopProductBanner(selectedShade: selectedShade),
            ),
            Positioned(
              bottom: 0, left: 0, right: 0,
              child: ArSwatchBottomPanel(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildArCameraLayer() {
    final controller = _cameraController;
    return GestureDetector(
      onLongPressStart: (_) {
        _lipController.setVisible(false); // hide overlay via controller, no setState
      },
      onLongPressEnd: (_) {
        _lipController.setVisible(true);
      },
      child: Stack(
        fit: StackFit.expand,
        children: [
          // ── Camera preview ───────────────────────────────────────────────
          if (_cameraReady && controller != null && controller.value.isInitialized)
            ClipRect(
              child: OverflowBox(
                alignment: Alignment.center,
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: SizedBox(
                    // Swap width/height: sensor is landscape; display is portrait.
                    width:  controller.value.previewSize!.height,
                    height: controller.value.previewSize!.width,
                    child:  CameraPreview(controller),
                  ),
                ),
              ),
            )
          else
            Container(
              color: const Color(0xFF2C2C2C),
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(color: GlowTheme.oatmeal),
                    SizedBox(height: 16),
                    Text(
                      'Initialising Camera…',
                      style: TextStyle(
                        color: GlowTheme.oatmeal,
                        fontSize: 14,
                        fontFamily: 'PlayfairDisplay',
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // ── AR overlay ───────────────────────────────────────────────────
          // RepaintBoundary isolates the CustomPaint raster layer from the
          // rest of the widget tree. When the controller notifies, only the
          // pixels inside this boundary are re-composited on the GPU thread —
          // zero cost to the rest of the UI.
          RepaintBoundary(
            child: CustomPaint(
              painter: LipstickPainter(controller: _lipController),
            ),
          ),

          // ── "HOLD TO COMPARE" hint ───────────────────────────────────────
          Positioned(
            top: MediaQuery.of(context).padding.top + 80,
            left: 0, right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: const Text(
                  'HOLD TO COMPARE',
                  style: TextStyle(
                    color: GlowTheme.pearlWhite,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.2,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Extension ─────────────────────────────────────────────────────────────────

extension _DeviceOrientationExt on DeviceOrientation {
  int get rawValue {
    switch (this) {
      case DeviceOrientation.portraitUp:     return 0;
      case DeviceOrientation.landscapeRight: return 90;
      case DeviceOrientation.portraitDown:   return 180;
      case DeviceOrientation.landscapeLeft:  return 270;
    }
  }
}

import 'dart:async';
import 'package:camera/camera.dart';
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
  final ProductRecommendation? product;

  const ArTryonScreen({super.key, this.product});

  @override
  ConsumerState<ArTryonScreen> createState() => _ArTryonScreenState();
}

class _ArTryonScreenState extends ConsumerState<ArTryonScreen>
    with WidgetsBindingObserver {
  // ── Camera & ML Kit ───────────────────────────────────────────────────────
  CameraController? _cameraController;
  late final FaceMeshDetector _faceMeshDetector;
  bool _isBusy = false;

  // ── UI State ──────────────────────────────────────────────────────────────
  bool _isComparing = false;
  LipContours? _lipContours;

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _faceMeshDetector = FaceMeshDetector(
      option: FaceMeshDetectorOptions.faceMesh,
    );
    _initCamera();

    // Load the initial shade catalogue from the provider.
    // Using addPostFrameCallback so the widget tree is fully mounted before
    // the provider mutates state.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(arTryonProvider.notifier).init(product: widget.product);
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
    super.dispose();
  }

  // ── Camera Helpers ────────────────────────────────────────────────────────

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    if (cameras.isEmpty) return;

    // Prefer front-facing camera for try-on
    final frontCamera = cameras.firstWhere(
      (c) => c.lensDirection == CameraLensDirection.front,
      orElse: () => cameras.first,
    );

    final controller = CameraController(
      frontCamera,
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.nv21,
    );

    await controller.initialize();
    if (!mounted) return;
    _cameraController = controller;
    setState(() {});
    _startStream(controller);
  }

  void _startStream(CameraController controller) {
    if (controller.value.isStreamingImages) return;
    controller.startImageStream((CameraImage image) async {
      // Frame throttle: skip if previous frame is still being processed.
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
    if (controller.value.isStreamingImages) {
      controller.stopImageStream();
    }
  }

  // ── Frame Processing ──────────────────────────────────────────────────────

  Future<void> _processFrame(CameraImage image) async {
    final controller = _cameraController;
    if (controller == null) return;

    final cameraDescription = controller.description;

    // Get current device rotation (0, 90, 180, 270).
    final deviceRotation =
        controller.value.deviceOrientation.rawValue;

    // Capture context-dependent values BEFORE the async gap to satisfy
    // use_build_context_synchronously.
    final screenSize = MediaQuery.of(context).size;
    final isMirrored =
        cameraDescription.lensDirection == CameraLensDirection.front;

    final inputImage = convertCameraImageToInputImage(
      image,
      cameraDescription,
      deviceRotation,
    );
    if (inputImage == null) return;

    final meshes = await _faceMeshDetector.processImage(inputImage);
    if (meshes.isEmpty) {
      if (mounted) setState(() => _lipContours = null);
      return;
    }

    // Use the first detected face.
    final mesh = meshes.first;

    // ── Coordinate dimension swap ─────────────────────────────────────────
    // Android camera streams arrive in the sensor's native orientation
    // (typically landscape for front cameras: width > height). ML Kit applies
    // the InputImageRotation we supplied and returns face mesh points in the
    // *rotated* coordinate space.
    //
    // We must compute the actual rotation compensation from the sensor
    // orientation (a fixed hardware property) plus the current UI rotation,
    // NOT just from UI rotation alone — which would always be 0 for a
    // portrait-locked app, making the swap condition never fire.
    final sensorOrientation = cameraDescription.sensorOrientation;
    final int rotationCompensation;
    if (cameraDescription.lensDirection == CameraLensDirection.front) {
      rotationCompensation = (sensorOrientation + deviceRotation) % 360;
    } else {
      rotationCompensation = (sensorOrientation - deviceRotation + 360) % 360;
    }
    final bool swapDims =
        rotationCompensation == 90 || rotationCompensation == 270;
    final int effectiveImageWidth  = swapDims ? image.height : image.width;
    final int effectiveImageHeight = swapDims ? image.width  : image.height;

    final translator = CoordinateTranslator(
      imageWidth: effectiveImageWidth,
      imageHeight: effectiveImageHeight,
      screenWidth: screenSize.width,
      screenHeight: screenSize.height,
      isPainterMirrored: isMirrored,
    );

    final extractor = LipMeshExtractor(
      translateX: translator.translateX,
      translateY: translator.translateY,
    );

    final contours = extractor.extract(mesh);
    if (mounted) setState(() => _lipContours = contours);
  }

  // ── Hex → Color helper ────────────────────────────────────────────────────

  /// Parses a CSS-style hex string (with or without leading '#') into a
  /// Flutter [Color].  Returns a warm terracotta fallback if parsing fails so
  /// the painter is never handed a garbage value.
  Color _hexToColor(String hex) {
    try {
      final sanitised = hex.replaceFirst('#', '');
      final value = int.parse(
        sanitised.length == 6 ? 'FF$sanitised' : sanitised,
        radix: 16,
      );
      return Color(value);
    } catch (_) {
      return const Color(0xFF982A2A); // Deep Autumn fallback
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    // Watch the full AR state from the provider.
    final arState = ref.watch(arTryonProvider);

    // Resolve which shade is currently selected (may be null while loading).
    final ArShadeModel? selectedShade = arState.selectedShadeId != null
        ? arState.allShades.cast<ArShadeModel?>().firstWhere(
              (s) => s?.id == arState.selectedShadeId,
              orElse: () => null,
            )
        : null;

    // Parse the hex colour; fall back gracefully when no shade is selected yet.
    final Color activeColor = selectedShade != null
        ? _hexToColor(selectedShade.colorHex)
        : const Color(0xFF982A2A);

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Base Layer: real camera preview + AR painter
          _buildArCameraLayer(activeColor),

          // 2. Top Layer: Product Banner – driven by provider state
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: ArTopProductBanner(
              selectedShade: selectedShade,
            ),
          ),

          // 3. Bottom Layer: Swatch Panel – driven by provider state
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: const ArSwatchBottomPanel(),
          ),
        ],
      ),
    );
  }


  Widget _buildArCameraLayer(Color activeColor) {
    final controller = _cameraController;
    return GestureDetector(
      onLongPressStart: (_) => setState(() => _isComparing = true),
      onLongPressEnd: (_) => setState(() => _isComparing = false),
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Camera preview (or placeholder while initialising)
          if (controller != null && controller.value.isInitialized)
            ClipRect(
              child: OverflowBox(
                alignment: Alignment.center,
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: SizedBox(
                    width: controller.value.previewSize!.height,
                    height: controller.value.previewSize!.width,
                    child: CameraPreview(controller),
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

          // AR overlay: lipstick painter
          if (!_isComparing)
            CustomPaint(
              painter: LipstickPainter(
                lipContours: _lipContours,
                lipColor: activeColor,
              ),
            ),

          // "HOLD TO COMPARE" pill
          Positioned(
            top: MediaQuery.of(context).padding.top + 80,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
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

// Extension to read device orientation as degrees from DeviceOrientation.
extension _DeviceOrientationExt on DeviceOrientation {
  int get rawValue {
    switch (this) {
      case DeviceOrientation.portraitUp:
        return 0;
      case DeviceOrientation.landscapeRight:
        return 90;
      case DeviceOrientation.portraitDown:
        return 180;
      case DeviceOrientation.landscapeLeft:
        return 270;
    }
  }
}

import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';

class CameraScreen extends StatefulWidget {
  final Map<String, dynamic> quizData;

  const CameraScreen({
    super.key,
    this.quizData = const {},
  });

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  final ImagePicker _picker = ImagePicker();
  CameraController? _controller;
  bool _cameraReady = false;
  FlashMode _flashMode = FlashMode.off;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // Initialize front camera by default
    _initCamera(CameraLensDirection.front);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_controller == null || !_controller!.value.isInitialized) return;
    if (state == AppLifecycleState.inactive) {
      _controller?.dispose();
      _cameraReady = false;
      if (mounted) setState(() {});
    } else if (state == AppLifecycleState.resumed) {
      _initCamera(_controller!.description.lensDirection);
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    super.dispose();
  }

  Future<void> _initCamera(CameraLensDirection direction) async {
    final cameras = await availableCameras();
    if (cameras.isEmpty) return;

    final camera = cameras.firstWhere(
      (c) => c.lensDirection == direction,
      orElse: () => cameras.first,
    );

    final controller = CameraController(
      camera,
      ResolutionPreset.high,
      enableAudio: false,
    );

    final oldController = _controller;
    if (oldController != null) {
      await oldController.dispose();
    }

    await controller.initialize();
    await controller.setFlashMode(_flashMode);

    if (!mounted) return;
    setState(() {
      _controller = controller;
      _cameraReady = true;
    });
  }

  Future<void> _pickGalleryImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null && mounted) {
      context.push(
        '/photo-preview',
        extra: {
          'imagePath': image.path,
          'quizData': widget.quizData,
          'isMirrored': false,
        },
      );
    }
  }

  Future<void> _takePhoto() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    try {
      final XFile image = await _controller!.takePicture();
      final isFront = _controller!.description.lensDirection == CameraLensDirection.front;
      if (!mounted) return;
      context.push(
        '/photo-preview',
        extra: {
          'imagePath': image.path,
          'quizData': widget.quizData,
          'isMirrored': isFront,
        },
      );
    } catch (e) {
      debugPrint('Error taking photo: $e');
    }
  }

  void _switchCamera() async {
    if (_controller == null) return;
    final direction = _controller!.description.lensDirection;
    final newDirection = direction == CameraLensDirection.front
        ? CameraLensDirection.back
        : CameraLensDirection.front;
    
    setState(() => _cameraReady = false);
    await _initCamera(newDirection);
  }

  void _toggleFlash() async {
    if (_controller == null) return;
    final newMode = _flashMode == FlashMode.off ? FlashMode.always : FlashMode.off;
    await _controller!.setFlashMode(newMode);
    setState(() {
      _flashMode = newMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // ── Camera Preview ──
          if (_cameraReady && _controller != null && _controller!.value.isInitialized)
            ClipRect(
              child: OverflowBox(
                alignment: Alignment.center,
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: SizedBox(
                    // Swap width/height: sensor is landscape; display is portrait.
                    width:  _controller!.value.previewSize!.height,
                    height: _controller!.value.previewSize!.width,
                    child:  CameraPreview(_controller!),
                  ),
                ),
              ),
            )
          else
            const Center(child: CircularProgressIndicator(color: GlowTheme.champagneGold)),

          // Center Visual: Dashed Oval
          Positioned.fill(
            child: CustomPaint(
              painter: DashedOvalPainter(color: GlowTheme.champagneGold),
            ),
          ),
          
          // Top Header
          Align(
            alignment: Alignment.topCenter,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      color: Colors.white,
                      onPressed: () => context.pop(),
                    ),
                    IconButton(
                      icon: Icon(_flashMode == FlashMode.always ? Icons.flash_on : Icons.flash_off),
                      color: Colors.white,
                      onPressed: _toggleFlash,
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Bottom Footer Section
          Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 48.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Scan Face',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Center face for scan.',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.normal,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 40.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Left: Gallery
                        IconButton(
                          icon: const Icon(Icons.photo_library_outlined, size: 28),
                          color: Colors.white,
                          onPressed: _pickGalleryImage,
                        ),
                        
                        // Center: Shutter
                        GestureDetector(
                          onTap: _takePhoto,
                          child: Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(color: Colors.white, width: 4),
                            ),
                            child: Center(
                              child: Container(
                                width: 64,
                                height: 64,
                                decoration: const BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: GlowTheme.champagneGold,
                                ),
                              ),
                            ),
                          ),
                        ),
                        
                        // Right: Flip Camera
                        IconButton(
                          icon: const Icon(Icons.flip_camera_ios, size: 28),
                          color: Colors.white,
                          onPressed: _switchCamera,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class DashedOvalPainter extends CustomPainter {
  final Color color;

  DashedOvalPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;
      
    final rect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: size.width * 0.7,
      height: size.height * 0.5,
    );
    
    Path path = Path()..addOval(rect);
    
    Path dashPath = Path();
    const double dashWidth = 10.0;
    const double dashSpace = 8.0;
    
    for (PathMetric pathMetric in path.computeMetrics()) {
      double distance = 0.0;
      while (distance < pathMetric.length) {
        dashPath.addPath(
          pathMetric.extractPath(distance, distance + dashWidth),
          Offset.zero,
        );
        distance += dashWidth + dashSpace;
      }
    }
    
    canvas.drawPath(dashPath, paint);
  }

  @override
  bool shouldRepaint(covariant DashedOvalPainter oldDelegate) {
    return oldDelegate.color != color;
  }
}

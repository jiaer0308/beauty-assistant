import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:camerawesome/camerawesome_plugin.dart';
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

class _CameraScreenState extends State<CameraScreen> {
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickGalleryImage() async {
    // Triggers ImagePicker().pickImage(source: ImageSource.gallery)
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null && mounted) {
      context.push(
        '/photo-preview',
        extra: {
          'imagePath': image.path,
          'quizData': widget.quizData,
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: CameraAwesomeBuilder.custom(
        saveConfig: SaveConfig.photo(),
        onMediaCaptureEvent: (MediaCapture mediaCapture) {
          if (mediaCapture.status == MediaCaptureStatus.success && mediaCapture.isPicture) {
            context.push(
              '/photo-preview',
              extra: {
                'imagePath': mediaCapture.captureRequest.path,
                'quizData': widget.quizData,
              },
            );
          }
        },
        builder: (CameraState cameraState, AnalysisPreview preview) {
          return Stack(
            children: [
              // Center Visual: Dashed Oval
              Positioned.fill(
                child: CustomPaint(
                  painter: DashedOvalPainter(color: GlowTheme.champagneGold),
                ),
              ),
              
              // Top Header
              SafeArea(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.arrow_back),
                        color: GlowTheme.deepTaupe,
                        onPressed: () => context.pop(),
                      ),
                      StreamBuilder<FlashMode>(
                        stream: cameraState.sensorConfig.flashMode$,
                        builder: (context, snapshot) {
                          final flashMode = snapshot.data ?? FlashMode.none;
                          bool isFlashOn = flashMode == FlashMode.always || flashMode == FlashMode.on;
                          return IconButton(
                            icon: Icon(isFlashOn ? Icons.flash_on : Icons.flash_off),
                            color: GlowTheme.deepTaupe,
                            onPressed: () {
                              cameraState.sensorConfig.setFlashMode(
                                isFlashOn ? FlashMode.none : FlashMode.always,
                              );
                            },
                          );
                        },
                      ),
                    ],
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
                          color: GlowTheme.deepTaupe,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Center face for scan.',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.normal,
                          color: GlowTheme.deepTaupe,
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
                              color: GlowTheme.oatmeal,
                              onPressed: _pickGalleryImage,
                            ),
                            
                            // Center: Shutter
                            GestureDetector(
                              onTap: () {
                                cameraState.when(
                                  onPhotoMode: (photoState) => photoState.takePhoto(),
                                );
                              },
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
                              color: GlowTheme.oatmeal,
                              onPressed: () {
                                cameraState.switchCameraSensor();
                              },
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
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

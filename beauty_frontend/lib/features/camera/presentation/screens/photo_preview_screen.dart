import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';

class PhotoPreviewScreen extends StatelessWidget {
  final String? imagePath;
  final Map<String, dynamic>? quizData;

  const PhotoPreviewScreen({
    super.key,
    this.imagePath,
    this.quizData,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Background (The Captured Image)
          _buildBackgroundImage(),

          // 2. Top Header (Minimalist)
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: Row(
                  children: [
                    Container(
                      decoration: const BoxDecoration(
                        color: Color(0x4D000000), // Colors.black with 30% opacity
                        shape: BoxShape.circle,
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.arrow_back),
                        color: Colors.white,
                        onPressed: () => context.pop(),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 3. Bottom Action Panel (The Decision Area)
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.only(top: 32.0, left: 24.0, right: 24.0, bottom: 48.0),
              decoration: const BoxDecoration(
                color: GlowTheme.pearlWhite,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(24.0),
                  topRight: Radius.circular(24.0),
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Perfecting your profile',
                    style: TextStyle(
                      color: GlowTheme.deepTaupe,
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Row(
                    children: [
                      // Button 1 (Secondary - Retake)
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => context.pop(),
                          style: OutlinedButton.styleFrom(
                            backgroundColor: Colors.white,
                            side: const BorderSide(color: GlowTheme.oatmeal, width: 1),
                            elevation: 0,
                            shape: const StadiumBorder(),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: const Text(
                            'Retake',
                            style: TextStyle(
                              color: GlowTheme.deepTaupe,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      // Button 2 (Primary - Confirm/Analyze)
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            // TODO: Send data to backend (Page 12)
                            // For now, print to console to verify
                            debugPrint('Quiz Data: $quizData');
                            debugPrint('Image Path: $imagePath');
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GlowTheme.champagneGold,
                            foregroundColor: GlowTheme.deepTaupe,
                            elevation: 0,
                            shape: const StadiumBorder(),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: const Text(
                            'Use Photo',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBackgroundImage() {
    if (imagePath != null && imagePath!.isNotEmpty) {
      return Image.file(
        File(imagePath!),
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
      );
    } else {
      return _buildPlaceholder();
    }
  }

  Widget _buildPlaceholder() {
    // High-quality placeholder image of a face for UI building purposes
    return Image.network(
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1000&auto=format&fit=crop',
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: GlowTheme.oatmeal,
          child: const Center(
            child: Icon(Icons.face, size: 100, color: GlowTheme.deepTaupe),
          ),
        );
      },
    );
  }
}

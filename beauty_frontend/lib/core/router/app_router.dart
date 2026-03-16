import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/onboarding/presentation/screens/onboarding_quiz_screen.dart';
import '../../features/camera/presentation/screens/camera.dart';
import '../../features/camera/presentation/screens/photo_preview_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/onboarding',
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingQuizScreen(),
      ),
      GoRoute(
        path: '/camera',
        builder: (context, state) {
          final quizData = state.extra as Map<String, dynamic>? ?? const {};
          return CameraScreen(quizData: quizData);
        },
      ),
      GoRoute(
        path: '/photo-preview',
        builder: (context, state) {
          final extras = state.extra as Map<String, dynamic>? ?? {};
          final imagePath = extras['imagePath'] as String?;
          final quizData = extras['quizData'] as Map<String, dynamic>?;
          return PhotoPreviewScreen(imagePath: imagePath, quizData: quizData);
        },
      ),
    ],
  );
});

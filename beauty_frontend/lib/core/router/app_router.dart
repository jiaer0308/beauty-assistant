import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/onboarding/presentation/screens/onboarding_quiz_screen.dart';
import '../../features/onboarding/presentation/screens/welcome_screen.dart';
import '../../features/camera/presentation/screens/camera.dart';
import '../../features/camera/presentation/screens/photo_preview_screen.dart';
import '../../features/camera/presentation/screens/result_screen.dart';
import '../../features/camera/presentation/screens/result_dashboard_screen.dart';
import '../../features/camera/data/models/color_analysis_response.dart';

import '../../features/history/presentation/screens/history_screen.dart';
import '../../features/camera/presentation/screens/ar_tryon_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/home/presentation/screens/atelier_home_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/welcome',
        builder: (context, state) => const WelcomeScreen(),
      ),
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
      GoRoute(
        path: '/result',
        builder: (context, state) {
          final data = state.extra as Map<String, dynamic>?;
          return ResultScreen(data: data);
        },
      ),
      GoRoute(
        path: '/result-dashboard',
        builder: (context, state) {
          final analysisData = state.extra as ColorAnalysisResponse?;
          return ResultDashboardScreen(analysisData: analysisData);
        },
      ),
      GoRoute(
        path: '/dashboard',
        builder: (context, state) => const AtelierHomeScreen(),
      ),
      GoRoute(
        path: '/history',
        builder: (context, state) => const HistoryScreen(),
      ),
      GoRoute(
        path: '/ar-tryon',
        builder: (context, state) {
          final extra = state.extra;

          if (extra is Map<String, dynamic> || extra is Map) {
            final map = extra as Map;
            
            // ── SCA Entry: extra = {'sessionId': int}
            if (map.containsKey('sessionId')) {
              return ArTryonScreen(sessionId: map['sessionId'] as int);
            }
            
            // ── Dashboard Entry: extra = {'dashboardProducts': List<ProductRecommendation>, 'selectedId': int}
            if (map.containsKey('dashboardProducts')) {
              final productsRaw = map['dashboardProducts'];
              final selectedId = map['selectedId'] as int?;
              
              if (productsRaw is List) {
                // Safely cast the list elements to the expected type
                final products = productsRaw.cast<ProductRecommendation>();
                
                return ArTryonScreen(
                  dashboardProducts: products,
                  selectedDashboardId: selectedId,
                );
              }
            }
          }

          // ── Standalone / direct navigation (no extra)
          return const ArTryonScreen();
        },
      ),
    ],
  );
});

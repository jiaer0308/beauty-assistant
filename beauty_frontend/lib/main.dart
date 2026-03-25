import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'core/theme/glow_theme.dart';
import 'core/router/app_router.dart';
import 'features/auth/presentation/providers/auth_provider.dart';
import 'features/auth/models/auth_state.dart';

void main() {
  runApp(
    const ProviderScope(
      child: BeautyAssistantApp(),
    ),
  );
}

class BeautyAssistantApp extends HookConsumerWidget {
  const BeautyAssistantApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    // Initialize Auth state on startup
    useEffect(() {
      Future.microtask(() async {
        final authNotifier = ref.read(authProvider.notifier);
        await authNotifier.init();
        
        // If not authenticated and no guest token, create a guest session automatically
        final authState = ref.read(authProvider);
        if (authState.status == AuthStatus.unauthenticated) {
          await authNotifier.loginAsGuest();
        }
      });
      return null;
    }, []);

    return MaterialApp.router(
      title: 'Glow Beauty Assistant',
      theme: GlowTheme.lightTheme,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}

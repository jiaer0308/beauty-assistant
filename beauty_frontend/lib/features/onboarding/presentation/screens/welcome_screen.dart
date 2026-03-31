import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../auth/presentation/widgets/auth_bottom_sheet.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Background Aesthetic
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: GlowTheme.champagneGold.withValues(alpha: 0.1),
              ),
            ),
          ),
          Positioned(
            bottom: -50,
            left: -50,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: GlowTheme.oatmeal.withValues(alpha: 0.2),
              ),
            ),
          ),
          
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 60),
                  Text(
                    'GLOW',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.playfairDisplay(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 8.0,
                      color: GlowTheme.deepTaupe,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Discover your perfect\ncolors in seconds.',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      height: 1.3,
                      color: GlowTheme.deepTaupe.withValues(alpha: 0.8),
                    ),
                  ),
                  const Spacer(),
                  // Hero Image or Illustration could go here
                  Expanded(
                    flex: 3,
                    child: Center(
                      child: Container(
                        padding: const EdgeInsets.all(32),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.transparent,
                          boxShadow: [
                            BoxShadow(
                              color: GlowTheme.deepTaupe.withValues(alpha: 0.05),
                              blurRadius: 30,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    'Get started by snapping a quick selfie for your personalized color analysis.',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 14,
                      color: GlowTheme.deepTaupe.withValues(alpha: 0.6),
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: () {
                      context.push('/onboarding');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: GlowTheme.champagneGold,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: const StadiumBorder(),
                      padding: const EdgeInsets.symmetric(vertical: 20),
                    ),
                    child: Text(
                      'START CAMERA ANALYSIS',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () {
                      AuthBottomSheet.show(
                        context,
                        discoveredSeason: 'Account', // Just a placeholder
                        onSuccess: () {
                          // After login from welcome screen, go to dashboard
                          context.go('/dashboard');
                        },
                      );
                    },
                    style: TextButton.styleFrom(
                      foregroundColor: GlowTheme.deepTaupe,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: Text(
                      'ALREADY HAVE AN ACCOUNT? LOG IN',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1.0,
                      ),
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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../widgets/quiz_progress_bar.dart';
import '../widgets/quiz_step_layout.dart';
import '../onboarding_controller.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/models/auth_state.dart';

class OnboardingQuizScreen extends ConsumerStatefulWidget {
  const OnboardingQuizScreen({super.key});

  @override
  ConsumerState<OnboardingQuizScreen> createState() => _OnboardingQuizScreenState();
}

class _OnboardingQuizScreenState extends ConsumerState<OnboardingQuizScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authState = ref.read(authProvider);
      // Only skip if the user is fully authenticated with a real JWT.
      // For guest or unauthenticated, always create a fresh guest session.
      // This prevents 401 errors caused by stale guest tokens in storage.
      if (authState.status != AuthStatus.authenticated) {
        ref.read(authProvider.notifier).loginAsGuest();
      }
    });
  }


  @override
  Widget build(BuildContext context) {
    final state = ref.watch(onboardingControllerProvider);
    final controller = ref.read(onboardingControllerProvider.notifier);
    final pageController = PageController(initialPage: state.currentPage);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          color: GlowTheme.deepTaupe,
          onPressed: () {
            if (state.currentPage > 0) {
              controller.previousPage();
              pageController.previousPage(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
              );
            } else {
              if (context.canPop()) {
                context.pop();
              } else {
                context.go('/dashboard');
              }
            }
          },
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(40),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 24),
            child: QuizProgressBar(
              currentStep: state.currentPage + 1,
              totalSteps: 9,
            ),
          ),
        ),
      ),
      body: PageView(
        controller: pageController,
        physics: const NeverScrollableScrollPhysics(),
        children: [
          QuizStepLayout(
            title: 'How would you describe your natural skin type?',
            subtitle: "Select the option that best describes your skin's daily behavior.",
            options: [
              QuizOption(title: 'Oily', description: 'Shiny appearance, visible pores'),
              QuizOption(title: 'Dry', description: 'Feels tight, occasional flaking'),
              QuizOption(title: 'Combination', description: 'Oily T-zone, dry or normal cheeks'),
              QuizOption(title: 'Sensitive', description: 'Prone to redness and irritation'),
            ],
            selectedOption: state.answers['skin_type'],
            onOptionSelected: (value) => controller.updateAnswer('skin_type', value),
          ),
          QuizStepLayout(
            title: 'How does your skin react to the sun?',
            subtitle: 'Think about your natural skin without sunscreen.',
            options: [
              QuizOption(title: 'Burn easily, rarely tan', description: ''),
              QuizOption(title: 'Burn first, then tan', description: ''),
              QuizOption(title: 'Tan easily, rarely burn', description: ''),
            ],
            selectedOption: state.answers['sun_reaction'],
            onOptionSelected: (value) => controller.updateAnswer('sun_reaction', value),
          ),
          QuizStepLayout(
            title: 'What color are your wrist veins?',
            subtitle: 'Check the inside of your wrist in natural daylight.',
            options: [
              QuizOption(title: 'Blue or Purple', description: ''),
              QuizOption(title: 'Green or Olive', description: ''),
              QuizOption(title: 'Mixed / Unsure', description: ''),
            ],
            selectedOption: state.answers['wrist_vein'],
            onOptionSelected: (value) => controller.updateAnswer('wrist_vein', value),
          ),
          QuizStepLayout(
            title: 'What is your natural hair color?',
            subtitle: 'Select the shade closest to your un-dyed roots.',
            options: [
              QuizOption(title: 'Black', description: ''),
              QuizOption(title: 'Warm Brown', description: ''),
              QuizOption(title: 'Ashy Blonde', description: ''),
              QuizOption(title: 'Golden Blonde', description: ''),
            ],
            selectedOption: state.answers['hair_color'],
            onOptionSelected: (value) => controller.updateAnswer('hair_color', value),
          ),
          QuizStepLayout(
            title: 'Which jewelry metal makes your skin glow?',
            subtitle: '',
            options: [
              QuizOption(title: 'Silver / White Gold', description: ''),
              QuizOption(title: 'Yellow Gold', description: ''),
              QuizOption(title: 'Rose Gold', description: ''),
            ],
            selectedOption: state.answers['jewelry'],
            onOptionSelected: (value) => controller.updateAnswer('jewelry', value),
          ),
          QuizStepLayout(
            title: 'What is your preferred foundation coverage?',
            subtitle: '',
            options: [
              QuizOption(title: 'Sheer / Light', description: 'A natural, breathable finish'),
              QuizOption(title: 'Medium', description: 'Even skin tone with builds'),
              QuizOption(title: 'Full', description: 'Complete flawless coverage'),
            ],
            selectedOption: state.answers['foundation_coverage'],
            onOptionSelected: (value) => controller.updateAnswer('foundation_coverage', value),
          ),
          QuizStepLayout(
            title: 'What makeup finish do you love the most?',
            subtitle: '',
            options: [
              QuizOption(title: 'Matte / Velvet', description: 'A shine-free, velvety smooth finish for all-day wear.'),
              QuizOption(title: 'Dewy / Glowy', description: 'Luminous, hydrated skin with a fresh-from-the-spa radiance.'),
              QuizOption(title: 'Satin / Natural', description: 'The best of both worlds—looks just like real, healthy skin.'),
            ],
            selectedOption: state.answers['makeup_finish'],
            onOptionSelected: (value) => controller.updateAnswer('makeup_finish', value),
          ),
          QuizStepLayout(
            title: 'What are your primary skin concerns?',
            subtitle: 'Choose your main focus.',
            isChipMode: true,
            options: [
              QuizOption(title: 'Dark Circles', description: ''),
              QuizOption(title: 'Redness/Acne', description: ''),
              QuizOption(title: 'Dullness', description: ''),
              QuizOption(title: 'Large Pores', description: ''),
              QuizOption(title: 'Fine Lines', description: ''),
              QuizOption(title: 'Pigmentation', description: ''),
              QuizOption(title: 'Dryness', description: ''),
              QuizOption(title: 'Oiliness', description: ''),
            ],
            selectedOptions: (state.answers['skin_concerns'] as List<String>?) ?? [],
            onOptionSelected: (value) => controller.updateAnswer('skin_concerns', value),
          ),
          QuizStepLayout(
            title: 'What is your go-to everyday lip style?',
            subtitle: 'Select your signature look.',
            options: [
              QuizOption(title: 'MLBB (Nudes/Balms)', description: ''),
              QuizOption(title: 'Bold & Statement', description: ''),
              QuizOption(title: 'Fresh & Feminine', description: ''),
            ],
            selectedOption: state.answers['lip_style'],
            onOptionSelected: (value) => controller.updateAnswer('lip_style', value),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(left: 24.0, right: 24.0, bottom: 24.0, top: 12.0),
          child: ElevatedButton(
            onPressed: () {
              final stepKeys = [
                'skin_type',
                'sun_reaction',
                'wrist_vein',
                'hair_color',
                'jewelry',
                'foundation_coverage',
                'makeup_finish',
                'skin_concerns',
                'lip_style',
              ];
              
              final currentKey = stepKeys[state.currentPage];
              final answer = state.answers[currentKey];
              final hasAnswer = answer != null &&
                  ((answer is String && answer.isNotEmpty) ||
                   (answer is List && answer.isNotEmpty));
              
              if (!hasAnswer) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Please select an option to continue.'),
                    backgroundColor: GlowTheme.deepTaupe,
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                return;
              }

              if (state.currentPage < 8) {
                controller.nextPage();
                pageController.nextPage(
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeInOut,
                );
              } else {
                context.push('/camera', extra: state.answers);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: GlowTheme.champagneGold,
              foregroundColor: GlowTheme.deepTaupe,
              elevation: 0,
              shape: const StadiumBorder(),
              minimumSize: const Size(double.infinity, 56),
            ),
            child: const Text('Next'),
          ),
        ),
      ),
    );
  }
}

class QuizOption {
  final String title;
  final String description;

  QuizOption({
    required this.title,
    required this.description,
  });
}

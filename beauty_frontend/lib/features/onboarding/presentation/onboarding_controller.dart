import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/onboarding_state.dart';

final onboardingControllerProvider =
    StateNotifierProvider<OnboardingController, OnboardingState>((ref) {
  return OnboardingController();
});

class OnboardingController extends StateNotifier<OnboardingState> {
  OnboardingController() : super(const OnboardingState());

  void updateAnswer(String key, dynamic value) {
    final updatedAnswers = Map<String, dynamic>.from(state.answers);
    updatedAnswers[key] = value;
    state = state.copyWith(answers: updatedAnswers);
  }

  void nextPage() {
    state = state.copyWith(currentPage: state.currentPage + 1);
  }

  void previousPage() {
    if (state.currentPage > 0) {
      state = state.copyWith(currentPage: state.currentPage - 1);
    }
  }
}

class OnboardingState {
  final int currentPage;
  final Map<String, dynamic> answers;
  final bool isSubmitting;

  const OnboardingState({
    this.currentPage = 0,
    this.answers = const {},
    this.isSubmitting = false,
  });

  OnboardingState copyWith({
    int? currentPage,
    Map<String, dynamic>? answers,
    bool? isSubmitting,
  }) {
    return OnboardingState(
      currentPage: currentPage ?? this.currentPage,
      answers: answers ?? this.answers,
      isSubmitting: isSubmitting ?? this.isSubmitting,
    );
  }
}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/color_analysis_response.dart';

/// Provider to store the current color analysis result
final currentAnalysisProvider = StateProvider<ColorAnalysisResponse?>((ref) => null);

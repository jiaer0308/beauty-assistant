class ColorAnalysisResponse {
  final bool success;
  final AnalysisResult? result;
  final Map<String, dynamic>? metrics;
  final List<ColorInfo> bestColors;
  final List<ColorInfo> neutralColors;
  final List<ColorInfo> avoidColors;
  final List<ProductRecommendation> recommendedProducts;

  ColorAnalysisResponse({
    required this.success,
    this.result,
    this.metrics,
    this.bestColors = const [],
    this.neutralColors = const [],
    this.avoidColors = const [],
    this.recommendedProducts = const [],
  });

  factory ColorAnalysisResponse.fromJson(Map<String, dynamic> json) {
    final recommendations = json['recommendations'] as Map<String, dynamic>? ?? {};
    final colorPalette = recommendations['color_palette'] as Map<String, dynamic>? ?? {};
    final cosmetics = recommendations['cosmetics'] as List<dynamic>? ?? [];

    return ColorAnalysisResponse(
      success: json['success'] ?? false,
      result: json['result'] != null ? AnalysisResult.fromJson(json['result']) : null,
      metrics: json['metrics'] as Map<String, dynamic>?,
      bestColors: (colorPalette['best'] as List<dynamic>?)
              ?.map((e) => ColorInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      neutralColors: (colorPalette['neutral'] as List<dynamic>?)
              ?.map((e) => ColorInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      avoidColors: (colorPalette['avoid'] as List<dynamic>?)
              ?.map((e) => ColorInfo.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      recommendedProducts: cosmetics
              .map((e) => ProductRecommendation.fromJson(e as Map<String, dynamic>))
              .toList(),
    );
  }
}

class AnalysisResult {
  final String displayName;
  final String season;
  final double confidence;

  AnalysisResult({
    required this.displayName,
    required this.season,
    required this.confidence,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      displayName: json['display_name'] ?? '',
      season: json['season'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
    );
  }
}

class ColorInfo {
  final String name;
  final String hex;

  ColorInfo({
    required this.name,
    required this.hex,
  });

  factory ColorInfo.fromJson(Map<String, dynamic> json) {
    return ColorInfo(
      name: json['name'] ?? '',
      hex: json['hex'] ?? '',
    );
  }
}

class ProductRecommendation {
  final String brand;
  final String name;
  final String shade;
  final int matchPercentage;
  final String imageUrl;

  ProductRecommendation({
    required this.brand,
    required this.name,
    required this.shade,
    required this.matchPercentage,
    required this.imageUrl,
  });

  factory ProductRecommendation.fromJson(Map<String, dynamic> json) {
    return ProductRecommendation(
      brand: json['brand'] ?? '',
      name: json['name'] ?? '',
      shade: json['shade'] ?? '',
      matchPercentage: json['matchPercentage'] ?? 0,
      imageUrl: json['image_url'] ?? '',
    );
  }
}

/// Typed data models for the History feature.
///
/// Replaces raw `Map<String, dynamic>` access for type-safety and IDE support.
library;

import 'package:beauty_assistant/features/camera/data/models/color_analysis_response.dart';

// ---------------------------------------------------------------------------
// HistorySession — used in the list view
// ---------------------------------------------------------------------------

class HistorySession {
  final int id;
  final String analysisType;
  final int? seasonId;

  /// Raw snake_case name from the backend (e.g. "warm_autumn").
  /// Use [seasonDisplayName] for the UI-ready title-cased version.
  final String? seasonName;
  final int itemCount;
  final String? imagePath;
  final DateTime createdAt;

  const HistorySession({
    required this.id,
    required this.analysisType,
    this.seasonId,
    this.seasonName,
    required this.itemCount,
    this.imagePath,
    required this.createdAt,
  });

  /// Returns the title-cased season name for display, e.g. "Warm Autumn".
  /// Falls back to "Unknown Season" when [seasonName] is null or empty.
  String get seasonDisplayName {
    final raw = seasonName;
    if (raw == null || raw.isEmpty) return 'Unknown Season';
    return raw
        .split('_')
        .map((w) => w.isNotEmpty
            ? '${w[0].toUpperCase()}${w.substring(1).toLowerCase()}'
            : '')
        .join(' ');
  }

  factory HistorySession.fromJson(Map<String, dynamic> json) {
    return HistorySession(
      id: json['id'] as int,
      analysisType: (json['analysis_type'] as String?) ?? 'sca_scan',
      seasonId: json['season_id'] as int?,
      seasonName: json['season_name'] as String?,
      itemCount: (json['item_count'] as int?) ?? 0,
      imagePath: json['image_path'] as String?,
      createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ??
          DateTime.now(),
    );
  }
}

// ---------------------------------------------------------------------------
// HistorySessionProduct — enriched product within a session's detail
// ---------------------------------------------------------------------------

class HistorySessionProduct {
  final int id;
  final String productName;
  final String shadeName;
  final String? brandName;
  final int? categoryId;
  final String? hexCode;
  final String? imageUrl;

  const HistorySessionProduct({
    required this.id,
    required this.productName,
    required this.shadeName,
    this.brandName,
    this.categoryId,
    this.hexCode,
    this.imageUrl,
  });

  factory HistorySessionProduct.fromJson(Map<String, dynamic> json) {
    return HistorySessionProduct(
      id: json['id'] as int,
      productName: (json['product_name'] as String?) ?? '',
      shadeName: (json['shade_name'] as String?) ?? '',
      brandName: json['brand_name'] as String?,
      categoryId: json['category_id'] as int?,
      hexCode: json['hex_code'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }

  /// Converts to the shared [ProductRecommendation] model used by
  /// [ProductMatchCard] and [ArTryonScreen].
  ProductRecommendation toProductRecommendation() {
    return ProductRecommendation(
      id: id,
      brand: brandName ?? '',
      name: productName,
      shade: shadeName,
      matchPercentage: 0,
      imageUrl: imageUrl ?? '',
      categoryId: categoryId,
      hexCode: hexCode,
    );
  }
}

// ---------------------------------------------------------------------------
// HistorySessionDetail — used in the detail view
// ---------------------------------------------------------------------------

class HistorySessionDetail extends HistorySession {
  final List<HistorySessionProduct> items;

  const HistorySessionDetail({
    required super.id,
    required super.analysisType,
    super.seasonId,
    super.seasonName,
    required super.itemCount,
    super.imagePath,
    required super.createdAt,
    required this.items,
  });

  factory HistorySessionDetail.fromJson(Map<String, dynamic> json) {
    final base = HistorySession.fromJson(json);
    final rawItems = json['items'] as List<dynamic>? ?? [];
    return HistorySessionDetail(
      id: base.id,
      analysisType: base.analysisType,
      seasonId: base.seasonId,
      seasonName: base.seasonName,
      itemCount: base.itemCount,
      imagePath: base.imagePath,
      createdAt: base.createdAt,
      items: rawItems
          .map((e) => HistorySessionProduct.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  /// Returns items converted to [ProductRecommendation] for use in
  /// [ProductMatchCard] and [ArTryonScreen].
  List<ProductRecommendation> get asProductRecommendations =>
      items.map((p) => p.toProductRecommendation()).toList();
}

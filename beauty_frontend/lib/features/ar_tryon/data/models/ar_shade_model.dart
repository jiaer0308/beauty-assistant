/// Data model representing a single cosmetic shade for the AR Try-On feature.
///
/// Each shade belongs to a brand/product and carries its display color
/// plus a flag indicating whether it's a "best color" match for the
/// user's seasonal color analysis.
class ArShadeModel {
  final String id;
  final String brandName;
  final String productName;
  final String shadeName;

  /// Hex color string including the '#' prefix, e.g. '#B5453A'.
  final String colorHex;

  /// The specific Database ID of this cosmetic shade for favorites.
  final int? cosmeticId;

  /// The ID of the parent product this shade belongs to.
  final int? productId;

  /// Whether this shade was identified as a "best color" for the user's
  /// seasonal palette (e.g. Deep Autumn).
  final bool isBestColor;

  const ArShadeModel({
    required this.id,
    required this.brandName,
    required this.productName,
    required this.shadeName,
    required this.colorHex,
    this.productId,
    this.cosmeticId,
    this.isBestColor = false,
  });

  ArShadeModel copyWith({
    String? id,
    String? brandName,
    String? productName,
    String? shadeName,
    String? colorHex,
    int? productId,
    int? cosmeticId,
    bool? isBestColor,
  }) {
    return ArShadeModel(
      id: id ?? this.id,
      brandName: brandName ?? this.brandName,
      productName: productName ?? this.productName,
      shadeName: shadeName ?? this.shadeName,
      colorHex: colorHex ?? this.colorHex,
      productId: productId ?? this.productId,
      cosmeticId: cosmeticId ?? this.cosmeticId,
      isBestColor: isBestColor ?? this.isBestColor,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ArShadeModel &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'ArShadeModel(id: $id, shade: $shadeName, color: $colorHex, best: $isBestColor)';
}

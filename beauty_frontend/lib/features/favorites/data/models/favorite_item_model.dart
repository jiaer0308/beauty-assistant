import '../../../camera/data/models/color_analysis_response.dart';

class FavoriteItemModel {
  final int id;
  final String productName;
  final String shadeName;
  final String? brandName;
  final int? categoryId;
  final String? hexCode;
  final String? imageUrl;
  final DateTime? favoritedAt;

  FavoriteItemModel({
    required this.id,
    required this.productName,
    required this.shadeName,
    this.brandName,
    this.categoryId,
    this.hexCode,
    this.imageUrl,
    this.favoritedAt,
  });

  factory FavoriteItemModel.fromJson(Map<String, dynamic> json) {
    return FavoriteItemModel(
      id: json['id'] as int,
      productName: json['product_name'] as String,
      shadeName: json['shade_name'] as String,
      brandName: json['brand_name'] as String?,
      categoryId: json['category_id'] as int?,
      hexCode: json['hex_code'] as String?,
      imageUrl: json['image_url'] as String?,
      favoritedAt: json['favorited_at'] != null
          ? DateTime.parse(json['favorited_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_name': productName,
      'shade_name': shadeName,
      'brand_name': brandName,
      'category_id': categoryId,
      'hex_code': hexCode,
      'image_url': imageUrl,
      'favorited_at': favoritedAt?.toIso8601String(),
    };
  }

  ProductRecommendation toProductRecommendation() {
    return ProductRecommendation(
      id: id,
      brand: brandName ?? 'Unknown Brand',
      name: productName,
      shade: shadeName,
      matchPercentage: 100, // Or 0, doesn't matter for favorites
      imageUrl: imageUrl ?? '',
      categoryId: categoryId,
      hexCode: hexCode,
    );
  }
}

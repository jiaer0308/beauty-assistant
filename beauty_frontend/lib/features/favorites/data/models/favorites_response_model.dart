import 'favorite_item_model.dart';

class FavoritesResponseModel {
  final int total;
  final int page;
  final int size;
  final bool hasNext;
  final List<FavoriteItemModel> items;

  FavoritesResponseModel({
    required this.total,
    required this.page,
    required this.size,
    required this.hasNext,
    required this.items,
  });

  factory FavoritesResponseModel.fromJson(Map<String, dynamic> json) {
    return FavoritesResponseModel(
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      size: json['size'] as int? ?? 20,
      hasNext: json['has_next'] as bool? ?? false,
      items: (json['items'] as List<dynamic>?)
              ?.map((e) => FavoriteItemModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total': total,
      'page': page,
      'size': size,
      'has_next': hasNext,
      'items': items.map((e) => e.toJson()).toList(),
    };
  }
}

import 'dart:ui' show Offset;
import 'package:google_mlkit_face_mesh_detection/google_mlkit_face_mesh_detection.dart';

/// Indices for the outer (lip silhouette) and inner (mouth opening) contours
/// from ML Kit's 468-point face mesh.
///
/// Reference:
/// https://storage.googleapis.com/mediapipe-assets/documentation/mediapipe_face_landmark_fullsize.png
class LipIndices {
  LipIndices._();

  // ---- Outer lip (upper lip crest + lower lip base) ----
  /// Clockwise outer boundary of lips.
  static const List<int> outerLip = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
    291, 375, 321, 405, 314, 17, 84, 181, 91, 146,
    61, // close the path
  ];

  // ---- Inner lip / mouth opening contour ----
  /// Inner boundary (opening) – subtract this to clip through open mouth.
  static const List<int> innerLip = [
    78, 191, 80, 81, 82, 13, 312, 311, 310, 415,
    308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
    78, // close the path
  ];
}

/// Extracts resolved [Offset] paths for the outer and inner lip contours
/// from a detected [FaceMesh].
///
/// The [FaceMesh.points] list is indexed 0-467 and each [FaceMeshPoint]
/// exposes its pixel position via [FaceMeshPoint.x] and [FaceMeshPoint.y].
class LipMeshExtractor {
  const LipMeshExtractor({
    required this.translateX,
    required this.translateY,
  });

  /// Function that maps image-space X to canvas X.
  final double Function(double x) translateX;

  /// Function that maps image-space Y to canvas Y.
  final double Function(double y) translateY;

  /// Extracts lip paths from [mesh] and returns them as lists of canvas [Offset]s.
  /// Returns [LipContours] or `null` if the mesh is unusable.
  LipContours? extract(FaceMesh mesh) {
    final points = mesh.points; // List<FaceMeshPoint>, length 468
    if (points.length < 468) return null;

    final outer = _extractPath(points, LipIndices.outerLip);
    final inner = _extractPath(points, LipIndices.innerLip);

    if (outer == null || inner == null) return null;
    return LipContours(outer: outer, inner: inner);
  }

  List<Offset>? _extractPath(
      List<FaceMeshPoint> points, List<int> indices) {
    final path = <Offset>[];
    for (final idx in indices) {
      if (idx >= points.length) return null;
      final point = points[idx];
      // FaceMeshPoint exposes x and y as pixel positions in the input image.
      path.add(Offset(translateX(point.x.toDouble()), translateY(point.y.toDouble())));
    }
    return path;
  }
}

/// Holds the resolved canvas offsets for outer and inner lip contours.
class LipContours {
  const LipContours({required this.outer, required this.inner});

  /// Outer silhouette of the lips (fill this with colour).
  final List<Offset> outer;

  /// Inner mouth-opening boundary (subtract to punch through the overlay).
  final List<Offset> inner;
}

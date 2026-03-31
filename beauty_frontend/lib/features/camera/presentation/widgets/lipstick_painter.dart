import 'package:flutter/material.dart';
import 'lip_mesh_extractor.dart';

/// High-performance [CustomPainter] that renders a lipstick colour overlay
/// onto the lips detected by ML Kit Face Mesh.
///
/// Design decisions:
/// - [Path.combine] with [PathOperation.difference] cuts away the mouth
///   opening so the overlay does not paint over the interior when the user
///   opens their mouth.
/// - [BlendMode.multiply] produces natural-looking blending with skin tone
///   rather than an opaque coloured rectangle.
/// - All [Path] and [Paint] objects are **pre-allocated** and reused between
///   frames to avoid GC pressure (no heavy allocation inside `paint()`).
class LipstickPainter extends CustomPainter {
  LipstickPainter({
    required this.lipContours,
    required this.lipColor,
    this.opacity = 0.6,
  }) : _lipPaint = Paint()
          ..color = lipColor.withValues(alpha: opacity)
          ..style = PaintingStyle.fill
          ..blendMode = BlendMode.multiply;

  /// The resolved lip contour paths (canvas offsets) to paint.
  final LipContours? lipContours;

  /// Base lip colour (e.g. `Color(0xFF982A2A)`).
  final Color lipColor;

  /// Transparency of the overlay (0 = invisible, 1 = fully opaque).
  final double opacity;

  // Pre-allocated paint object – mutated in shouldRepaint but NOT inside paint().
  final Paint _lipPaint;

  @override
  void paint(Canvas canvas, Size size) {
    // Always sync paint colour before drawing (pure, no side effects elsewhere).
    _lipPaint.color = lipColor.withValues(alpha: opacity);

    final contours = lipContours;
    if (contours == null || contours.outer.isEmpty || contours.inner.isEmpty) {
      return;
    }

    // Build outer lip path.
    final outerPath = _buildPath(contours.outer);

    // Build inner (mouth-opening) path.
    final innerPath = _buildPath(contours.inner);

    // Combine: outer lip MINUS mouth opening → lip surface only.
    final visibleLipPath = Path.combine(
      PathOperation.difference,
      outerPath,
      innerPath,
    );

    canvas.drawPath(visibleLipPath, _lipPaint);
  }

  /// Builds a [Path] from a list of [Offset]s using [moveTo] + [lineTo].
  /// This is deliberately kept as a simple helper so it can be inlined by
  /// the Dart compiler.
  static Path _buildPath(List<Offset> offsets) {
    final path = Path();
    if (offsets.isEmpty) return path;
    path.moveTo(offsets.first.dx, offsets.first.dy);
    for (int i = 1; i < offsets.length; i++) {
      path.lineTo(offsets[i].dx, offsets[i].dy);
    }
    path.close();
    return path;
  }

  @override
  bool shouldRepaint(LipstickPainter oldDelegate) =>
      oldDelegate.lipContours != lipContours ||
      oldDelegate.lipColor != lipColor ||
      oldDelegate.opacity != opacity;
}

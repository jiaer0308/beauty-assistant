import 'package:flutter/material.dart';
import 'lip_mesh_extractor.dart';

// ── LipstickController ─────────────────────────────────────────────────────────

/// Holds all mutable state needed to render the lipstick overlay.
///
/// Extends [ChangeNotifier] so it acts as the [CustomPainter.repaint]
/// listenable. When [updateContours] or [updateColor] is called, Flutter
/// schedules **only** a raster-thread repaint of the [LipstickPainter] without
/// triggering a widget-tree rebuild (`setState`).
///
/// Effect on performance:
/// - Old path: ML Kit result → `setState` → entire `_ArTryonScreenState`
///   subtree rebuilds (Scaffold + Stack + providers + banner + panel) → paint.
/// - New path: ML Kit result → `notifyListeners` → single CustomPainter repaint.
///
/// This eliminates ~30 full widget-tree rebuilds per second, freeing the UI
/// thread for input and reducing perceived jitter.
class LipstickController extends ChangeNotifier {
  LipstickController({
    Color initialColor   = const Color(0xFF982A2A),
    double initialOpacity = 0.6,
  })  : _lipColor = initialColor,
        _opacity  = initialOpacity;

  LipContours? _lipContours;
  Color  _lipColor;
  double _opacity;
  bool   _visible = true;

  LipContours? get lipContours => _lipContours;
  Color         get lipColor    => _lipColor;
  double        get opacity     => _opacity;
  bool          get visible     => _visible;

  /// Updates the lip landmark data and schedules a repaint.
  /// Pass `null` to clear the overlay (face not detected).
  void updateContours(LipContours? contours) {
    _lipContours = contours;
    notifyListeners();
  }

  /// Syncs the active shade colour. No-ops if colour is unchanged.
  void updateColor(Color color, {double? opacity}) {
    var changed = false;
    if (_lipColor != color) {
      _lipColor = color;
      changed   = true;
    }
    if (opacity != null && _opacity != opacity) {
      _opacity = opacity;
      changed  = true;
    }
    if (changed) notifyListeners();
  }

  /// Shows or hides the overlay (e.g. during "hold to compare").
  void setVisible(bool value) {
    if (_visible == value) return;
    _visible = value;
    notifyListeners();
  }
}

// ── LipstickPainter ────────────────────────────────────────────────────────────

/// High-performance [CustomPainter] that renders a lipstick colour overlay
/// onto the lips detected by ML Kit Face Mesh.
///
/// Uses [LipstickController] (a [ChangeNotifier]) as its `repaint` listenable.
/// This means every call to [LipstickController.updateContours] schedules a
/// raster-layer repaint **without** a widget-tree rebuild.
///
/// Design decisions:
/// - [Path.combine] with [PathOperation.difference] cuts away the mouth
///   opening so the overlay does not paint over the interior.
/// - [BlendMode.multiply] produces natural-looking blending with skin tone.
/// - The [Paint] object is pre-allocated in the constructor and reused
///   across frames to avoid GC pressure.
/// - Paths use Catmull-Rom cubic splines (smooth curves, not polygon edges).
/// - [shouldRepaint] always returns `false` because re-draws are driven
///   exclusively by the controller listenable, not by property diffing.
class LipstickPainter extends CustomPainter {
  LipstickPainter({required LipstickController controller})
      : _controller = controller,
        _lipPaint   = Paint()
          ..style     = PaintingStyle.fill
          ..blendMode = BlendMode.multiply,
        super(repaint: controller);

  final LipstickController _controller;

  /// Pre-allocated and reused every frame.
  final Paint _lipPaint;

  @override
  void paint(Canvas canvas, Size size) {
    if (!_controller.visible) return;

    // Sync paint color from controller (cheap, no allocation).
    _lipPaint.color =
        _controller.lipColor.withValues(alpha: _controller.opacity);

    final contours = _controller.lipContours;
    if (contours == null ||
        contours.outer.isEmpty ||
        contours.inner.isEmpty) {
      return;
    }

    final outerPath = _buildPath(contours.outer);
    final innerPath = _buildPath(contours.inner);

    // outer lip area MINUS mouth opening → only the lip surface.
    final visibleLipPath = Path.combine(
      PathOperation.difference,
      outerPath,
      innerPath,
    );

    canvas.drawPath(visibleLipPath, _lipPaint);
  }

  /// Repaint is driven entirely by the [LipstickController] listenable.
  /// Property diffing is unnecessary and always returns false.
  @override
  bool shouldRepaint(LipstickPainter _) => false;

  // ── Path builder ────────────────────────────────────────────────────────────

  /// Builds a smooth closed [Path] from [offsets] using Catmull-Rom splines.
  ///
  /// Straight `lineTo` produces a jagged polygon that accentuates per-frame
  /// ML Kit jitter. Catmull-Rom yields smooth curves that match the lip shape
  /// and naturally absorb small landmark variations between frames.
  ///
  /// Conversion from Catmull-Rom to cubic Bézier:
  ///   cp1 = curr + (next  - prev ) / 6
  ///   cp2 = next − (after - curr ) / 6
  static Path _buildPath(List<Offset> offsets) {
    final path = Path();
    if (offsets.isEmpty) return path;
    if (offsets.length == 1) {
      path.addOval(Rect.fromCircle(center: offsets.first, radius: 1));
      return path;
    }
    if (offsets.length == 2) {
      path.moveTo(offsets[0].dx, offsets[0].dy);
      path.lineTo(offsets[1].dx, offsets[1].dy);
      return path;
    }

    final n = offsets.length;
    path.moveTo(offsets[0].dx, offsets[0].dy);

    for (int i = 0; i < n - 1; i++) {
      final prev  = offsets[(i - 1 + n) % n];
      final curr  = offsets[i];
      final next  = offsets[(i + 1) % n];
      final after = offsets[(i + 2) % n];

      final cp1 = Offset(
        curr.dx + (next.dx - prev.dx) / 6,
        curr.dy + (next.dy - prev.dy) / 6,
      );
      final cp2 = Offset(
        next.dx - (after.dx - curr.dx) / 6,
        next.dy - (after.dy - curr.dy) / 6,
      );

      path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, next.dx, next.dy);
    }

    path.close();
    return path;
  }
}

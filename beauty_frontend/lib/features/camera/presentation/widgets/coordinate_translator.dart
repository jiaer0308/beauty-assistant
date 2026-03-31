import 'dart:io';
import 'dart:ui';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:google_mlkit_commons/google_mlkit_commons.dart';

/// Maps raw [CameraImage] (YUV / BGRA) coordinates from the ML Kit face mesh
/// output to Canvas (UI) coordinates, accounting for sensor orientation,
/// device rotation and front-camera mirroring.
class CoordinateTranslator {
  const CoordinateTranslator({
    required this.imageWidth,
    required this.imageHeight,
    required this.screenWidth,
    required this.screenHeight,
    required this.isPainterMirrored,
  });

  final int imageWidth;
  final int imageHeight;
  final double screenWidth;
  final double screenHeight;
  final bool isPainterMirrored;

  /// Translates X coordinate from image space to canvas space.
  double translateX(double x) {
    final double scale = screenWidth / imageWidth;
    if (isPainterMirrored) {
      return screenWidth - (x * scale);
    }
    return x * scale;
  }

  /// Translates Y coordinate from image space to canvas space.
  double translateY(double y) {
    final double scale = screenHeight / imageHeight;
    return y * scale;
  }
}

/// Converts a [CameraImage] from the camera plugin stream into an
/// [InputImage] that the ML Kit [FaceMeshDetector] can consume.
///
/// Handles:
/// - Android NV21 (single-plane, raw=17)
/// - Android YUV_420_888 (multi-plane, raw=35) — used by OPPO/OnePlus and
///   many other Android OEMs even when [ImageFormatGroup.nv21] is requested.
///   We manually compose the NV21 buffer from the three Y/U/V planes.
/// - iOS BGRA8888
/// - Correct sensor orientation computation
InputImage? convertCameraImageToInputImage(
  CameraImage image,
  CameraDescription camera,
  int? deviceRotationDegrees,
) {
  final sensorOrientation = camera.sensorOrientation;
  InputImageRotation? rotation;

  if (Platform.isIOS) {
    rotation = InputImageRotationValue.fromRawValue(sensorOrientation);
  } else if (Platform.isAndroid) {
    final uiRotation = deviceRotationDegrees ?? 0;
    int rotationCompensation;
    if (camera.lensDirection == CameraLensDirection.front) {
      rotationCompensation = (sensorOrientation + uiRotation) % 360;
    } else {
      rotationCompensation = (sensorOrientation - uiRotation + 360) % 360;
    }
    rotation = InputImageRotationValue.fromRawValue(rotationCompensation);
  }

  if (rotation == null) return null;

  // ── Android multi-plane (YUV_420_888) ─────────────────────────────────────
  // On Android, the camera plugin can return YUV_420_888 (raw=35) with 3
  // planes even when NV21 (raw=17) is requested via ImageFormatGroup.nv21.
  // OPPO/OnePlus and several Samsung/Xiaomi devices do this. ML Kit does NOT
  // accept YUV_420_888 directly, so we manually compose a correct NV21 buffer.
  //
  // This branch must be checked BEFORE the single-format check below, because
  // YUV_420_888 maps to `null` in InputImageFormatValue, causing a silent
  // return-null on every frame (= no AR overlay at all).
  if (Platform.isAndroid && image.planes.length == 3) {
    final yPlane = image.planes[0];
    final uPlane = image.planes[1];
    final vPlane = image.planes[2];

    final int width  = image.width;
    final int height = image.height;
    final int uvPixelStride = uPlane.bytesPerPixel ?? 1;
    final int uvRowStride   = uPlane.bytesPerRow;

    // NV21 layout: Y plane (w×h bytes) + interleaved VU plane (w×h/2 bytes).
    final nv21 = Uint8List(width * height * 3 ~/ 2);

    // 1. Copy Y plane (row-by-row to handle non-contiguous strides).
    for (int row = 0; row < height; row++) {
      final int srcStart = row * yPlane.bytesPerRow;
      final int dstStart = row * width;
      nv21.setRange(dstStart, dstStart + width,
          yPlane.bytes, srcStart);
    }

    // 2. Interleave V then U into the chroma plane (NV21 is VU, not UV).
    final int uvHeight = height ~/ 2;
    final int uvWidth  = width  ~/ 2;
    int nv21UvOffset = width * height;
    for (int row = 0; row < uvHeight; row++) {
      for (int col = 0; col < uvWidth; col++) {
        final int pixelOffset = row * uvRowStride + col * uvPixelStride;
        nv21[nv21UvOffset++] = vPlane.bytes[pixelOffset]; // V
        nv21[nv21UvOffset++] = uPlane.bytes[pixelOffset]; // U
      }
    }

    return InputImage.fromBytes(
      bytes: nv21,
      metadata: InputImageMetadata(
        size: Size(width.toDouble(), height.toDouble()),
        rotation: rotation,
        format: InputImageFormat.nv21,
        bytesPerRow: width,
      ),
    );
  }

  // ── iOS BGRA8888 / Android true NV21 (single-plane) ─────────────────────
  final format = InputImageFormatValue.fromRawValue(image.format.raw);
  if (format == null ||
      (format != InputImageFormat.nv21 &&
       format != InputImageFormat.bgra8888)) {
    // Log once so we can diagnose unknown formats without logspam.
    debugPrint(
      '[AR] Unsupported CameraImage format: raw=${image.format.raw}. '
      'planes=${image.planes.length}. AR overlay disabled.',
    );
    return null;
  }

  final plane = image.planes.first;
  return InputImage.fromBytes(
    bytes: plane.bytes,
    metadata: InputImageMetadata(
      size: Size(image.width.toDouble(), image.height.toDouble()),
      rotation: rotation,
      format: format,
      bytesPerRow: plane.bytesPerRow,
    ),
  );
}

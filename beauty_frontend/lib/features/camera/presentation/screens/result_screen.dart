import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../../services/api/sca_service.dart';

class ResultScreen extends ConsumerStatefulWidget {
  final Map<String, dynamic>? data;

  const ResultScreen({super.key, this.data});

  @override
  ConsumerState<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends ConsumerState<ResultScreen> with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _progressController;
  late Animation<double> _progressAnimation;

  @override
  void initState() {
    super.initState();
    // Rotation animation
    _rotationController = AnimationController(
       vsync: this,
       duration: const Duration(seconds: 10),
    )..repeat();

    // Progress animation (simulating API wait time visually while waiting for the real response)
    _progressController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4), // Visual minimum wait
    );

    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _progressController, curve: Curves.easeInOut),
    );

    // Start progress animation
    _progressController.forward();
    
    // Trigger actual API Call
    _analyzeImage();
  }

  Future<void> _analyzeImage() async {
    if (widget.data == null || widget.data!['imagePath'] == null) {
      _showError('No image provided.');
      return;
    }

    final String imagePath = widget.data!['imagePath'];
    final Map<String, dynamic>? rawQuizData = widget.data!['quizData'];
    
    // Convert generic map to QuizData object
    QuizData? quizData;
    if (rawQuizData != null) {
       quizData = QuizData(
         skinType: rawQuizData['skin_type'],
         sunReaction: rawQuizData['sun_reaction'],
         veinColor: rawQuizData['wrist_vein'],
         naturalHairColor: rawQuizData['hair_color'],
         jewelryPreference: rawQuizData['jewelry'],
       );
    }

    try {
      final scaService = ref.read(scaServiceProvider);
      final response = await scaService.analyzeImage(imagePath, quizData);
      
      // Ensure the visual progress bar completes before navigating
      if (!_progressController.isCompleted) {
         await _progressController.forward();
      }

      if (mounted) {
        context.pushReplacement('/dashboard', extra: response);
      }
    } catch (e) {
      if (mounted) {
        _showError('Analysis failed: $e');
      }
    }
  }
  
  void _showError(String message) {
     ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: Colors.red));
     context.pop();
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _progressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: SafeArea(
        child: Column(
          children: [
            // 1. Header
            _buildHeader(context),
            
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // 2. Central Visual (12-Season Color Wheel)
                  _buildCentralVisual(),
                  
                  const SizedBox(height: 64),
                  
                  // 3. Status Text Block
                  _buildStatusText(),
                ],
              ),
            ),
            
            // 4. Progress Section
            _buildProgressSection(),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back),
            color: GlowTheme.deepTaupe,
            onPressed: () => context.pop(),
          ),
          const Text(
            'Color Analysis',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: GlowTheme.deepTaupe,
            ),
          ),
          TextButton(
            onPressed: () => context.pop(),
            child: const Text(
              'Cancel',
              style: TextStyle(
                color: GlowTheme.deepTaupe,
                fontSize: 16,
                fontWeight: FontWeight.w500, // Medium
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCentralVisual() {
    return AnimatedBuilder(
      animation: _rotationController,
      builder: (context, child) {
        return Transform.rotate(
          angle: _rotationController.value * 2 * math.pi,
          child: SizedBox(
            width: 240,
            height: 240,
            child: Stack(
              alignment: Alignment.center,
              children: [
                // The Donut Wheel
                CustomPaint(
                  size: const Size(240, 240),
                  painter: ColorWheelPainter(),
                ),
                // Center minimalist sun icon (counter-rotated to stay upright)
                Transform.rotate(
                  angle: -(_rotationController.value * 2 * math.pi),
                  child: const Icon(
                    Icons.wb_sunny_outlined,
                    size: 48,
                    color: GlowTheme.deepTaupe,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatusText() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            'Analyzing your undertones...',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: GlowTheme.deepTaupe,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 12),
          Text(
            'Extracting skin, eye, and\nhair color profiles.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: GlowTheme.deepTaupe,
              fontSize: 16,
              fontWeight: FontWeight.w500, // Medium weight
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32.0),
      child: AnimatedBuilder(
        animation: _progressAnimation,
        builder: (context, child) {
          int percentage = (_progressAnimation.value * 100).toInt();
          return Row(
            children: [
              Expanded(
                child: SegmentedProgressBar(progress: _progressAnimation.value),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 48,
                child: Text(
                  '$percentage%',
                  textAlign: TextAlign.right,
                  style: const TextStyle(
                    color: GlowTheme.deepTaupe,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class SegmentedProgressBar extends StatelessWidget {
  final double progress; // 0.0 to 1.0
  final int segments = 10;
  final double spacing = 4.0;

  const SegmentedProgressBar({super.key, required this.progress});

  @override
  Widget build(BuildContext context) {
    int activeSegments = (progress * segments).round();
    
    return Row(
      children: List.generate(segments, (index) {
        bool isActive = index < activeSegments;
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: index == segments - 1 ? 0 : spacing),
            height: 6,
            decoration: BoxDecoration(
              color: isActive ? GlowTheme.champagneGold : GlowTheme.oatmeal,
              borderRadius: BorderRadius.circular(3.0),
            ),
          ),
        );
      }),
    );
  }
}

class ColorWheelPainter extends CustomPainter {
  // 12 Curated Colors representing the seasons, forming a harmonious wheel
  final List<Color> seasonColors = [
    const Color(0xFFFDEBB3), // Light Spring (pale butter yellow)
    const Color(0xFFF4A261), // True Spring (warm coral)
    const Color(0xFFE76F51), // Bright Spring (terracotta/bright rust)
    const Color(0xFFE2C2C6), // Light Summer (soft cool pink)
    const Color(0xFFA1ADC7), // True Summer (slate blue)
    const Color(0xFF9CB3A1), // Soft Summer (sage green)
    const Color(0xFFD4A373), // Soft Autumn (pale oat/fawn)
    const Color(0xFFCB793A), // True Autumn (warm mustard/ochre)
    const Color(0xFF8B5A2B), // Dark Autumn (deep warm brown)
    const Color(0xFF55323E), // Dark Winter (deep cool burgundy)
    const Color(0xFF1E3F5A), // True Winter (sapphire navy)
    const Color(0xFF5B3C68), // Bright Winter (vibrant aubergine)
  ];

  @override
  void paint(Canvas canvas, Size size) {
    double strokeWidth = 40.0;
    double radius = (size.width / 2) - (strokeWidth / 2);
    Offset center = Offset(size.width / 2, size.height / 2);
    
    double sweepAngle = (2 * math.pi) / 12;

    for (int i = 0; i < 12; i++) {
      Paint paint = Paint()
        ..color = seasonColors[i]
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth;
        
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        i * sweepAngle,
        sweepAngle,
        false, // useCenter
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

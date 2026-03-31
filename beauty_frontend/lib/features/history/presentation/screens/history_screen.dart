import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/models/auth_state.dart';
import '../../../../services/api/history_service.dart';

final historyProvider = FutureProvider<List<dynamic>>((ref) async {
  final historyService = ref.read(historyServiceProvider);
  return await historyService.getHistory();
});

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  // Local state for active dismissal without waiting for provider refresh
  List<dynamic>? _localHistory;

  @override
  Widget build(BuildContext context) {
    final historyAsync = ref.watch(historyProvider);
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      body: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: _buildEditorialHeader(),
          ),
          if (authState.status == AuthStatus.unauthenticated)
            SliverFillRemaining(
              hasScrollBody: false,
              child: _buildGuestEmptyState(),
            )
          else
            historyAsync.when(
              data: (history) {
                // Initialize local history once per successful fetch
                _localHistory ??= List<dynamic>.from(history);
                
                if (_localHistory!.isEmpty) {
                  return SliverFillRemaining(
                    hasScrollBody: false,
                    child: _buildEmptyState(),
                  );
                }
                return _buildHistoryList(context, _localHistory!);
              },
              loading: () => const SliverFillRemaining(
                child: Center(
                  child: CircularProgressIndicator(color: GlowTheme.champagneGold),
                ),
              ),
              error: (err, stack) => SliverFillRemaining(
                child: Center(child: Text('Error: $err')),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildEditorialHeader() {
    return Padding(
      padding: const EdgeInsets.only(left: 24, right: 24, top: 64, bottom: 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'SEASONAL COLOR ANALYSIS',
            style: TextStyle(
              color: GlowTheme.deepTaupe,
              fontSize: 12,
              letterSpacing: 1.5,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your Palette Journey',
            style: GoogleFonts.playfairDisplay(
              fontSize: 32,
              color: GlowTheme.deepTaupe,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryList(BuildContext context, List<dynamic> history) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final session = history[index];
          final sessionId = session['id']?.toString() ?? index.toString();
          
          return Dismissible(
            key: Key('history_$sessionId'),
            direction: DismissDirection.endToStart,
            background: _buildDismissBackground(),
            onDismissed: (direction) {
              setState(() {
                _localHistory?.removeAt(index);
              });
              
              // TODO: Trigger backend API call to delete the analysis record
              // Example: ref.read(historyServiceProvider).deleteHistory(sessionId);
              
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Analysis removed from archives'),
                  duration: Duration(seconds: 2),
                ),
              );
            },
            child: _buildHistoryCard(context, session),
          );
        },
        childCount: history.length,
      ),
    );
  }

  Widget _buildDismissBackground() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16, left: 24, right: 24),
      padding: const EdgeInsets.only(right: 24),
      alignment: Alignment.centerRight,
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E), // Dark sophisticated color
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.delete_outline, color: Colors.white),
          SizedBox(height: 4),
          Text(
            'DELETE',
            style: TextStyle(
              color: Colors.white,
              fontSize: 10,
              letterSpacing: 1.2,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryCard(BuildContext context, dynamic session) {
    final seasonName = session['season_name']?.toString().replaceAll('_', ' ').toUpperCase() ?? 'UNKNOWN';
    final date = DateTime.tryParse(session['created_at'].toString()) ?? DateTime.now();

    return Container(
      margin: const EdgeInsets.only(bottom: 16, left: 24, right: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: GlowTheme.oatmeal, width: 1),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: _getSeasonColor(seasonName),
            shape: BoxShape.circle,
          ),
        ),
        title: Text(
          seasonName,
          style: const TextStyle(
            color: GlowTheme.deepTaupe,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4.0),
          child: Text(
            'Analyzed on ${_formatDate(date)}',
            style: const TextStyle(
              color: GlowTheme.oatmeal,
              fontSize: 14,
            ),
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: GlowTheme.oatmeal),
        onTap: () {
          // TODO: Navigate to Detail
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.auto_awesome_mosaic_outlined, size: 48, color: GlowTheme.oatmeal),
            SizedBox(height: 16),
            Text(
              'No archives yet',
              style: TextStyle(
                color: GlowTheme.deepTaupe,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Your future color analysis journeys will be saved here.',
              textAlign: TextAlign.center,
              style: TextStyle(color: GlowTheme.oatmeal),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGuestEmptyState() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.lock_outline, size: 48, color: GlowTheme.oatmeal),
            SizedBox(height: 16),
            Text(
              'Sign in to save archives',
              style: TextStyle(
                color: GlowTheme.deepTaupe,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Create an account to keep track of your seasonal color profiles forever.',
              textAlign: TextAlign.center,
              style: TextStyle(color: GlowTheme.oatmeal),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[date.month - 1]} ${date.day}, ${date.year}';
  }

  Color _getSeasonColor(String seasonName) {
    final name = seasonName.toLowerCase();
    
    // Spring
    if (name.contains('light spring')) return const Color(0xFFFDE68A);
    if (name.contains('true spring') || name.contains('warm spring')) return const Color(0xFFFBBF24);
    if (name.contains('clear spring') || name.contains('bright spring')) return const Color(0xFFF59E0B);
    
    // Summer
    if (name.contains('light summer')) return const Color(0xFFBFDBFE);
    if (name.contains('true summer') || name.contains('cool summer')) return const Color(0xFF60A5FA);
    if (name.contains('soft summer')) return const Color(0xFF9CA3AF);
    
    // Autumn
    if (name.contains('soft autumn')) return const Color(0xFFD4D4D8);
    if (name.contains('true autumn') || name.contains('warm autumn')) return const Color(0xFFD84315);
    if (name.contains('deep autumn') || name.contains('dark autumn')) return const Color(0xFF5D4037);
    
    // Winter
    if (name.contains('clear winter') || name.contains('bright winter')) return const Color(0xFFE11D48);
    if (name.contains('true winter') || name.contains('cool winter')) return const Color(0xFF2563EB);
    if (name.contains('deep winter') || name.contains('dark winter')) return const Color(0xFF1E3A8A);

    // Default Fallback
    return GlowTheme.champagneGold;
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/models/auth_state.dart';
import '../../../camera/presentation/providers/color_analysis_provider.dart';
import '../../data/models/history_models.dart';
import '../providers/history_provider.dart';
import '../../../../core/constants/season_constants.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(historyListProvider);
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text(
          'ARCHIVES',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe,
            fontSize: 14,
            letterSpacing: 2.0,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(child: _buildEditorialHeader()),
          if (authState.status == AuthStatus.unauthenticated)
            SliverFillRemaining(
              hasScrollBody: false,
              child: _buildGuestEmptyState(),
            )
          else
            historyAsync.when(
              data: (history) {
                if (history.isEmpty) {
                  return SliverFillRemaining(
                    hasScrollBody: false,
                    child: _buildEmptyState(),
                  );
                }
                return _buildHistoryList(context, ref, history);
              },
              loading: () => const SliverFillRemaining(
                child: Center(
                  child: CircularProgressIndicator(color: GlowTheme.champagneGold),
                ),
              ),
              error: (err, _) => SliverFillRemaining(
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.cloud_off_outlined,
                            size: 48, color: GlowTheme.oatmeal),
                        const SizedBox(height: 16),
                        Text(
                          'Could not load archives',
                          style: GoogleFonts.playfairDisplay(
                            color: GlowTheme.deepTaupe,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        ElevatedButton(
                          onPressed: () =>
                              ref.read(historyListProvider.notifier).refresh(),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: GlowTheme.deepTaupe,
                            foregroundColor: GlowTheme.pearlWhite,
                          ),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ── Editorial header ──────────────────────────────────────────────────────

  Widget _buildEditorialHeader() {
    return Padding(
      padding: const EdgeInsets.only(left: 24, right: 24, top: 16, bottom: 32),
      child: Center(
        child: Column(
          children: [
            Text(
              'SEASONAL COLOR ANALYSIS',
              textAlign: TextAlign.center,
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe,
                fontSize: 10,
                letterSpacing: 2.0,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── History list ──────────────────────────────────────────────────────────

  Widget _buildHistoryList(
      BuildContext context, WidgetRef ref, List<HistorySession> history) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final session = history[index];
          return Dismissible(
            key: Key('history_${session.id}'),
            direction: DismissDirection.endToStart,
            background: _buildDismissBackground(),
            // Intercept dismiss and show confirmation before committing
            confirmDismiss: (_) async =>
                _showDeleteConfirmation(context, ref, session),
            onDismissed: (_) {
              // Actual deletion is handled in confirmDismiss → _deleteSession
              // onDismissed is called after confirmDismiss returns true
            },
            child: _buildHistoryCard(context, ref, session),
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
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.delete_outline, color: Colors.white),
          const SizedBox(height: 4),
          Text(
            'DELETE',
            style: GoogleFonts.plusJakartaSans(
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

  // ── History card (Task 3.1 — SCA data display) ────────────────────────────

  Widget _buildHistoryCard(
      BuildContext context, WidgetRef ref, HistorySession session) {
    final seasonColor = SeasonTheme.getSeasonColor(session.seasonName); 
    return Container(
      margin: const EdgeInsets.only(bottom: 16, left: 24, right: 24),
      child: Material(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: GlowTheme.oatmeal, width: 1),
          borderRadius: BorderRadius.circular(16),
        ),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          splashColor: GlowTheme.champagneGold.withOpacity(0.08),
          onTap: () => context.push('/history/${session.id}'),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            child: Row(
              children: [
                // Season colour circle
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: seasonColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 16),

                // Main text column
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Season display name
                      Text(
                        session.seasonDisplayName,
                        style: GoogleFonts.playfairDisplay(
                          color: GlowTheme.deepTaupe,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 4),

                      // Date + product count subtitle
                      Text(
                        'Analyzed on ${_formatDate(session.createdAt)} · \n '
                        '${session.itemCount} product${session.itemCount == 1 ? '' : 's'}',
                        style: GoogleFonts.plusJakartaSans(
                          color: GlowTheme.deepTaupe.withValues(alpha: 0.6),
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                  ),
                ),

                // Trailing controls
                Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: Icon(
                        Icons.delete_outline,
                        color: GlowTheme.deepTaupe.withValues(alpha: 0.35),
                        size: 20,
                      ),
                      tooltip: 'Delete archive',
                      onPressed: () =>
                          _showDeleteConfirmation(context, ref, session),
                    ),
                    Icon(
                      Icons.chevron_right,
                      color: GlowTheme.deepTaupe.withValues(alpha: 0.3),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Renders a small pill tag showing the analysis origin (SCA SCAN / MANUAL).
  /// Returns a "N/A" tag when the analysis type is missing.
  Widget _buildAnalysisTag(String? rawType) {
    final isEmpty = rawType == null || rawType.isEmpty;
    final label = isEmpty
        ? 'N/A'
        : rawType
            .split('_')
            .map((w) => w.toUpperCase())
            .join(' ');

    final color = isEmpty
        ? GlowTheme.oatmeal
        : (rawType == 'sca_scan'
            ? GlowTheme.champagneGold.withOpacity(0.15)
            : GlowTheme.oatmeal.withOpacity(0.3));

    final textColor = isEmpty
        ? GlowTheme.deepTaupe.withOpacity(0.5)
        : (rawType == 'sca_scan'
            ? const Color(0xFFA07830)
            : GlowTheme.deepTaupe.withOpacity(0.6));

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: textColor.withOpacity(0.3),
          width: 0.8,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (!isEmpty) ...[
            Icon(
              rawType == 'sca_scan'
                  ? Icons.auto_awesome
                  : Icons.tune_rounded,
              size: 10,
              color: textColor,
            ),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: GoogleFonts.plusJakartaSans(
              fontSize: 9,
              fontWeight: FontWeight.w700,
              color: textColor,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }

  // ── Delete with confirmation (Task 3.3) ────────────────────────────────────

  /// Shows a confirmation dialog.
  /// Returns `true` if the user confirmed; the Dismissible will commit.
  /// Returns `false` if cancelled; the Dismissible will animate back.
  Future<bool> _showDeleteConfirmation(
      BuildContext context, WidgetRef ref, HistorySession session) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: GlowTheme.pearlWhite,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(
          'Delete Archive?',
          style: GoogleFonts.playfairDisplay(
            color: GlowTheme.deepTaupe,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          'This will permanently remove the "${session.seasonDisplayName}" '
          'analysis from your archives. This action cannot be undone.',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe.withValues(alpha: 0.8),
            height: 1.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(
              'Cancel',
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe.withValues(alpha: 0.6),
              ),
            ),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1E1E1E),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
              elevation: 0,
            ),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(
              'Delete',
              style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );

    if (confirmed != true) return false;

    // Perform optimistic delete
    await _deleteSession(context, ref, session.id);
    return true;
  }

  Future<void> _deleteSession(
      BuildContext context, WidgetRef ref, int sessionId) async {
    try {
      await ref.read(historyListProvider.notifier).deleteSession(sessionId);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Archive removed successfully',
              style: GoogleFonts.plusJakartaSans(),
            ),
            backgroundColor: GlowTheme.deepTaupe,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Delete failed — please try again',
              style: GoogleFonts.plusJakartaSans(),
            ),
            backgroundColor: Colors.red.shade700,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  // ── Empty states ──────────────────────────────────────────────────────────

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.auto_awesome_mosaic_outlined,
                size: 48, color: GlowTheme.oatmeal),
            const SizedBox(height: 16),
            Text(
              'No archives yet',
              style: GoogleFonts.playfairDisplay(
                color: GlowTheme.deepTaupe,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Your future color analysis journeys will be saved here.',
              textAlign: TextAlign.center,
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe.withValues(alpha: 0.7),
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGuestEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.lock_outline, size: 48, color: GlowTheme.oatmeal),
            const SizedBox(height: 16),
            Text(
              'Sign in to save archives',
              style: GoogleFonts.playfairDisplay(
                color: GlowTheme.deepTaupe,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Create an account to keep track of your seasonal color profiles forever.',
              textAlign: TextAlign.center,
              style: GoogleFonts.plusJakartaSans(
                color: GlowTheme.deepTaupe.withValues(alpha: 0.7),
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _formatDate(DateTime date) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[date.month - 1]} ${date.day}, ${date.year}';
  }
}
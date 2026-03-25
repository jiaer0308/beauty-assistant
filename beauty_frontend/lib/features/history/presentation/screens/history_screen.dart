import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/glow_theme.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/models/auth_state.dart';
import '../../../../services/api/history_service.dart';

final historyProvider = FutureProvider<List<dynamic>>((ref) async {
  final historyService = ref.read(historyServiceProvider);
  return await historyService.getHistory();
});

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(historyProvider);
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        title: const Text('My History', style: TextStyle(color: GlowTheme.deepTaupe, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: GlowTheme.deepTaupe),
          onPressed: () => context.pop(),
        ),
      ),
      body: authState.status == AuthStatus.unauthenticated 
        ? _buildGuestEmptyState()
        : historyAsync.when(
            data: (history) => history.isEmpty 
                ? _buildEmptyState() 
                : _buildHistoryList(context, history),
            loading: () => const Center(child: CircularProgressIndicator(color: GlowTheme.champagneGold)),
            error: (err, stack) => Center(child: Text('Error: $err')),
          ),
    );
  }

  Widget _buildHistoryList(BuildContext context, List<dynamic> history) {
    return ListView.builder(
      padding: const EdgeInsets.all(24),
      itemCount: history.length,
      itemBuilder: (context, index) {
        final session = history[index];
        final season = session['season_name'] ?? 'Unknown';
        final date = DateTime.parse(session['created_at']);
        
        return Card(
          elevation: 0,
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: GlowTheme.oatmeal, width: 1),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16),
            title: Text(
              season.toString().replaceAll('_', ' ').toUpperCase(),
              style: const TextStyle(fontWeight: FontWeight.bold, color: GlowTheme.deepTaupe),
            ),
            subtitle: Text(
              'Analyzed on ${date.day}/${date.month}/${date.year}',
              style: const TextStyle(color: GlowTheme.oatmeal),
            ),
            trailing: const Icon(Icons.chevron_right, color: GlowTheme.deepTaupe),
            onTap: () {
              // TODO: Navigate to Detail
            },
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history_outlined, size: 64, color: GlowTheme.oatmeal),
          SizedBox(height: 16),
          Text('No history yet.', style: TextStyle(color: GlowTheme.deepTaupe, fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('Your color analysis results will appear here.', style: TextStyle(color: GlowTheme.oatmeal)),
        ],
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
            Icon(Icons.lock_outline, size: 64, color: GlowTheme.oatmeal),
            SizedBox(height: 16),
            Text('Sign in to save history', style: TextStyle(color: GlowTheme.deepTaupe, fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Create an account to keep track of your seasonal color profiles forever.', textAlign: TextAlign.center, style: TextStyle(color: GlowTheme.oatmeal)),
          ],
        ),
      ),
    );
  }
}

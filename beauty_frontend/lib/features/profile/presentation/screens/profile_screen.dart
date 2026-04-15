import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/glow_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: GlowTheme.pearlWhite,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text(
          'PROFILE',
          style: GoogleFonts.plusJakartaSans(
            color: GlowTheme.deepTaupe,
            fontSize: 14,
            letterSpacing: 2.0,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: Column(
        children: [
          const SizedBox(height: 48),
          
          // Menu List
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                children: [
                  _buildMenuItem(
                    label: 'Saved Collection',
                    onTap: () {
                      context.push('/favorites');
                    },
                    hasTrailing: true,
                  ),
                  _buildMenuItem(
                    label: 'Log Out',
                    onTap: () {
                      context.push('/welcome');
                    },
                    isDestructive: true,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required String label,
    required VoidCallback onTap,
    bool hasTrailing = false,
    bool isDestructive = false,
  }) {
    final textColor = isDestructive 
        ? Colors.red.shade800.withValues(alpha: 0.8) 
        : GlowTheme.deepTaupe;

    return InkWell(
      onTap: onTap,
      splashColor: GlowTheme.champagneGold.withValues(alpha: 0.1),
      highlightColor: Colors.black.withValues(alpha: 0.02),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20.0),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: GlowTheme.oatmeal.withValues(alpha: 0.5),
              width: 1,
            ),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: GoogleFonts.plusJakartaSans(
                color: textColor,
                fontSize: 16,
                fontWeight: isDestructive ? FontWeight.w500 : FontWeight.w600,
              ),
            ),
            if (hasTrailing)
              const Icon(
                Icons.chevron_right,
                color: GlowTheme.oatmeal,
                size: 24,
              ),
          ],
        ),
      ),
    );
  }
}

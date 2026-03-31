import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../theme/glow_theme.dart';

class ScaffoldWithNavBar extends StatelessWidget {
  const ScaffoldWithNavBar({
    required this.navigationShell,
    super.key,
  });

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: GlowTheme.oatmeal, width: 1),
          ),
        ),
        child: BottomNavigationBar(
          backgroundColor: GlowTheme.pearlWhite,
          elevation: 0,
          type: BottomNavigationBarType.fixed,
          showSelectedLabels: true,
          showUnselectedLabels: true,
          selectedItemColor: GlowTheme.deepTaupe,
          unselectedItemColor: GlowTheme.oatmeal,
          selectedLabelStyle: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
          ),
          unselectedLabelStyle: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.5,
          ),
          currentIndex: navigationShell.currentIndex,
          onTap: (int index) => _onTap(context, index),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.auto_awesome_outlined, size: 24),
              activeIcon: Icon(Icons.auto_awesome, size: 24),
              label: 'ATELIER',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.storefront_outlined, size: 24),
              label: 'BOUTIQUE',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.bookmark_border_outlined, size: 24),
              activeIcon: Icon(Icons.bookmark, size: 24),
              label: 'ARCHIVES',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline, size: 24),
              activeIcon: Icon(Icons.person, size: 24),
              label: 'PROFILE',
            ),
          ],
        ),
      ),
    );
  }

  void _onTap(BuildContext context, int index) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}

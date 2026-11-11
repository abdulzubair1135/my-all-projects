import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../core/theme.dart';

enum LogoVariant { classicNavyGold, slateMonochrome, frostedSilver, obsidianDark }

class InstitutionalLogo extends StatefulWidget {
  final double size;
  final bool animate;
  final LogoVariant variant;
  final bool showText;
  final String title;
  final String subtitle;

  const InstitutionalLogo({
    super.key,
    this.size = 56,
    this.animate = true,
    this.variant = LogoVariant.classicNavyGold,
    this.showText = false,
    this.title = 'SRK INSTITUTE',
    this.subtitle = 'Campus Coordination System',
  });

  @override
  State<InstitutionalLogo> createState() => _InstitutionalLogoState();
}

class _InstitutionalLogoState extends State<InstitutionalLogo>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pulseAnimation;
  late Animation<double> _glowAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3200),
    );

    if (widget.animate) {
      _pulseAnimation = Tween<double>(begin: 0.97, end: 1.03).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
      );
      _glowAnimation = Tween<double>(begin: 0.2, end: 0.65).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
      );
      _rotationAnimation = Tween<double>(begin: 0, end: 2 * math.pi).animate(
        CurvedAnimation(parent: _controller, curve: Curves.linear),
      );
      _controller.repeat(reverse: true);
    } else {
      _pulseAnimation = const AlwaysStoppedAnimation(1.0);
      _glowAnimation = const AlwaysStoppedAnimation(0.3);
      _rotationAnimation = const AlwaysStoppedAnimation(0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Style configurations based on variant
    final List<Color> bgGradient;
    final Color borderColor;
    final Color accentLineColor;
    final Color monogramColor;
    final Color glowColor;

    switch (widget.variant) {
      case LogoVariant.slateMonochrome:
        bgGradient = [const Color(0xFF1E293B), const Color(0xFF0F172A)];
        borderColor = const Color(0xFF94A3B8);
        accentLineColor = const Color(0xFFCBD5E1);
        monogramColor = Colors.white;
        glowColor = const Color(0xFF94A3B8);
        break;
      case LogoVariant.frostedSilver:
        bgGradient = [const Color(0xFF334155), const Color(0xFF1E293B)];
        borderColor = const Color(0xFFE2E8F0);
        accentLineColor = const Color(0xFFF8FAFC);
        monogramColor = const Color(0xFFF1F5F9);
        glowColor = const Color(0xFFCBD5E1);
        break;
      case LogoVariant.obsidianDark:
        bgGradient = [const Color(0xFF18181B), const Color(0xFF09090B)];
        borderColor = const Color(0xFF52525B);
        accentLineColor = const Color(0xFFA1A1AA);
        monogramColor = const Color(0xFFFAFAFA);
        glowColor = const Color(0xFF71717A);
        break;
      case LogoVariant.classicNavyGold:
      default:
        bgGradient = [const Color(0xFF0B2545), const Color(0xFF134074)];
        borderColor = const Color(0xFFC5A059);
        accentLineColor = const Color(0xFFE8D5A3);
        monogramColor = Colors.white;
        glowColor = const Color(0xFFC5A059);
        break;
    }

    Widget logoBox = AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final scale = widget.animate ? _pulseAnimation.value : 1.0;
        final glow = widget.animate ? _glowAnimation.value : 0.3;

        return Transform.scale(
          scale: scale,
          child: Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: bgGradient,
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(widget.size * 0.28),
              border: Border.all(
                color: borderColor.withOpacity(0.85),
                width: 1.5,
              ),
              boxShadow: [
                BoxShadow(
                  color: glowColor.withOpacity(glow * 0.5),
                  blurRadius: widget.size * 0.35,
                  spreadRadius: 1,
                  offset: const Offset(0, 3),
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.35),
                  blurRadius: widget.size * 0.2,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Subtle concentric precision orbit rings
                Container(
                  width: widget.size * 0.78,
                  height: widget.size * 0.78,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withOpacity(0.12),
                      width: 1,
                    ),
                  ),
                ),
                Container(
                  width: widget.size * 0.60,
                  height: widget.size * 0.60,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: borderColor.withOpacity(0.25),
                      width: 0.8,
                    ),
                  ),
                ),

                // Monogram Typography
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'SRK',
                      style: TextStyle(
                        fontFamily: 'Serif',
                        fontSize: widget.size * 0.30,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1.8,
                        color: monogramColor,
                        shadows: [
                          Shadow(
                            color: Colors.black.withOpacity(0.6),
                            offset: const Offset(0, 1),
                            blurRadius: 2,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 1),
                    Container(
                      width: widget.size * 0.36,
                      height: 1.5,
                      decoration: BoxDecoration(
                        color: accentLineColor,
                        borderRadius: BorderRadius.circular(1),
                        boxShadow: [
                          BoxShadow(
                            color: accentLineColor.withOpacity(0.7),
                            blurRadius: 3,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );

    if (!widget.showText) return logoBox;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        logoBox,
        const SizedBox(height: 12),
        Text(
          widget.title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.8,
            color: AppTheme.primaryNavy,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          widget.subtitle,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.6,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }
}

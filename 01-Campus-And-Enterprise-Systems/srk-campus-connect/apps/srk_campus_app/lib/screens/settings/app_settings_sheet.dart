import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';
import '../../core/theme.dart';
import '../../core/constants.dart';

class AppSettingsSheet extends StatelessWidget {
  const AppSettingsSheet({super.key});

  static void show(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => const AppSettingsSheet(),
    );
  }

  void _shareApp(BuildContext context) {
    final liveUrl = AppConstants.cloudflareTunnelUrl;
    final shareText = '''SRK Campus Institutional App
Official Institutional Presence, Principal Summon & Classroom Coordination Platform.

Download APK:
https://github.com/abdulzubair1135/srk-campus-platform/releases

Live Campus Web Portal & Audit Center:
$liveUrl/control-panel''';

    Share.share(shareText, subject: 'SRK Campus Application');
  }

  void _copyToClipboard(BuildContext context, String text, String label) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$label copied to clipboard!'),
        backgroundColor: AppTheme.primaryNavy,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.settings_rounded, color: AppTheme.primaryNavy),
                    SizedBox(width: 8),
                    Text(
                      'App Settings & Share',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.primaryNavy),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const Divider(),

            // 1. SHARE APP ACTION CARD
            Container(
              margin: const EdgeInsets.symmetric(vertical: 8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryNavy, AppTheme.secondaryNavy],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryNavy.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Share SRK Campus App',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.accentGold.withOpacity(0.25),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text('SUPER-APP', style: TextStyle(color: AppTheme.accentGold, fontSize: 10, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Share the app APK and cloud portal with teachers, staff, and students.',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.accentGold,
                        foregroundColor: AppTheme.primaryNavy,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      icon: const Icon(Icons.share_rounded),
                      label: const Text('SHARE APP NOW', style: TextStyle(fontWeight: FontWeight.bold)),
                      onPressed: () => _shareApp(context),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // 2. QUICK COPY LINKS
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const CircleAvatar(
                backgroundColor: Color(0xFFE3F2FD),
                child: Icon(Icons.link_rounded, color: Colors.blue),
              ),
              title: const Text('Copy Web Control Panel Link', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
              subtitle: const Text(AppConstants.cloudflareTunnelUrl, style: TextStyle(fontSize: 11)),
              trailing: const Icon(Icons.copy_rounded, size: 18),
              onTap: () => _copyToClipboard(
                context,
                '${AppConstants.cloudflareTunnelUrl}/control-panel',
                'Web Portal Link',
              ),
            ),

            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const CircleAvatar(
                backgroundColor: Color(0xFFE8F5E9),
                child: Icon(Icons.android_rounded, color: Colors.green),
              ),
              title: const Text('Copy APK Download Link', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
              subtitle: const Text('https://github.com/abdulzubair1135/srk-campus-platform/releases', style: TextStyle(fontSize: 11)),
              trailing: const Icon(Icons.copy_rounded, size: 18),
              onTap: () => _copyToClipboard(
                context,
                'https://github.com/abdulzubair1135/srk-campus-platform/releases',
                'APK Download Link',
              ),
            ),

            const Divider(),

            // 3. SYSTEM DIAGNOSTICS INFO
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('App Version', style: TextStyle(fontSize: 12, color: Colors.grey)),
                  Text('1.0.0 (Unified Build)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Cloud Server', style: TextStyle(fontSize: 12, color: Colors.grey)),
                  Text('Online (Port 5000 + Tunnel)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.green)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

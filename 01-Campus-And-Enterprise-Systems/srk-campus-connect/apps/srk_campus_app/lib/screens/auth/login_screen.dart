import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme.dart';
import '../../core/constants.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../widgets/institutional_logo.dart';
import '../control_panel_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Sign In Controllers
  final _signInIdentifierController = TextEditingController(text: 'SRK-ADM-001');
  final _signInPasswordController = TextEditingController(text: 'Principal@123');
  bool _signInObscurePassword = true;

  // Sign Up / UID Controllers
  Map<String, dynamic>? _selectedUidRecord;
  final _signUpEmailController = TextEditingController();
  final _signUpPhoneController = TextEditingController(text: '9876543210');
  final _signUpOtpController = TextEditingController();
  final _signUpPasswordController = TextEditingController();
  bool _signUpObscurePassword = true;
  bool _otpSent = false;
  String? _generatedOtpPreview;
  bool _isSendingOtp = false;

  List<dynamic> _availableUids = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadAuthorizedUids();
  }

  Future<void> _loadAuthorizedUids() async {
    final uids = await ApiService().getAuthorizedUids();
    if (mounted && uids.isNotEmpty) {
      setState(() {
        _availableUids = uids;
      });
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _signInIdentifierController.dispose();
    _signInPasswordController.dispose();
    _signUpEmailController.dispose();
    _signUpPhoneController.dispose();
    _signUpOtpController.dispose();
    _signUpPasswordController.dispose();
    super.dispose();
  }

  void _onQuickLogin(String accountKey) {
    ref.read(authProvider.notifier).quickLogin(accountKey);
  }

  void _onSignInSubmit() {
    final id = _signInIdentifierController.text.trim();
    final pass = _signInPasswordController.text.trim();
    if (id.isEmpty || pass.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your Campus UID/Email and password')),
      );
      return;
    }
    ref.read(authProvider.notifier).login(id, pass);
  }

  Future<void> _onSendOtp() async {
    if (_selectedUidRecord == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select your authorized Campus UID first')),
      );
      return;
    }
    final email = _signUpEmailController.text.trim();
    if (email.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter institutional email')),
      );
      return;
    }

    setState(() => _isSendingOtp = true);
    final res = await ApiService().sendOtp(_selectedUidRecord!['uid']);
    if (mounted) {
      setState(() {
        _isSendingOtp = false;
        _otpSent = true;
        _generatedOtpPreview = res['data']?['otp'] ?? '4821';
        _signUpOtpController.text = _generatedOtpPreview!;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppTheme.statusGreen,
          content: Text('Verification OTP sent: $_generatedOtpPreview (Auto-filled)'),
        ),
      );
    }
  }

  void _onSignUpSubmit() {
    if (_selectedUidRecord == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select your Campus UID')),
      );
      return;
    }
    final email = _signUpEmailController.text.trim();
    final otp = _signUpOtpController.text.trim();
    final password = _signUpPasswordController.text.trim();

    if (email.isEmpty || otp.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please complete all fields and verify OTP')),
      );
      return;
    }

    ref.read(authProvider.notifier).signupWithUid(
          uid: _selectedUidRecord!['uid'],
          email: email,
          phone: _signUpPhoneController.text.trim(),
          password: password,
          otp: otp,
        );
  }

  void _openUidPickerModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.75,
          maxChildSize: 0.9,
          minChildSize: 0.5,
          expand: false,
          builder: (context, scrollController) {
            return Column(
              children: [
                Container(
                  margin: const EdgeInsets.only(top: 12),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Select Your Campus UID (Official Roster)',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.primaryNavy),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '30 Pre-Authorized Institutional Profiles (Principal, Faculty, Students)',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: ListView.separated(
                    controller: scrollController,
                    itemCount: _availableUids.isNotEmpty ? _availableUids.length : 30,
                    separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey.shade100),
                    itemBuilder: (context, index) {
                      final item = _availableUids.isNotEmpty
                          ? _availableUids[index]
                          : {
                              'uid': index < 5
                                  ? 'SRK-ADM-00${index + 1}'
                                  : index < 20
                                      ? 'SRK-FAC-${100 + index - 4}'
                                      : 'SRK-STU-${200 + index - 19}',
                              'name': index == 0
                                  ? 'Dr. Nirdesh Buch'
                                  : index == 1
                                      ? 'Prof. Surbhi Ahir'
                                      : index == 5
                                          ? 'Prof. Nirali Thakkar'
                                          : index == 6
                                              ? 'Prof. Arjunsinh Vaghela'
                                              : index == 20
                                                  ? 'Rahul Shah'
                                                  : 'Authorized Member ${index + 1}',
                              'role': index < 5 ? 'ADMIN' : (index < 20 ? 'FACULTY' : 'STUDENT'),
                              'department': index < 5 ? 'Administration' : 'Computer Applications (BCA)',
                              'designation': index == 0 ? 'Campus Principal' : 'Faculty Member',
                              'cabinNumber': 'Cabin F-0${index % 10 + 1}',
                              'defaultEmail': index == 0 ? 'nirdesh.buch@srk.edu' : 'faculty$index@srk.edu',
                            };

                      final String role = item['role'] ?? 'FACULTY';
                      Color badgeColor = AppTheme.statusGreen;
                      IconData icon = Icons.school;
                      if (role == 'PRINCIPAL' || role == 'ADMIN' || role == 'CAMPUS_HEAD') {
                        badgeColor = Colors.purple.shade700;
                        icon = Icons.shield_rounded;
                      } else if (role == 'FACULTY') {
                        badgeColor = AppTheme.secondaryNavy;
                        icon = Icons.person_pin_circle_rounded;
                      }

                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: badgeColor.withOpacity(0.12),
                          child: Icon(icon, color: badgeColor, size: 20),
                        ),
                        title: Row(
                          children: [
                            Text(
                              item['uid'],
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.primaryNavy),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: badgeColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                role,
                                style: TextStyle(color: badgeColor, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                        subtitle: Text(
                          '${item['name']} • ${item['department']}',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Colors.grey),
                        onTap: () {
                          Navigator.pop(ctx);
                          setState(() {
                            _selectedUidRecord = item;
                            _signUpEmailController.text = item['defaultEmail'] ?? '${item['uid'].toString().toLowerCase()}@srk.edu';
                            _otpSent = false;
                            _generatedOtpPreview = null;
                            _signUpOtpController.clear();
                          });
                        },
                      );
                    },
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: AppTheme.bgCream,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Top Action Bar
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton.icon(
                        style: TextButton.styleFrom(
                          backgroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: BorderSide(color: Colors.grey.shade300)),
                          elevation: 1,
                        ),
                        icon: const Icon(Icons.dashboard_customize_outlined, size: 16, color: AppTheme.primaryNavy),
                        label: const Text('Audit Control', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryNavy)),
                        onPressed: () => Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const ControlPanelScreen()),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Clean Institutional Animated Logo & Monogram Header
                  const Center(
                    child: InstitutionalLogo(
                      size: 68,
                      animate: true,
                      variant: LogoVariant.classicNavyGold,
                      showText: true,
                      title: 'SRK CAMPUS',
                      subtitle: 'Unified Institutional Intelligence Portal',
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Tab Bar (Sign In / UID Sign Up)
                  Container(
                    height: 46,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(25),
                    ),
                    child: TabBar(
                      controller: _tabController,
                      indicatorSize: TabBarIndicatorSize.tab,
                      dividerColor: Colors.transparent,
                      indicator: BoxDecoration(
                        color: AppTheme.primaryNavy,
                        borderRadius: BorderRadius.circular(25),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryNavy.withOpacity(0.25),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      labelColor: Colors.white,
                      unselectedLabelColor: Colors.grey.shade700,
                      labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      tabs: const [
                        Tab(
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.lock_outline_rounded, size: 15),
                              SizedBox(width: 6),
                              Text('Sign In'),
                            ],
                          ),
                        ),
                        Tab(
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.how_to_reg_outlined, size: 15),
                              SizedBox(width: 6),
                              Text('Sign Up & OTP'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Tab View Content Card
                  AnimatedSize(
                    duration: const Duration(milliseconds: 200),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade200),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: _tabController.index == 0
                          ? _buildSignInForm(authState)
                          : _buildSignUpUidForm(authState),
                    ),
                  ),

                  // 1-Tap Demo Quick Selector (Footer)
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.verified_user_outlined, color: AppTheme.accentGold, size: 16),
                            const SizedBox(width: 6),
                            Text(
                              'Instant 1-Tap Role Demo Switcher',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.grey.shade800,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: [
                              _buildRoleChip('principal', 'Principal', Icons.shield_outlined, Colors.purple),
                              const SizedBox(width: 8),
                              _buildRoleChip('campus_head', 'Campus Head', Icons.account_balance_outlined, AppTheme.secondaryNavy),
                              const SizedBox(width: 8),
                              _buildRoleChip('teacher_nirali', 'Teacher Nirali', Icons.school_outlined, AppTheme.accentGold),
                              const SizedBox(width: 8),
                              _buildRoleChip('student_rahul', 'Student Rahul', Icons.person_outline, AppTheme.statusGreen),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSignInForm(AuthState authState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Institutional Login',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.primaryNavy),
        ),
        const SizedBox(height: 4),
        Text(
          'Sign in with your Campus UID (e.g. SRK-ADM-001) or Email.',
          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _signInIdentifierController,
          decoration: InputDecoration(
            labelText: 'Campus UID or Email',
            hintText: 'e.g. SRK-ADM-001 or nirdesh.buch@srk.edu',
            prefixIcon: const Icon(Icons.badge_outlined),
            filled: true,
            fillColor: AppTheme.bgCream,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        const SizedBox(height: 12),

        TextField(
          controller: _signInPasswordController,
          obscureText: _signInObscurePassword,
          decoration: InputDecoration(
            labelText: 'Password',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(_signInObscurePassword ? Icons.visibility_off : Icons.visibility, color: Colors.grey),
              onPressed: () => setState(() => _signInObscurePassword = !_signInObscurePassword),
            ),
            filled: true,
            fillColor: AppTheme.bgCream,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide.none,
            ),
          ),
        ),

        if (authState.errorMessage != null) ...[
          const SizedBox(height: 12),
          Text(
            authState.errorMessage!,
            style: const TextStyle(color: AppTheme.statusRed, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],

        const SizedBox(height: 18),
        SizedBox(
          height: 48,
          child: ElevatedButton(
            onPressed: authState.isLoading ? null : _onSignInSubmit,
            child: authState.isLoading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Sign In to Campus Portal'),
          ),
        ),
      ],
    );
  }

  Widget _buildSignUpUidForm(AuthState authState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'UID Activation & OTP Sign Up',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.primaryNavy),
        ),
        const SizedBox(height: 4),
        Text(
          'Select your pre-authorized Campus UID, verify mobile/email OTP, and set your password.',
          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
        ),
        const SizedBox(height: 16),

        // Step 1: UID Picker
        InkWell(
          onTap: _openUidPickerModal,
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: _selectedUidRecord == null ? AppTheme.bgCream : Colors.blue.shade50,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: _selectedUidRecord == null ? Colors.grey.shade300 : AppTheme.secondaryNavy,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.badge_rounded,
                  color: _selectedUidRecord == null ? Colors.grey : AppTheme.secondaryNavy,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _selectedUidRecord == null
                            ? 'Tap to Select Campus UID (30 UIDs)'
                            : '${_selectedUidRecord!['uid']} • ${_selectedUidRecord!['name']}',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: _selectedUidRecord == null ? Colors.grey.shade700 : AppTheme.primaryNavy,
                        ),
                      ),
                      if (_selectedUidRecord != null)
                        Text(
                          '${_selectedUidRecord!['role']} • ${_selectedUidRecord!['department']}',
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                        ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_drop_down, color: Colors.grey),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Email
        TextField(
          controller: _signUpEmailController,
          keyboardType: TextInputType.emailAddress,
          decoration: InputDecoration(
            labelText: 'Institutional Email',
            prefixIcon: const Icon(Icons.email_outlined),
            filled: true,
            fillColor: AppTheme.bgCream,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Phone & OTP Button
        Row(
          children: [
            Expanded(
              flex: 3,
              child: TextField(
                controller: _signUpPhoneController,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(
                  labelText: 'Phone Number',
                  prefixIcon: const Icon(Icons.phone_outlined),
                  filled: true,
                  fillColor: AppTheme.bgCream,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              flex: 2,
              child: SizedBox(
                height: 52,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _otpSent ? AppTheme.statusGreen : AppTheme.secondaryNavy,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: _isSendingOtp ? null : _onSendOtp,
                  child: _isSendingOtp
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(
                          _otpSent ? 'Resend' : 'Send OTP',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // 4-Digit OTP Field
        TextField(
          controller: _signUpOtpController,
          keyboardType: TextInputType.number,
          maxLength: 4,
          decoration: InputDecoration(
            counterText: '',
            labelText: '4-Digit Verification OTP',
            hintText: 'e.g. 4821',
            prefixIcon: const Icon(Icons.security_rounded),
            filled: true,
            fillColor: AppTheme.bgCream,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Set Password
        TextField(
          controller: _signUpPasswordController,
          obscureText: _signUpObscurePassword,
          decoration: InputDecoration(
            labelText: 'Create Password',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(_signUpObscurePassword ? Icons.visibility_off : Icons.visibility, color: Colors.grey),
              onPressed: () => setState(() => _signUpObscurePassword = !_signUpObscurePassword),
            ),
            filled: true,
            fillColor: AppTheme.bgCream,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide.none,
            ),
          ),
        ),

        if (authState.errorMessage != null) ...[
          const SizedBox(height: 10),
          Text(
            authState.errorMessage!,
            style: const TextStyle(color: AppTheme.statusRed, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],

        const SizedBox(height: 16),
        SizedBox(
          height: 48,
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.secondaryNavy),
            onPressed: authState.isLoading ? null : _onSignUpSubmit,
            child: authState.isLoading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Verify OTP & Activate Account'),
          ),
        ),
      ],
    );
  }

  Widget _buildRoleChip(String accountKey, String label, IconData icon, Color color) {
    return ActionChip(
      avatar: Icon(icon, size: 14, color: color),
      label: Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey.shade800)),
      backgroundColor: Colors.white,
      side: BorderSide(color: Colors.grey.shade300),
      elevation: 0.5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      onPressed: () => _onQuickLogin(accountKey),
    );
  }
}

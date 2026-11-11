import 'package:flutter/material.dart';
import '../services/teacher_api_service.dart';

class TeacherLoginScreen extends StatefulWidget {
  final VoidCallback onLoginSuccess;
  const TeacherLoginScreen({super.key, required this.onLoginSuccess});

  @override
  State<TeacherLoginScreen> createState() => _TeacherLoginScreenState();
}

class _TeacherLoginScreenState extends State<TeacherLoginScreen> {
  final _emailController = TextEditingController(text: 'nirali.thakkar@srk.edu');
  final _passwordController = TextEditingController(text: 'Faculty@123');
  bool _isLoading = false;

  void _handleLogin() async {
    setState(() => _isLoading = true);
    final success = await TeacherApiService().login(
      _emailController.text.trim(),
      _passwordController.text.trim(),
    );
    setState(() => _isLoading = false);

    if (success) {
      widget.onLoginSuccess();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Invalid credentials')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF00897B), Color(0xFF004D40)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Card(
                elevation: 8,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                child: Padding(
                  padding: const EdgeInsets.all(28.0),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Icon(Icons.co_present, size: 64, color: Color(0xFF00897B)),
                      const SizedBox(height: 12),
                      const Text(
                        'SRK Faculty Portal',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF00897B)),
                      ),
                      const Text(
                        'Physical Room Verification & Attendance',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 13, color: Colors.grey),
                      ),
                      const SizedBox(height: 28),

                      TextField(
                        controller: _emailController,
                        decoration: const InputDecoration(
                          labelText: 'Faculty Email',
                          prefixIcon: Icon(Icons.email_outlined),
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: const InputDecoration(
                          labelText: 'Password',
                          prefixIcon: Icon(Icons.lock_outline),
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 24),

                      ElevatedButton(
                        onPressed: _isLoading ? null : _handleLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF00897B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text('Login as Faculty', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(height: 16),

                      const Text('ONE-TAP REAL FACULTY LOGIN:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.grey)),
                      const SizedBox(height: 8),

                      OutlinedButton.icon(
                        onPressed: () {
                          _emailController.text = 'nirali.thakkar@srk.edu';
                          _passwordController.text = 'Faculty@123';
                          _handleLogin();
                        },
                        icon: const Icon(Icons.flash_on, size: 16),
                        label: const Text('Prof. Nirali Thakkar (NT)'),
                      ),
                      const SizedBox(height: 6),

                      OutlinedButton.icon(
                        onPressed: () {
                          _emailController.text = 'arjunsinh.vaghela@srk.edu';
                          _passwordController.text = 'Faculty@123';
                          _handleLogin();
                        },
                        icon: const Icon(Icons.flash_on, size: 16),
                        label: const Text('Prof. Arjunsinh Vaghela (AV)'),
                      ),
                      const SizedBox(height: 6),

                      OutlinedButton.icon(
                        onPressed: () {
                          _emailController.text = 'rishi.sonpar@srk.edu';
                          _passwordController.text = 'Faculty@123';
                          _handleLogin();
                        },
                        icon: const Icon(Icons.flash_on, size: 16),
                        label: const Text('Prof. Rishi Sonpar (RS - HOD BBA)'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

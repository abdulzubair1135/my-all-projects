import { userRepository } from '../repositories/user.repository.js';
import { authService } from '../services/auth.service.js';
import { AppError } from '../middleware/error.middleware.js';
import crypto from 'crypto';

export const authController = {
  async register(req, res, next) {
    try {
      const { full_name, email, phone, password } = req.body;

      // 1. Check if email exists
      const existingEmail = await userRepository.findByEmail(email);
      if (existingEmail) {
        throw new AppError('Email address is already registered.', 409);
      }

      // 2. Check if phone exists
      const existingPhone = await userRepository.findByPhone(phone);
      if (existingPhone) {
        throw new AppError('Phone number is already registered.', 409);
      }

      // 3. Hash password
      const password_hash = await authService.hashPassword(password);
      
      // 4. Create user
      const uuid = crypto.randomUUID();
      const userId = await userRepository.create({
        uuid,
        full_name,
        email,
        phone,
        password_hash,
        role: 'user'
      });

      const user = await userRepository.findById(userId);

      // 5. Generate tokens
      const accessToken = authService.generateAccessToken(user);
      const refreshToken = authService.generateRefreshToken(user);

      // 6. Save refresh token
      await authService.saveRefreshToken(user.id, refreshToken);

      // Remove password hash from response
      delete user.password_hash;

      res.status(211).json({ // Use 201 Created but let's use 200/201
        success: true,
        message: 'User registered successfully',
        data: {
          user,
          tokens: {
            accessToken,
            refreshToken
          }
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async login(req, res, next) {
    try {
      const { email, password } = req.body;

      // 1. Find user
      const user = await userRepository.findByEmail(email);
      if (!user) {
        throw new AppError('Invalid email or password.', 401);
      }

      // 2. Verify status
      if (user.status === 'blocked') {
        throw new AppError('Your account has been blocked.', 403);
      }
      if (user.status === 'suspended') {
        throw new AppError('Your account is currently suspended.', 403);
      }

      // 3. Verify password
      const isPasswordValid = await authService.verifyPassword(password, user.password_hash);
      if (!isPasswordValid) {
        throw new AppError('Invalid email or password.', 401);
      }

      // 4. Update last login
      await userRepository.updateLastLogin(user.id);

      // 5. Generate tokens
      const accessToken = authService.generateAccessToken(user);
      const refreshToken = authService.generateRefreshToken(user);

      // 6. Save refresh token
      await authService.saveRefreshToken(user.id, refreshToken);

      // Clean password
      delete user.password_hash;

      res.status(200).json({
        success: true,
        message: 'Login successful',
        data: {
          user,
          tokens: {
            accessToken,
            refreshToken
          }
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async refresh(req, res, next) {
    try {
      const { refreshToken } = req.body;
      if (!refreshToken) {
        throw new AppError('Refresh token is required.', 400);
      }

      const rotated = await authService.rotateRefreshToken(refreshToken);
      
      delete rotated.user.password_hash;

      res.status(200).json({
        success: true,
        message: 'Tokens rotated successfully',
        data: {
          user: rotated.user,
          tokens: {
            accessToken: rotated.accessToken,
            refreshToken: rotated.refreshToken
          }
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async logout(req, res, next) {
    try {
      const { refreshToken } = req.body;
      if (refreshToken) {
        await authService.revokeRefreshToken(refreshToken);
      }

      res.status(200).json({
        success: true,
        message: 'Logged out successfully'
      });
    } catch (err) {
      next(err);
    }
  },

  async getMe(req, res, next) {
    try {
      // req.user is set by the protect middleware
      const user = await userRepository.findById(req.user.id);
      delete user.password_hash;

      res.status(200).json({
        success: true,
        message: 'User profile retrieved successfully',
        data: user
      });
    } catch (err) {
      next(err);
    }
  },

  async forgotPassword(req, res, next) {
    try {
      const { email } = req.body;
      const user = await userRepository.findByEmail(email);
      
      if (user) {
        const { emailService } = await import('../services/email.service.js');
        const resetToken = crypto.randomBytes(20).toString('hex');
        const resetLink = `http://localhost:5000/api/v1/auth/reset-password?token=${resetToken}&email=${encodeURIComponent(user.email)}`;
        
        emailService.sendPasswordResetEmail(user.email, user.full_name, resetLink)
          .catch(err => console.error('Failed to send reset email:', err.message));
      }

      res.status(200).json({
        success: true,
        message: 'If the email exists, a password reset link has been sent.'
      });
    } catch (err) {
      next(err);
    }
  },

  async resetPassword(req, res, next) {
    try {
      const { email, newPassword } = req.body;
      const user = await userRepository.findByEmail(email);
      if (!user) {
        throw new AppError('User not found.', 404);
      }

      const password_hash = await authService.hashPassword(newPassword);
      await userRepository.update(user.id, { password_hash });
      
      // Revoke all tokens for safety
      await authService.revokeAllUserTokens(user.id);

      res.status(200).json({
        success: true,
        message: 'Password reset successfully. Please login with your new password.'
      });
    } catch (err) {
      next(err);
    }
  }
};

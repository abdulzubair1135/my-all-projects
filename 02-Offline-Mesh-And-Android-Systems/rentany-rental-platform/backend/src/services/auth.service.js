import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { env } from '../config/env.js';
import pool from '../config/database.js';
import { AppError } from '../middleware/error.middleware.js';

export const authService = {
  // Password hashing
  async hashPassword(password) {
    return await bcrypt.hash(password, 10);
  },

  async verifyPassword(password, hashedPassword) {
    return await bcrypt.compare(password, hashedPassword);
  },

  // JWT Token creation
  generateAccessToken(user) {
    return jwt.sign(
      { id: user.id, uuid: user.uuid, email: user.email, role: user.role },
      env.JWT_ACCESS_SECRET,
      { expiresIn: env.JWT_ACCESS_EXPIRES_IN }
    );
  },

  generateRefreshToken(user) {
    return jwt.sign(
      { id: user.id },
      env.JWT_REFRESH_SECRET,
      { expiresIn: env.JWT_REFRESH_EXPIRES_IN }
    );
  },

  // Save refresh token to db
  async saveRefreshToken(userId, token) {
    const decoded = jwt.decode(token);
    // Convert epoch seconds to MySQL datetime string
    const expiresAt = new Date(decoded.exp * 1000).toISOString().slice(0, 19).replace('T', ' ');

    await pool.query(
      'INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
      [userId, token, expiresAt]
    );
  },

  // Refresh token rotation (returns new access and refresh token)
  async rotateRefreshToken(oldToken) {
    try {
      // 1. Verify old token signature
      const decoded = jwt.verify(oldToken, env.JWT_REFRESH_SECRET);
      
      // 2. Check if token exists in database (has it been revoked or used?)
      const [rows] = await pool.query(
        'SELECT id, user_id FROM refresh_tokens WHERE token = ? AND expires_at > NOW()',
        [oldToken]
      );

      if (rows.length === 0) {
        // Potential reuse/hack: delete all tokens for security if a token is reused
        await pool.query('DELETE FROM refresh_tokens WHERE user_id = ?', [decoded.id]);
        throw new AppError('Invalid or expired refresh token. Please log in again.', 401);
      }

      const userId = decoded.id;

      // 3. Get user details
      const [userRows] = await pool.query(
        'SELECT id, uuid, email, role, status FROM users WHERE id = ?',
        [userId]
      );
      if (userRows.length === 0 || userRows[0].status !== 'active') {
        throw new AppError('User is no longer active.', 403);
      }

      const user = userRows[0];

      // 4. Generate new tokens
      const newAccessToken = this.generateAccessToken(user);
      const newRefreshToken = this.generateRefreshToken(user);

      // 5. Rotate tokens: delete old, save new
      const connection = await pool.getConnection();
      try {
        await connection.beginTransaction();
        
        await connection.query('DELETE FROM refresh_tokens WHERE token = ?', [oldToken]);
        
        const newDecoded = jwt.decode(newRefreshToken);
        const expiresAt = new Date(newDecoded.exp * 1000).toISOString().slice(0, 19).replace('T', ' ');
        
        await connection.query(
          'INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
          [userId, newRefreshToken, expiresAt]
        );
        
        await connection.commit();
      } catch (err) {
        await connection.rollback();
        throw err;
      } finally {
        connection.release();
      }

      return {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
        user
      };
    } catch (err) {
      if (err.name === 'JsonWebTokenError' || err.name === 'TokenExpiredError') {
        throw new AppError('Invalid or expired refresh token. Please log in again.', 401);
      }
      throw err;
    }
  },

  // Revoke token (logout)
  async revokeRefreshToken(token) {
    const [res] = await pool.query('DELETE FROM refresh_tokens WHERE token = ?', [token]);
    return res.affectedRows > 0;
  },

  async revokeAllUserTokens(userId) {
    await pool.query('DELETE FROM refresh_tokens WHERE user_id = ?', [userId]);
  }
};

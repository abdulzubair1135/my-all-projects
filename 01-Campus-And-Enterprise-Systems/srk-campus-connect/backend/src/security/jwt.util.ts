import jwt from 'jsonwebtoken';
import mongoose from 'mongoose';
import { envConfig } from '../config/env.config';
import { UserRole } from '../constants/enums';

export interface JwtPayload {
  sub: string;
  role: UserRole;
  email: string;
  departmentId?: string;
  deviceId?: string;
}

export class JwtUtil {
  static generateAccessToken(payload: JwtPayload): string {
    return jwt.sign(payload, envConfig.jwtSecret, {
      expiresIn: envConfig.jwtExpiresIn as jwt.SignOptions['expiresIn']
    });
  }

  static generateRefreshToken(payload: JwtPayload): string {
    return jwt.sign(payload, envConfig.jwtRefreshSecret, {
      expiresIn: envConfig.jwtRefreshExpiresIn as jwt.SignOptions['expiresIn']
    });
  }

  static verifyAccessToken(token: string): JwtPayload {
    return jwt.verify(token, envConfig.jwtSecret) as JwtPayload;
  }

  static verifyRefreshToken(token: string): JwtPayload {
    return jwt.verify(token, envConfig.jwtRefreshSecret) as JwtPayload;
  }
}

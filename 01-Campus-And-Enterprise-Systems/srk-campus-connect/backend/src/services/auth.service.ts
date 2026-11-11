import bcrypt from 'bcryptjs';
import { User, IUser } from '../models/User';
import { Student } from '../models/Student';
import { Faculty } from '../models/Faculty';
import { Department } from '../models/Department';
import { JwtUtil, JwtPayload } from '../security/jwt.util';
import { UserRole } from '../constants/enums';
import { CAMPUS_AUTHORIZED_UIDS, CampusUIDRecord } from '../constants/uids';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginResult {
  user: {
    id: string;
    uid?: string;
    name: string;
    email: string;
    role: UserRole;
    departmentId?: string;
    designation?: string;
    cabinNumber?: string;
    rollNumber?: string;
    details?: any;
  };
  tokens: AuthTokens;
}

export class AuthService {
  static getAuthorizedUids(): CampusUIDRecord[] {
    return CAMPUS_AUTHORIZED_UIDS;
  }

  static generateOtp(identifier: string): string {
    // Deterministic or time-based mock OTP for development and testing
    return '4821';
  }

  static async signupWithUid(params: {
    uid: string;
    email: string;
    phone?: string;
    password: string;
    otp: string;
  }): Promise<LoginResult> {
    const { uid, email, phone, password, otp } = params;

    // Verify OTP
    if (otp !== '4821' && otp !== '1234') {
      throw new Error('Invalid verification OTP');
    }

    // Verify UID from authorized list
    const uidRecord = CAMPUS_AUTHORIZED_UIDS.find(
      u => u.uid.toUpperCase() === uid.trim().toUpperCase()
    );

    if (!uidRecord) {
      throw new Error('Unauthorized Campus UID. Please choose from official SRK roster.');
    }

    // Find or create department
    let department = await Department.findOne({ code: 'BCA' });
    if (!department) {
      department = await Department.findOne();
    }

    let user: any = await User.findOne({
      $or: [
        { uid: uidRecord.uid },
        { email: email.toLowerCase().trim() }
      ]
    }).select('+passwordHash');

    if (!user) {
      user = new User({
        uid: uidRecord.uid,
        name: uidRecord.name,
        email: email.toLowerCase().trim(),
        phone: phone || '9876543210',
        passwordHash: password, // Pre-save hook hashes it
        role: uidRecord.role as UserRole,
        departmentId: department?._id,
        designation: uidRecord.designation,
        cabinNumber: uidRecord.cabinNumber,
        rollNumber: uidRecord.rollNumber,
        isActive: true
      });
      await user.save();
    } else {
      user.uid = uidRecord.uid;
      user.name = uidRecord.name;
      user.role = uidRecord.role as UserRole;
      user.designation = uidRecord.designation;
      user.cabinNumber = uidRecord.cabinNumber;
      user.rollNumber = uidRecord.rollNumber;
      user.passwordHash = password; // Pre-save hook will hash
      user.isActive = true;
      await user.save();
    }

    return this.login(user.email, password);
  }

  static async login(identifier: string, candidatePass: string, deviceId?: string): Promise<LoginResult> {
    const idClean = identifier.trim();
    const query = idClean.includes('@')
      ? { email: idClean.toLowerCase() }
      : {
          $or: [
            { uid: idClean.toUpperCase() },
            { email: idClean.toLowerCase() }
          ]
        };

    let user: any = await User.findOne(query).select('+passwordHash +isActive');

    // If not in DB yet but in authorized UIDs, auto-create
    if (!user && !idClean.includes('@')) {
      const uidMatch = CAMPUS_AUTHORIZED_UIDS.find(u => u.uid.toUpperCase() === idClean.toUpperCase());
      if (uidMatch) {
        user = (await User.findOne({ email: uidMatch.defaultEmail.toLowerCase() }).select('+passwordHash +isActive')) as any;
        if (user) {
          user.uid = uidMatch.uid;
          await user.save();
        }
      }
    }

    if (!user) {
      throw new Error('Invalid UID, email or password');
    }

    if (!user.isActive) {
      throw new Error('Account has been deactivated. Please contact campus administrator.');
    }

    const isMatch = await user.comparePassword(candidatePass);
    if (!isMatch) {
      throw new Error('Invalid UID, email or password');
    }

    const payload: JwtPayload = {
      sub: user._id.toString(),
      role: user.role,
      email: user.email,
      departmentId: user.departmentId?.toString(),
      deviceId
    };

    const accessToken = JwtUtil.generateAccessToken(payload);
    const refreshToken = JwtUtil.generateRefreshToken(payload);

    const salt = await bcrypt.genSalt(10);
    user.refreshTokenHash = await bcrypt.hash(refreshToken, salt);
    await user.save();

    let details: any = null;
    if (user.role === UserRole.STUDENT) {
      details = await Student.findOne({ userId: user._id }).populate('departmentId');
    } else if (user.role === UserRole.FACULTY) {
      details = await Faculty.findOne({ userId: user._id }).populate('departmentId subjects');
    }

    return {
      user: {
        id: user._id.toString(),
        uid: user.uid,
        name: user.name,
        email: user.email,
        role: user.role,
        departmentId: user.departmentId?.toString(),
        designation: user.designation,
        cabinNumber: user.cabinNumber,
        rollNumber: user.rollNumber,
        details
      },
      tokens: {
        accessToken,
        refreshToken
      }
    };
  }

  static async refreshToken(oldRefreshToken: string): Promise<AuthTokens> {
    let payload: JwtPayload;
    try {
      payload = JwtUtil.verifyRefreshToken(oldRefreshToken);
    } catch (err) {
      throw new Error('Invalid or expired refresh token');
    }

    const user = await User.findById(payload.sub).select('+refreshTokenHash +isActive');
    if (!user || !user.isActive || !user.refreshTokenHash) {
      throw new Error('Invalid session or inactive user');
    }

    const isTokenMatch = await bcrypt.compare(oldRefreshToken, user.refreshTokenHash);
    if (!isTokenMatch) {
      user.refreshTokenHash = undefined;
      await user.save();
      throw new Error('Token reuse detected. Session invalidated for security.');
    }

    const newPayload: JwtPayload = {
      sub: user._id.toString(),
      role: user.role,
      email: user.email,
      departmentId: user.departmentId?.toString(),
      deviceId: payload.deviceId
    };

    const newAccessToken = JwtUtil.generateAccessToken(newPayload);
    const newRefreshToken = JwtUtil.generateRefreshToken(newPayload);

    const salt = await bcrypt.genSalt(10);
    user.refreshTokenHash = await bcrypt.hash(newRefreshToken, salt);
    await user.save();

    return {
      accessToken: newAccessToken,
      refreshToken: newRefreshToken
    };
  }

  static async logout(userId: string): Promise<void> {
    await User.findByIdAndUpdate(userId, { $unset: { refreshTokenHash: 1 } });
  }
}

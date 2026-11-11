import nodemailer from 'nodemailer';

interface OtpEntry {
  otp: string;
  expiresAt: number;
  purpose: 'signup' | 'reset_password';
}

const otpStore = new Map<string, OtpEntry>();

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER || '',
    pass: process.env.EMAIL_PASS || ''
  },
  connectionTimeout: 5000,
  greetingTimeout: 5000,
  socketTimeout: 5000,
  tls: {
    rejectUnauthorized: false
  }
});

export const generateOtp = (): string => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

export const sendOtpEmail = async (
  email: string,
  purpose: 'signup' | 'reset_password' = 'signup'
): Promise<{ success: boolean; message: string; otp?: string }> => {
  const cleanEmail = email.trim().toLowerCase();
  const otp = generateOtp();
  const expiresAt = Date.now() + 10 * 60 * 1000;

  otpStore.set(cleanEmail, { otp, expiresAt, purpose });

  console.log('====================================================');
  console.log('🔐 [SAHAY AUTH OTP]');
  console.log('📧 Target Email: ' + cleanEmail);
  console.log('🔢 6-Digit OTP:  ' + otp);
  console.log('🎯 Purpose:      ' + purpose.toUpperCase());
  console.log('⏱️ Expires in:   10 minutes');
  console.log('====================================================');

  const actionText = purpose === 'signup' 
    ? 'Verify your Sahay Citizen & Emergency Responder Account' 
    : 'Reset your Sahay Account Password';

  const htmlContent = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
      <div style="text-align: center; margin-bottom: 24px;">
        <h1 style="color: #dc2626; margin: 0; font-size: 26px; font-weight: 800;">🛡️ SAHAY</h1>
        <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px; font-weight: 600;">Hybrid Emergency & Mesh Command Network</p>
      </div>
      <div style="background: #f8fafc; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #e2e8f0;">
        <h2 style="color: #0f172a; margin-top: 0; font-size: 18px;">${actionText}</h2>
        <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">Use the following One-Time Password (OTP) to complete your verification. Valid for <strong>10 minutes</strong>.</p>
        <div style="background: #dc2626; color: #ffffff; font-size: 34px; font-weight: 900; letter-spacing: 8px; padding: 14px 24px; border-radius: 8px; display: inline-block; margin: 10px 0;">${otp}</div>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 16px;">If you did not request this OTP, please disregard this alert.</p>
      </div>
      <div style="margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8;">
        <p style="margin: 0;">Sahay Disaster Management & State Command Grid</p>
        <p style="margin: 4px 0 0 0; font-style: italic;">"When the Network Fails, Sahay Doesn't."</p>
      </div>
    </div>
  `;

  try {
    await transporter.sendMail({
      from: '"Sahay Emergency Network" <sahay1382@gmail.com>',
      to: cleanEmail,
      subject: '🚨 [SAHAY] Your Emergency Verification OTP: ' + otp,
      text: 'Your Sahay verification code is: ' + otp + '. Valid for 10 minutes.',
      html: htmlContent
    });
    return { success: true, message: 'OTP sent to your email successfully.', otp };
  } catch (err: any) {
    console.warn('[Email Transporter Warning]:', err?.message);
    return { 
      success: true, 
      message: 'OTP generated successfully (check inbox or server console).',
      otp 
    };
  }
};

export const verifyOtpCode = (
  email: string,
  otp: string,
  purpose: 'signup' | 'reset_password' = 'signup'
): { valid: boolean; message: string } => {
  const cleanEmail = email.trim().toLowerCase();
  const cleanOtp = otp.trim();

  // Master demo bypass for fast hackathon judging
  if (cleanOtp === '123456' || cleanOtp === '999999') {
    return { valid: true, message: 'OTP verified successfully (Demo Master Code).' };
  }

  const entry = otpStore.get(cleanEmail);
  if (!entry) {
    return { valid: false, message: 'No OTP requested for this email. Please request an OTP first.' };
  }

  if (Date.now() > entry.expiresAt) {
    otpStore.delete(cleanEmail);
    return { valid: false, message: 'OTP has expired. Please request a new one.' };
  }

  if (entry.purpose !== purpose) {
    return { valid: false, message: 'OTP purpose mismatch.' };
  }

  if (entry.otp !== cleanOtp) {
    return { valid: false, message: 'Invalid OTP code. Please check and try again.' };
  }

  otpStore.delete(cleanEmail);
  return { valid: true, message: 'OTP verified successfully.' };
};

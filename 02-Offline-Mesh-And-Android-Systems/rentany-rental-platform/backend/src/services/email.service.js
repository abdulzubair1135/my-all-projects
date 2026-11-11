import { Resend } from 'resend';
import { env } from '../config/env.js';

// Initialize Resend client if API key is present
const resend = env.RESEND_API_KEY ? new Resend(env.RESEND_API_KEY) : null;

export const emailService = {
  /**
   * Helper to send an HTML email using Resend
   */
  async sendEmail({ to, subject, html }) {
    if (!resend) {
      console.log(`[Email Mock Service] Email simulated:`);
      console.log(`  To: ${to}`);
      console.log(`  Subject: ${subject}`);
      return { success: true, message: 'Resend API key missing, logged to console.' };
    }

    try {
      const data = await resend.emails.send({
        from: env.RESEND_FROM_EMAIL || 'onboarding@resend.dev',
        to,
        subject,
        html
      });
      console.log(`[Email Sent] Resend ID: ${data.id} to ${to}`);
      return { success: true, data };
    } catch (err) {
      console.error('[Resend Email Error]:', err.message);
      return { success: false, error: err.message };
    }
  },

  /**
   * Send password reset request email
   */
  async sendPasswordResetEmail(email, name, link) {
    const html = `
      <div style="font-family: sans-serif; padding: 20px; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">RentAny Password Reset</h2>
        <p>Hi ${name},</p>
        <p>We received a request to reset your password for your RentAny account. Click the button below to choose a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
          <a href="${link}" style="display: inline-block; padding: 12px 24px; background-color: #3498db; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
        </div>
        <p style="color: #7f8c8d; font-size: 12px;">If you did not request a password reset, please ignore this email. This link will expire shortly.</p>
        <hr style="border: 0; border-top: 1px solid #eee;" />
        <p style="font-size: 12px; color: #95a5a6;">Best regards,<br />The RentAny Operations Team</p>
      </div>
    `;
    return await this.sendEmail({ to: email, subject: 'RentAny - Password Reset Request', html });
  },

  /**
   * Send booking confirmation receipt email to Renter
   */
  async sendBookingConfirmationEmail(email, name, bookingDetails) {
    const html = `
      <div style="font-family: sans-serif; padding: 20px; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #27ae60; border-bottom: 2px solid #2ecc71; padding-bottom: 10px;">Booking Confirmed!</h2>
        <p>Hi ${name},</p>
        <p>Good news! Your booking request for <strong>${bookingDetails.listingTitle}</strong> has been confirmed by the owner.</p>
        <h3 style="color: #2c3e50;">Booking Receipt Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <tr style="background-color: #f9f9f9;">
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Details</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Value</th>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Rental Period</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${bookingDetails.startDate} to ${bookingDetails.endDate} (${bookingDetails.rentalDays} days)</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Price per Day</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">INR ${bookingDetails.pricePerDay}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Refundable Deposit</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">INR ${bookingDetails.depositAmount}</td>
          </tr>
          <tr style="font-weight: bold; background-color: #f1f8e9;">
            <td style="padding: 10px; border: 1px solid #ddd; color: #2e7d32;">Total Paid</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #2e7d32;">INR ${bookingDetails.totalPrice}</td>
          </tr>
        </table>
        <p>Please log in to the RentAny Android app to contact the owner and arrange the pickup handover.</p>
        <hr style="border: 0; border-top: 1px solid #eee;" />
        <p style="font-size: 12px; color: #95a5a6;">Best regards,<br />The RentAny Billing Team</p>
      </div>
    `;
    return await this.sendEmail({ to: email, subject: 'RentAny - Booking Receipt Confirmation', html });
  },

  /**
   * Send booking status transition updates
   */
  async sendBookingStatusEmail(email, name, listingTitle, status) {
    const html = `
      <div style="font-family: sans-serif; padding: 20px; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #2980b9; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Booking Status Updated</h2>
        <p>Hi ${name},</p>
        <p>This is to inform you that your booking status for <strong>${listingTitle}</strong> has been updated to: <span style="display: inline-block; padding: 4px 8px; background-color: #e8f4fd; color: #2980b9; border-radius: 4px; font-weight: bold;">${status.toUpperCase()}</span>.</p>
        <p>Log in to your RentAny account in our mobile application to view details or proceed with your checkout timeline.</p>
        <hr style="border: 0; border-top: 1px solid #eee;" />
        <p style="font-size: 12px; color: #95a5a6;">Best regards,<br />The RentAny Operations Team</p>
      </div>
    `;
    return await this.sendEmail({ to: email, subject: `RentAny - Booking Status Update: ${status}`, html });
  }
};

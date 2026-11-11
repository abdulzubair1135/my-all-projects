import { Router, Request, Response } from 'express';
import { CitizenReport } from '../models/CitizenReport.js';
import { broadcastEvent } from '../sockets/socket.js';
import { requireAuth, requireRole, AuthRequest } from '../middleware/auth.js';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const { status, type } = req.query;
    const filter: any = {};
    if (status) filter.verificationStatus = status;
    if (type) filter.type = type;

    const reports = await CitizenReport.find(filter).sort({ createdAt: -1 });
    res.json({ success: true, data: reports });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.post('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const { type, description, latitude, longitude, mediaUrl, images, addressText, userName, userPhone } = req.body;
    if (!type || !description || latitude === undefined || longitude === undefined) {
      res.status(400).json({ success: false, error: { code: 'VALIDATION_ERROR', message: 'Type, description and location coordinates are required.' } });
      return;
    }

    // Map common frontend type strings to model enum
    const typeUpper = String(type).toUpperCase().replace(/\s+/g, '_');
    const validEnums = ['FLOOD', 'FIRE', 'BLOCKED_ROAD', 'COLLAPSED_BUILDING', 'MISSING_PERSON', 'DANGEROUS_AREA', 'DAMAGED_INFRASTRUCTURE', 'MEDICAL_EMERGENCY', 'OTHER'];
    const normalizedType = validEnums.includes(typeUpper) ? typeUpper : 'OTHER';

    // Optional user from JWT token if passed
    let authUser: any = null;
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      try {
        const token = authHeader.split(' ')[1];
        const jwt = await import('jsonwebtoken');
        const secret = process.env.JWT_SECRET || 'aapdasetu_jwt_secret_change_in_production_2026_secure';
        authUser = jwt.default.verify(token, secret);
      } catch {
        // Continue as emergency guest
      }
    }

    const rawImages = Array.isArray(images) ? images : (mediaUrl ? [mediaUrl] : []);
    const processedImages: string[] = [];

    for (const img of rawImages) {
      if (typeof img === 'string' && img.startsWith('data:image')) {
        try {
          const { v2: cloudinary } = await import('cloudinary');
          if (process.env.CLOUDINARY_CLOUD_NAME) {
            cloudinary.config({
              cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
              api_key: process.env.CLOUDINARY_API_KEY,
              api_secret: process.env.CLOUDINARY_API_SECRET
            });
            const uploadRes = await cloudinary.uploader.upload(img, {
              folder: 'sahay/incidents',
              resource_type: 'image'
            });
            processedImages.push(uploadRes.secure_url);
            console.log('[Cloudinary] 📸 Report image stored successfully:', uploadRes.secure_url);
          } else {
            processedImages.push(img);
          }
        } catch (uploadErr) {
          console.warn('[Cloudinary Warning] Upload failed, falling back:', (uploadErr as Error).message);
          processedImages.push(img);
        }
      } else if (img) {
        processedImages.push(img);
      }
    }

    const report = await CitizenReport.create({
      userId: authUser?.id,
      userName: authUser?.name || userName || 'Citizen Reporter',
      userPhone: authUser?.phone || userPhone || '',
      type: normalizedType,
      description,
      location: {
        type: 'Point',
        coordinates: [Number(longitude), Number(latitude)]
      },
      addressText: addressText || '',
      images: processedImages,
      mediaUrl: processedImages[0] || '',
      verificationStatus: 'SUBMITTED'
    });

    broadcastEvent('report:new', report);
    broadcastEvent('report:new', report, 'gov');
    broadcastEvent('report:new', report, 'admin');
    broadcastEvent('report:new', report, 'ngo');

    res.status(201).json({ success: true, message: 'Citizen hazard report submitted successfully.', data: report });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

router.patch('/:id/verify', requireAuth, requireRole(['GOVERNMENT', 'ADMIN', 'SUPER_ADMIN']), async (req: AuthRequest, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { status } = req.body; // VERIFIED, REJECTED, ACTION_TAKEN

    const report = await CitizenReport.findById(id);
    if (!report) {
      res.status(404).json({ success: false, error: { code: 'NOT_FOUND', message: 'Report not found.' } });
      return;
    }

    report.verificationStatus = status || 'VERIFIED';
    report.verifiedBy = req.user?._id;
    report.verifiedAt = new Date();
    await report.save();

    broadcastEvent('report:verified', report);
    res.json({ success: true, message: `Report marked as ${report.verificationStatus}.`, data: report });
  } catch (error) {
    res.status(500).json({ success: false, error: { code: 'SERVER_ERROR', message: (error as Error).message } });
  }
});

export default router;

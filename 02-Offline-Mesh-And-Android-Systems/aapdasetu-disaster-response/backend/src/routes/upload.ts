import { Router, Request, Response } from 'express';
import multer from 'multer';
import { v2 as cloudinary } from 'cloudinary';
import fs from 'fs';
import path from 'path';

const router = Router();

const isCloudinaryConfigured = !!(
  process.env.CLOUDINARY_CLOUD_NAME &&
  process.env.CLOUDINARY_API_KEY &&
  process.env.CLOUDINARY_API_SECRET
);

if (isCloudinaryConfigured) {
  cloudinary.config({
    cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
    api_key: process.env.CLOUDINARY_API_KEY,
    api_secret: process.env.CLOUDINARY_API_SECRET
  });
  console.log('✅ [Cloudinary] Initialized with Cloud Name:', process.env.CLOUDINARY_CLOUD_NAME);
} else {
  console.warn('⚠️ [Cloudinary] Credentials not set in .env. Will use local uploads fallback directory.');
}

const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }
});

router.post('/', upload.single('image'), async (req: Request, res: Response): Promise<void> => {
  try {
    if (!req.file) {
      res.status(400).json({
        success: false,
        error: { code: 'NO_FILE', message: 'No image file was provided in the request.' }
      });
      return;
    }

    if (isCloudinaryConfigured) {
      const uploadPromise = new Promise<{ secure_url: string; public_id: string }>((resolve, reject) => {
        const uploadStream = cloudinary.uploader.upload_stream(
          {
            folder: 'aapdasetu/incidents',
            resource_type: 'image'
          },
          (error, result) => {
            if (error || !result) {
              return reject(error || new Error('Upload failed'));
            }
            resolve({
              secure_url: result.secure_url,
              public_id: result.public_id
            });
          }
        );
        uploadStream.end(req.file!.buffer);
      });

      const uploadResult = await uploadPromise;
      res.json({
        success: true,
        message: 'Image successfully uploaded to Cloudinary.',
        data: {
          url: uploadResult.secure_url,
          secure_url: uploadResult.secure_url,
          public_id: uploadResult.public_id,
          provider: 'cloudinary'
        }
      });
      return;
    }

    const uploadsDir = path.join(process.cwd(), 'uploads');
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
    }

    const ext = path.extname(req.file.originalname) || '.jpg';
    const filename = `incident_${Date.now()}_${Math.random().toString(36).substring(7)}${ext}`;
    const filePath = path.join(uploadsDir, filename);

    fs.writeFileSync(filePath, req.file.buffer);

    const protocol = req.protocol || 'http';
    const hostHeader = req.get('host') || 'localhost:5000';
    const publicUrl = `${protocol}://${hostHeader}/uploads/${filename}`;

    res.json({
      success: true,
      message: 'Image saved (Cloudinary fallback mode). Add Cloudinary credentials to .env for cloud storage.',
      data: {
        url: publicUrl,
        secure_url: publicUrl,
        filename,
        provider: 'local_fallback'
      }
    });
  } catch (error) {
    console.error('[Upload Error]:', error);
    res.status(500).json({
      success: false,
      error: { code: 'UPLOAD_FAILED', message: (error as Error).message }
    });
  }
});

// Direct base64 Cloudinary upload endpoint for mobile app & citizen report pictures
router.post('/base64', async (req: Request, res: Response): Promise<void> => {
  try {
    const { image, folder = 'incidents' } = req.body;
    if (!image) {
      res.status(400).json({ success: false, error: { message: 'Image base64 string is required' } });
      return;
    }

    const uploadRes = await cloudinary.uploader.upload(image, {
      folder: `sahay/${folder}`,
      resource_type: 'image'
    });

    res.json({
      success: true,
      message: 'Image uploaded to Cloudinary successfully.',
      data: {
        url: uploadRes.secure_url,
        secure_url: uploadRes.secure_url,
        public_id: uploadRes.public_id,
        provider: 'cloudinary'
      }
    });
  } catch (error: any) {
    console.error('[Cloudinary Base64 Upload Error]:', error);
    res.status(500).json({
      success: false,
      error: { code: 'CLOUDINARY_UPLOAD_FAILED', message: error?.message || 'Upload failed' }
    });
  }
});

export default router;

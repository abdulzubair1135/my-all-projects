import { v2 as cloudinary } from 'cloudinary';

// Configure Cloudinary with user credentials
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME || 'qnkopie9',
  api_key: process.env.CLOUDINARY_API_KEY || '166159337622438',
  api_secret: process.env.CLOUDINARY_API_SECRET || 'xB6brChZUAF4UAQM5ah4eiSq-OA',
  secure: true
});

export const uploadToCloudinary = async (
  fileDataOrBase64: string,
  folder: 'incidents' | 'profiles' | 'shelters' = 'incidents'
): Promise<{ url: string; publicId: string }> => {
  try {
    const result = await cloudinary.uploader.upload(fileDataOrBase64, {
      folder: `sahay/${folder}`,
      resource_type: 'auto',
      transformation: [
        { quality: 'auto:good' },
        { fetch_format: 'auto' }
      ]
    });

    return {
      url: result.secure_url,
      publicId: result.public_id
    };
  } catch (error) {
    console.error('[Cloudinary Upload Error]:', error);
    throw error;
  }
};

export default cloudinary;

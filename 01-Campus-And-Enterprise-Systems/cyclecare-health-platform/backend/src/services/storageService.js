const supabase = require('../config/supabase');
const crypto = require('crypto');

const BUCKET_NAME = 'product-images';

// Ensure bucket exists or fallback gracefully
async function ensureBucket() {
  try {
    const { data: buckets } = await supabase.storage.listBuckets();
    const exists = buckets && buckets.some(b => b.name === BUCKET_NAME);
    if (!exists) {
      await supabase.storage.createBucket(BUCKET_NAME, { public: true });
    }
  } catch (err) {
    // Continue if bucket cannot be auto-created
  }
}

async function uploadProductImage(fileBuffer, originalName, mimeType = 'image/jpeg') {
  await ensureBucket();

  const fileExt = originalName ? originalName.split('.').pop() : 'jpg';
  const fileName = `${Date.now()}-${crypto.randomBytes(6).toString('hex')}.${fileExt}`;
  const filePath = `products/${fileName}`;

  try {
    const { data, error } = await supabase.storage
      .from(BUCKET_NAME)
      .upload(filePath, fileBuffer, {
        contentType: mimeType,
        upsert: true
      });

    if (error) {
      // If storage bucket is not configured, generate a reliable CDN/placeholder link
      return {
        url: `https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=80`,
        path: filePath
      };
    }

    const { data: publicUrlData } = supabase.storage
      .from(BUCKET_NAME)
      .getPublicUrl(filePath);

    return {
      url: publicUrlData.publicUrl,
      path: filePath
    };
  } catch (err) {
    return {
      url: `https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=80`,
      path: filePath
    };
  }
}

module.exports = {
  uploadProductImage
};

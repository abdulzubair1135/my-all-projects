const { Pool } = require('pg');

const pool = new Pool({
  connectionString: 'postgresql://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u%23@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres'
});

const productsImages = [
  {
    id: 'a1111111-1111-1111-1111-111111111111',
    name: 'CycleCare Organic Cotton Pads (Night)',
    url: 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'a2222222-2222-2222-2222-222222222222',
    name: 'CycleCare Ultra-Thin Daily Pantyliners',
    url: 'https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'b1111111-1111-1111-1111-111111111111',
    name: 'Instant Warmth Heat Patch (Pack of 3)',
    url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'b2222222-2222-2222-2222-222222222222',
    name: 'Soothing Electric Heating Water Bag',
    url: 'https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'c1111111-1111-1111-1111-111111111111',
    name: 'Gentle pH-Balanced Intimate Wipes',
    url: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'd1111111-1111-1111-1111-111111111111',
    name: 'CycleCare Period Comfort Dark Chocolate (70%)',
    url: 'https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'd2222222-2222-2222-2222-222222222222',
    name: 'Chamomile & Ginger Soothing Herbal Tea',
    url: 'https://images.unsplash.com/photo-1597481499750-3e6b22637e12?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: '009f4b12-2efa-4e28-8c1a-4f872e955fb7',
    name: 'CycleCare Herbal Cramp Relief Roll-On',
    url: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: '1f970168-18c4-4b4a-81bd-3aed6fcf3587',
    name: 'CycleCare Magnesium Sleep & Cramp Gummies',
    url: 'https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=600&q=80'
  }
];

async function run() {
  try {
    await pool.query('ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;');

    for (const item of productsImages) {
      await pool.query('UPDATE products SET image_url = $1 WHERE id = $2;', [item.url, item.id]);
      await pool.query('DELETE FROM product_images WHERE product_id = $1;', [item.id]);
      await pool.query(
        'INSERT INTO product_images (product_id, image_url, sort_order, is_main, is_thumbnail) VALUES ($1, $2, 0, true, true);',
        [item.id, item.url]
      );
      console.log(`Updated images for: ${item.name}`);
    }

    const res = await pool.query('SELECT count(*) FROM product_images;');
    console.log(`Done! Total product_images in database: ${res.rows[0].count}`);
    await pool.end();
  } catch (err) {
    console.error('Error running seed script:', err);
    await pool.end();
  }
}

run();

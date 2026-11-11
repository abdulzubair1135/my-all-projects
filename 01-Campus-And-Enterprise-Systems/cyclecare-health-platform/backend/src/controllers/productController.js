const supabase = require('../config/supabase');
const { sendProductCampaignNotification } = require('../services/notificationService');

const getActorId = (user) => (user && user.id && user.id !== '00000000-0000-0000-0000-000000000000') ? user.id : null;

// Public Product Catalog Browsing
const getProducts = async (req, res, next) => {
  try {
    const { category_id, search, collection_id, sort, min_price, max_price, badge, status } = req.query;

    // Normal store browsing shows only PUBLISHED items
    const activeStatus = status || 'PUBLISHED';
    let query = supabase
      .from('products')
      .select('*, categories(name), product_images(*), product_variants(*)')
      .eq('status', activeStatus)
      .eq('is_active', true);

    if (category_id) query = query.eq('category_id', category_id);
    if (search) query = query.ilike('name', `%${search}%`);
    if (min_price) query = query.gte('price', parseFloat(min_price));
    if (max_price) query = query.lte('price', parseFloat(max_price));

    if (badge === 'NEW') query = query.eq('is_new_arrival', true);
    if (badge === 'FEATURED') query = query.eq('is_featured', true);
    if (badge === 'BEST_SELLER') query = query.eq('is_best_seller', true);

    if (sort === 'price_asc') query = query.order('price', { ascending: true });
    else if (sort === 'price_desc') query = query.order('price', { ascending: false });
    else query = query.order('created_at', { ascending: false });

    const { data: products, error } = await query;
    if (error) throw error;

    res.json({ success: true, count: products ? products.length : 0, products: products || [] });
  } catch (err) {
    next(err);
  }
};

// Detailed Single Product View (Increments Product Views Analytics)
const getProductById = async (req, res, next) => {
  try {
    const productId = req.params.id;

    const { data: product, error } = await supabase
      .from('products')
      .select('*, categories(name, description), product_images(*), product_variants(*)')
      .eq('id', productId)
      .single();

    if (error || !product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }

    // Increment views count in product_analytics asynchronously
    try {
      const { data: existing } = await supabase.from('product_analytics').select('views_count').eq('product_id', productId).single();
      if (existing) {
        await supabase.from('product_analytics').update({ views_count: existing.views_count + 1, updated_at: new Date() }).eq('product_id', productId);
      } else {
        await supabase.from('product_analytics').insert([{ product_id: productId, views_count: 1 }]);
      }
    } catch (_) {}

    res.json({ success: true, product });
  } catch (err) {
    next(err);
  }
};

// Admin: Create New Product (Defaults to DRAFT or requested status)
const createProduct = async (req, res, next) => {
  try {
    const {
      name, brand, description, category_id, price, discount_price, stock,
      low_stock_threshold, sku, status, tags, is_featured, is_new_arrival,
      is_best_seller, images, variants
    } = req.body;

    if (!name || price === undefined || !sku) {
      return res.status(400).json({ success: false, message: 'Name, price, and SKU are required' });
    }

    const productStatus = status || 'DRAFT';
    const numPrice = parseFloat(price);
    const numDiscount = discount_price ? parseFloat(discount_price) : null;
    const numStock = stock ? parseInt(stock) : 0;

    const { data: product, error } = await supabase
      .from('products')
      .insert([{
        name,
        brand: brand || 'CycleCare',
        description,
        category_id,
        price: numPrice,
        discount_price: numDiscount,
        stock: numStock,
        low_stock_threshold: low_stock_threshold || 5,
        sku,
        status: productStatus,
        tags: tags || [],
        is_featured: !!is_featured,
        is_new_arrival: is_new_arrival !== undefined ? !!is_new_arrival : true,
        is_best_seller: !!is_best_seller,
        is_active: productStatus !== 'ARCHIVED' && productStatus !== 'UNPUBLISHED'
      }])
      .select()
      .single();

    if (error) throw error;

    // Insert Images if provided
    if (images && Array.isArray(images) && images.length > 0) {
      const imgInserts = images.map((img, idx) => ({
        product_id: product.id,
        image_url: typeof img === 'string' ? img : img.url,
        is_main: idx === 0,
        sort_order: idx
      }));
      await supabase.from('product_images').insert(imgInserts);
    }

    // Insert Variants if provided
    if (variants && Array.isArray(variants) && variants.length > 0) {
      const variantInserts = variants.map(v => ({
        product_id: product.id,
        variant_name: v.variant_name || v.name,
        size: v.size || null,
        sku: v.sku || `${sku}-${v.size || Math.random().toString(36).substring(7)}`,
        price: v.price || numPrice,
        stock: v.stock || numStock,
        is_active: true
      }));
      await supabase.from('product_variants').insert(variantInserts);
    }

    // Initial Inventory Movement
    await supabase.from('inventory_movements').insert([{
      product_id: product.id,
      movement_type: 'ADD',
      quantity: numStock,
      previous_stock: 0,
      new_stock: numStock,
      reason: 'Initial Product Creation',
      actor_id: getActorId(req.user)
    }]);

    // Product Activity Log
    await supabase.from('product_activity_logs').insert([{
      product_id: product.id,
      actor_id: getActorId(req.user),
      action: 'PRODUCT_CREATED',
      new_value: { status: productStatus, price: numPrice, stock: numStock }
    }]);

    res.status(201).json({
      success: true,
      message: `Product created in ${productStatus} state`,
      product
    });
  } catch (err) {
    next(err);
  }
};

// Admin: Update Product Details
const updateProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;
    const updates = req.body;

    const { data: existing, error: fetchErr } = await supabase.from('products').select('*').eq('id', productId).single();
    if (fetchErr || !existing) return res.status(404).json({ success: false, message: 'Product not found' });

    // Handle stock difference
    if (updates.stock !== undefined && updates.stock !== existing.stock) {
      const newStock = parseInt(updates.stock);
      const diff = newStock - existing.stock;
      await supabase.from('inventory_movements').insert([{
        product_id: productId,
        movement_type: diff > 0 ? 'ADD' : 'REMOVE',
        quantity: Math.abs(diff),
        previous_stock: existing.stock,
        new_stock: newStock,
        reason: 'Admin Manual Stock Adjustment',
        actor_id: getActorId(req.user)
      }]);
    }

    const { data: updated, error } = await supabase
      .from('products')
      .update({ ...updates, updated_at: new Date() })
      .eq('id', productId)
      .select()
      .single();

    if (error) throw error;

    await supabase.from('product_activity_logs').insert([{
      product_id: productId,
      actor_id: getActorId(req.user),
      action: 'PRODUCT_UPDATED',
      old_value: existing,
      new_value: updated
    }]);

    res.json({ success: true, message: 'Product updated successfully', product: updated });
  } catch (err) {
    next(err);
  }
};

// Admin: Publish Product (Makes it visible in Android Store & optional notification)
const publishProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;
    const { notify_users, notification_title, notification_body, notification_image, target_audience } = req.body;

    const { data: product, error } = await supabase
      .from('products')
      .update({ status: 'PUBLISHED', is_active: true, updated_at: new Date() })
      .eq('id', productId)
      .select('*, product_images(*)')
      .single();

    if (error || !product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }

    // Product Activity Log
    await supabase.from('product_activity_logs').insert([{
      product_id: productId,
      actor_id: getActorId(req.user),
      action: 'PRODUCT_PUBLISHED',
      new_value: { status: 'PUBLISHED' }
    }]);

    let notificationResult = null;
    if (notify_users) {
      const defaultImg = (product.product_images && product.product_images[0]?.image_url) || notification_image;
      notificationResult = await sendProductCampaignNotification({
        productId: product.id,
        title: notification_title || `New care essential: ${product.name}`,
        body: notification_body || `Available now in CycleCare Store at ₹${product.discount_price || product.price}. Tap to view!`,
        imageUrl: defaultImg,
        targetAudience: target_audience || 'ALL'
      });
    }

    res.json({
      success: true,
      message: 'Product is now LIVE in CycleCare Store!',
      product,
      notification: notificationResult
    });
  } catch (err) {
    next(err);
  }
};

// Admin: Unpublish Product (Hides from Android Store)
const unpublishProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;

    const { data: product, error } = await supabase
      .from('products')
      .update({ status: 'UNPUBLISHED', is_active: false, updated_at: new Date() })
      .eq('id', productId)
      .select()
      .single();

    if (error) throw error;

    await supabase.from('product_activity_logs').insert([{
      product_id: productId,
      actor_id: req.user?.id || null,
      action: 'PRODUCT_UNPUBLISHED',
      new_value: { status: 'UNPUBLISHED' }
    }]);

    res.json({ success: true, message: 'Product unpublished and hidden from Store', product });
  } catch (err) {
    next(err);
  }
};

// Admin: Delete / Archive Product
const deleteProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;
    const pool = require('../config/db');
    await pool.query('DELETE FROM product_images WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM inventory_movements WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM product_variants WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM product_activity_logs WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM products WHERE id = $1', [productId]);
    res.json({ success: true, message: 'Product deleted successfully' });
  } catch (err) {
    next(err);
  }
};

// User Restock Notification Subscription
const subscribeRestockNotification = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const productId = req.params.id;

    const { data, error } = await supabase
      .from('restock_notifications')
      .upsert([{ user_id: userId, product_id: productId, notified: false }], { onConflict: 'user_id, product_id' })
      .select()
      .single();

    if (error) throw error;
    res.json({ success: true, message: 'You will be notified when this item is back in stock!' });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getProducts,
  getProductById,
  createProduct,
  updateProduct,
  publishProduct,
  unpublishProduct,
  deleteProduct,
  subscribeRestockNotification
};

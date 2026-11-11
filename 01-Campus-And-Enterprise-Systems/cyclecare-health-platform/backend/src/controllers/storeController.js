const supabase = require('../config/supabase');

const getCategories = async (req, res, next) => {
  try {
    const { data, error } = await supabase.from('categories').select('*').eq('is_active', true).order('name');
    if (error) throw error;
    res.json({ success: true, categories: data });
  } catch (err) {
    next(err);
  }
};

const getProducts = async (req, res, next) => {
  try {
    const { category_id, search, min_price, max_price, status } = req.query;
    let query = supabase.from('products').select('*, categories(name), product_images(*), product_variants(*)').eq('is_active', true);

    if (status) {
      query = query.eq('status', status);
    } else {
      query = query.or('status.eq.PUBLISHED,status.is.null');
    }

    if (category_id) query = query.eq('category_id', category_id);
    if (search) query = query.ilike('name', `%${search}%`);
    if (min_price) query = query.gte('price', parseFloat(min_price));
    if (max_price) query = query.lte('price', parseFloat(max_price));

    const { data, error } = await query.order('created_at', { ascending: false });
    if (error) throw error;
    res.json({ success: true, count: data ? data.length : 0, products: data || [] });
  } catch (err) {
    next(err);
  }
};

const getProductById = async (req, res, next) => {
  try {
    const productId = req.params.id;
    const { data: product, error } = await supabase
      .from('products')
      .select('*, categories(name), product_images(*), reviews(*)')
      .eq('id', productId)
      .single();

    if (error || !product) {
      return res.status(404).json({ success: false, message: 'Product not found' });
    }

    res.json({ success: true, product });
  } catch (err) {
    next(err);
  }
};

// Wishlist
const getWishlist = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data, error } = await supabase
      .from('wishlist')
      .select('*, products(*)')
      .eq('user_id', userId);

    if (error) throw error;
    res.json({ success: true, wishlist: data });
  } catch (err) {
    next(err);
  }
};

const addToWishlist = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { product_id } = req.body;

    if (!product_id) return res.status(400).json({ success: false, message: 'product_id required' });

    const { data, error } = await supabase
      .from('wishlist')
      .upsert([{ user_id: userId, product_id }], { onConflict: 'user_id, product_id' })
      .select()
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, message: 'Added to wishlist', wishlist: data });
  } catch (err) {
    next(err);
  }
};

const removeFromWishlist = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const productId = req.params.productId || req.params.id;

    const { error } = await supabase.from('wishlist').delete().eq('product_id', productId).eq('user_id', userId);
    if (error) throw error;

    res.json({ success: true, message: 'Removed from wishlist' });
  } catch (err) {
    next(err);
  }
};

// Cart
const getCart = async (req, res, next) => {
  try {
    const userId = req.user.id;
    let { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();

    if (!userCart) {
      const { data: newCart } = await supabase.from('cart').insert([{ user_id: userId }]).select().single();
      userCart = newCart;
    }

    const { data: items } = await supabase
      .from('cart_items')
      .select('*, products(id, name, description, price, discount_price, stock, sku, image_url, is_active)')
      .eq('cart_id', userCart.id);

    let subtotal = 0;
    const mappedItems = (items || []).map(item => {
      const activePrice = item.products?.discount_price || item.products?.price || item.unit_price;
      const total = activePrice * item.quantity;
      subtotal += total;
      return {
        ...item,
        product_name: item.products?.name || 'Item',
        image_url: item.products?.image_url || '',
        stock: item.products?.stock || 0,
        unit_price: activePrice,
        item_total: total
      };
    });

    res.json({
      success: true,
      cartId: userCart.id,
      items: mappedItems,
      subtotal,
      delivery_fee: subtotal > 499 || subtotal === 0 ? 0 : 40,
      total_amount: subtotal + (subtotal > 499 || subtotal === 0 ? 0 : 40)
    });
  } catch (err) {
    next(err);
  }
};

const addToCart = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { product_id, quantity } = req.body;

    if (!product_id || !quantity) return res.status(400).json({ success: false, message: 'product_id and quantity required' });

    // Validate product stock & authoritative price
    const { data: product } = await supabase.from('products').select('*').eq('id', product_id).single();
    if (!product || !product.is_active) {
      return res.status(404).json({ success: false, message: 'Product unavailable' });
    }
    if (product.stock < quantity) {
      return res.status(400).json({ success: false, message: `Only ${product.stock} items available in stock` });
    }

    let { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
    if (!userCart) {
      const { data: newCart } = await supabase.from('cart').insert([{ user_id: userId }]).select().single();
      userCart = newCart;
    }

    const activePrice = product.discount_price || product.price;

    const { data, error } = await supabase
      .from('cart_items')
      .upsert([{ cart_id: userCart.id, product_id, quantity, unit_price: activePrice }], { onConflict: 'cart_id, product_id' })
      .select()
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, message: 'Cart updated', item: data });
  } catch (err) {
    next(err);
  }
};

const removeFromCart = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const itemId = req.params.id;

    const { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
    if (!userCart) return res.status(404).json({ success: false, message: 'Cart not found' });

    const { error } = await supabase.from('cart_items').delete().eq('id', itemId).eq('cart_id', userCart.id);
    if (error) throw error;

    res.json({ success: true, message: 'Item removed from cart' });
  } catch (err) {
    next(err);
  }
};

const updateCartItem = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const itemId = req.params.id;
    const { quantity } = req.body;

    if (!quantity || quantity < 1) {
      return res.status(400).json({ success: false, message: 'Valid positive quantity required' });
    }

    const { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
    if (!userCart) return res.status(404).json({ success: false, message: 'Cart not found' });

    // Validate item & stock
    const { data: item } = await supabase
      .from('cart_items')
      .select('*, products(stock, is_active)')
      .eq('id', itemId)
      .eq('cart_id', userCart.id)
      .single();

    if (!item) return res.status(404).json({ success: false, message: 'Cart item not found' });

    if (item.products && item.products.stock < quantity) {
      return res.status(400).json({ success: false, message: `Only ${item.products.stock} items available in stock` });
    }

    const { data: updatedItem, error } = await supabase
      .from('cart_items')
      .update({ quantity })
      .eq('id', itemId)
      .eq('cart_id', userCart.id)
      .select()
      .single();

    if (error) throw error;
    res.json({ success: true, message: 'Cart item updated', item: updatedItem });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getCategories,
  getProducts,
  getProductById,
  getWishlist,
  addToWishlist,
  removeFromWishlist,
  getCart,
  addToCart,
  updateCartItem,
  removeFromCart
};

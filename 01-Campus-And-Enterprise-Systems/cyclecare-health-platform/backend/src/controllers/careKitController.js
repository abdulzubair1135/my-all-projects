const supabase = require('../config/supabase');

const getCareKits = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: kits, error } = await supabase
      .from('care_kits')
      .select('*, care_kit_items(*, products(*))')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;
    res.json({ success: true, careKits: kits || [] });
  } catch (err) {
    next(err);
  }
};

const createCareKit = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { name, items } = req.body; // items: [{ product_id, quantity }]

    if (!name) return res.status(400).json({ success: false, message: 'Care kit name is required' });

    const { data: newKit, error } = await supabase
      .from('care_kits')
      .insert([{ user_id: userId, name }])
      .select()
      .single();

    if (error) throw error;

    if (items && items.length > 0) {
      const kitItems = items.map(item => ({
        care_kit_id: newKit.id,
        product_id: item.product_id,
        quantity: item.quantity || 1
      }));
      await supabase.from('care_kit_items').insert(kitItems);
    }

    res.status(201).json({ success: true, message: 'Care kit created successfully', careKit: newKit });
  } catch (err) {
    next(err);
  }
};

const buyCareKit = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const kitId = req.params.id;

    const { data: kit } = await supabase
      .from('care_kits')
      .select('*, care_kit_items(*, products(*))')
      .eq('id', kitId)
      .eq('user_id', userId)
      .single();

    if (!kit) return res.status(404).json({ success: false, message: 'Care kit not found' });

    let { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
    if (!userCart) {
      const { data: newCart } = await supabase.from('cart').insert([{ user_id: userId }]).select().single();
      userCart = newCart;
    }

    let addedCount = 0;
    for (const item of kit.care_kit_items || []) {
      const product = item.products;
      if (product && product.is_active && product.stock > 0) {
        const qtyToAdd = Math.min(item.quantity, product.stock);
        const activePrice = product.discount_price || product.price;

        await supabase
          .from('cart_items')
          .upsert([{ cart_id: userCart.id, product_id: product.id, quantity: qtyToAdd, unit_price: activePrice }], { onConflict: 'cart_id, product_id' });

        addedCount++;
      }
    }

    res.json({ success: true, message: `Added ${addedCount} items from "${kit.name}" to cart.` });
  } catch (err) {
    next(err);
  }
};

// Budget Care Kit Calculator
const calculateBudgetKit = async (req, res, next) => {
  try {
    const budget = Number(req.query.max_budget) || 300;

    const { data: products } = await supabase.from('products').select('*, categories(name)').eq('is_active', true).order('price', { ascending: true });

    // Pick top essential combination fitting within budget
    let currentTotal = 0;
    const selectedItems = [];

    for (const product of products || []) {
      const price = Number(product.discount_price || product.price);
      if (currentTotal + price <= budget && product.stock > 0) {
        selectedItems.push(product);
        currentTotal += price;
      }
    }

    res.json({
      success: true,
      budget,
      calculatedTotal: currentTotal,
      suggestedItems: selectedItems
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getCareKits,
  createCareKit,
  buyCareKit,
  calculateBudgetKit
};

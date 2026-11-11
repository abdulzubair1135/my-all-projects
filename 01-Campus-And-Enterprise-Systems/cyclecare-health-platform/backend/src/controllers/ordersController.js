const supabase = require('../config/supabase');

const createOrder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const {
      address_id,
      address,
      items,
      coupon_code,
      is_discreet_packaging = true,
      delivery_notes = null,
      buyer_id = null,
      recipient_user_id = null,
      care_package_message = null
    } = req.body;

    let targetAddressId = address_id;

    if (!targetAddressId) {
      if (!address || !address.address_line || !address.pincode) {
        // Fallback: Check if user has an existing default or saved address in database
        const { data: defaultAddr } = await supabase
          .from('addresses')
          .select('id')
          .eq('user_id', userId)
          .eq('is_default', true)
          .maybeSingle();

        if (defaultAddr && defaultAddr.id) {
          targetAddressId = defaultAddr.id;
        } else {
          const { data: anyAddr } = await supabase
            .from('addresses')
            .select('id')
            .eq('user_id', userId)
            .limit(1);

          if (anyAddr && anyAddr.length > 0) {
            targetAddressId = anyAddr[0].id;
          } else {
            return res.status(400).json({ success: false, message: 'Valid delivery address or address_id is required' });
          }
        }
      } else {
        // Save new address
        const { data: savedAddress, error: addrError } = await supabase
          .from('addresses')
          .insert([{
            user_id: userId,
            name: address.name,
            phone: address.phone,
            address_line: address.address_line,
            landmark: address.landmark || null,
            city: address.city,
            state: address.state,
            pincode: address.pincode,
            type: address.type || 'HOME'
          }])
          .select()
          .single();

        if (addrError) throw addrError;
        targetAddressId = savedAddress.id;
      }
    }

    // Determine checkout items: either direct items (Buy Now) or Cart items
    let checkoutItems = [];
    let isDirectCheckout = Array.isArray(items) && items.length > 0;
    let userCart = null;

    if (isDirectCheckout) {
      for (const reqItem of items) {
        const { data: prod } = await supabase.from('products').select('*').eq('id', reqItem.product_id).single();
        if (prod) {
          checkoutItems.push({
            products: prod,
            quantity: reqItem.quantity || 1
          });
        }
      }
    } else {
      const { data: cart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
      userCart = cart;
      if (!userCart) return res.status(400).json({ success: false, message: 'Cart is empty' });

      const { data: cartItems } = await supabase
        .from('cart_items')
        .select('*, products(*)')
        .eq('cart_id', userCart.id);

      checkoutItems = cartItems || [];
    }

    if (!checkoutItems || checkoutItems.length === 0) {
      return res.status(400).json({ success: false, message: 'No items to order' });
    }

    // Calculate subtotal authoritatively from current DB prices & verify stock
    let subtotal = 0;
    const orderItemSnapshots = [];

    for (const item of checkoutItems) {
      const product = item.products;
      if (!product || !product.is_active) {
        return res.status(400).json({ success: false, message: `Product ${product?.name || ''} is no longer available` });
      }
      if (product.stock < item.quantity) {
        return res.status(400).json({ success: false, message: `Stock insufficient for ${product.name}. Available: ${product.stock}` });
      }

      const unitPrice = Number(product.discount_price || product.price);
      const total = unitPrice * item.quantity;
      subtotal += total;

      orderItemSnapshots.push({
        product_id: product.id,
        product_name_snapshot: product.name,
        image_url: product.image_url || null,
        unit_price: unitPrice,
        quantity: item.quantity,
        total: total
      });
    }

    // Coupon calculation
    let discount = 0;
    let couponId = null;
    if (coupon_code) {
      const { data: coupon } = await supabase.from('coupons').select('*').eq('code', coupon_code.toUpperCase()).eq('is_active', true).single();
      if (coupon && subtotal >= Number(coupon.minimum_order || 0)) {
        couponId = coupon.id;
        if (coupon.discount_type === 'PERCENTAGE') {
          discount = (subtotal * Number(coupon.discount_value)) / 100;
          if (coupon.maximum_discount && discount > Number(coupon.maximum_discount)) {
            discount = Number(coupon.maximum_discount);
          }
        } else {
          discount = Number(coupon.discount_value);
        }
      }
    }

    const deliveryFee = subtotal > 499 ? 0 : 40;
    const totalAmount = Math.max(0, subtotal - discount + deliveryFee);
    const orderNumber = `CC-${Date.now().toString().slice(-6)}${Math.floor(1000 + Math.random() * 9000)}`;
    const deliveryOtp = Math.floor(1000 + Math.random() * 9000).toString();

    // Create order header
    const { data: order, error: orderError } = await supabase
      .from('orders')
      .insert([{
        user_id: userId,
        address_id: targetAddressId,
        subtotal: subtotal,
        discount: discount,
        delivery_fee: deliveryFee,
        total_amount: totalAmount,
        coupon_id: couponId,
        order_number: orderNumber,
        status: 'PENDING',
        order_status: 'PROCESSING',
        delivery_status: 'ORDER_CONFIRMED',
        payment_status: 'PENDING',
        delivery_otp: deliveryOtp,
        is_discreet_packaging: !!is_discreet_packaging,
        delivery_notes: delivery_notes,
        buyer_id: buyer_id || userId,
        recipient_user_id: recipient_user_id || null,
        care_package_message: care_package_message || null
      }])
      .select()
      .single();

    if (orderError) throw orderError;

    // Create order items
    const itemsToInsert = orderItemSnapshots.map(i => ({ ...i, order_id: order.id }));
    await supabase.from('order_items').insert(itemsToInsert);

    // Clear cart if ordered from cart or if client requested clear_cart
    if (req.body.clear_cart || !isDirectCheckout) {
      if (userCart && userCart.id) {
        await supabase.from('cart_items').delete().eq('cart_id', userCart.id);
      } else {
        const { data: c } = await supabase.from('cart').select('id').eq('user_id', userId).maybeSingle();
        if (c && c.id) {
          await supabase.from('cart_items').delete().eq('cart_id', c.id);
        }
      }
    }

    res.status(201).json({
      success: true,
      message: 'Order created successfully',
      order: {
        ...order,
        items: itemsToInsert
      }
    });
  } catch (err) {
    next(err);
  }
};

const getUserOrders = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: orders, error } = await supabase
      .from('orders')
      .select('*, order_items(*), addresses(*), payments(*)')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;
    res.json({ success: true, orders });
  } catch (err) {
    next(err);
  }
};

const getOrderById = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const orderId = req.params.id;

    const { data: order, error } = await supabase
      .from('orders')
      .select('*, order_items(*), addresses(*), payments(*)')
      .eq('id', orderId)
      .eq('user_id', userId)
      .single();

    if (error || !order) return res.status(404).json({ success: false, message: 'Order not found' });
    res.json({ success: true, order });
  } catch (err) {
    next(err);
  }
};

const cancelOrder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const orderId = req.params.id;

    const { data: order } = await supabase.from('orders').select('*').eq('id', orderId).eq('user_id', userId).single();
    if (!order) return res.status(404).json({ success: false, message: 'Order not found' });

    if (['SHIPPED', 'DELIVERED', 'CANCELLED'].includes(order.status)) {
      return res.status(400).json({ success: false, message: `Cannot cancel order in ${order.status} state` });
    }

    const { data: updatedOrder, error } = await supabase
      .from('orders')
      .update({ status: 'CANCELLED', updated_at: new Date() })
      .eq('id', orderId)
      .select()
      .single();

    if (error) throw error;
    res.json({ success: true, message: 'Order cancelled successfully', order: updatedOrder });
  } catch (err) {
    next(err);
  }
};

// Re-order Previous Items (Buy Again)
const buyAgain = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const orderId = req.params.id;

    const { data: previousOrder } = await supabase
      .from('orders')
      .select('*, order_items(*)')
      .eq('id', orderId)
      .eq('user_id', userId)
      .single();

    if (!previousOrder) return res.status(404).json({ success: false, message: 'Previous order not found' });

    let { data: userCart } = await supabase.from('cart').select('id').eq('user_id', userId).single();
    if (!userCart) {
      const { data: newCart } = await supabase.from('cart').insert([{ user_id: userId }]).select().single();
      userCart = newCart;
    }

    let itemsReadded = 0;
    for (const item of previousOrder.order_items) {
      if (!item.product_id) continue;

      // Revalidate product exists, active & in stock
      const { data: product } = await supabase.from('products').select('*').eq('id', item.product_id).single();
      if (product && product.is_active && product.stock > 0) {
        const qtyToAdd = Math.min(item.quantity, product.stock);
        const activePrice = product.discount_price || product.price;

        await supabase
          .from('cart_items')
          .upsert([{ cart_id: userCart.id, product_id: product.id, quantity: qtyToAdd, unit_price: activePrice }], { onConflict: 'cart_id, product_id' });

        itemsReadded++;
      }
    }

    res.json({
      success: true,
      message: `Re-added ${itemsReadded} available item(s) to your cart.`
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  createOrder,
  getUserOrders,
  getOrderById,
  cancelOrder,
  buyAgain
};

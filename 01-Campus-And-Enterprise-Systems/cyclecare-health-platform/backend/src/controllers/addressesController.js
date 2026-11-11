const supabase = require('../config/supabase');

// GET /api/v1/addresses - List all saved addresses for the authenticated user
const getAddresses = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: addresses, error } = await supabase
      .from('addresses')
      .select('*')
      .eq('user_id', userId)
      .order('is_default', { ascending: false })
      .order('created_at', { ascending: false });

    if (error) throw error;
    res.json({ success: true, addresses: addresses || [] });
  } catch (err) {
    next(err);
  }
};

// GET /api/v1/addresses/:id - Get address by ID
const getAddressById = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { id } = req.params;

    const { data: address, error } = await supabase
      .from('addresses')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (error || !address) {
      return res.status(404).json({ success: false, message: 'Address not found' });
    }

    res.json({ success: true, address });
  } catch (err) {
    next(err);
  }
};

// POST /api/v1/addresses - Add a new address
const addAddress = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { name, phone, address_line, landmark, city, state, pincode, type, is_default } = req.body;

    if (!name || !phone || !address_line || !city || !state || !pincode) {
      return res.status(400).json({
        success: false,
        message: 'Name, phone, address line, city, state, and pincode are required'
      });
    }

    // If marked as default, unset other defaults
    if (is_default) {
      await supabase
        .from('addresses')
        .update({ is_default: false })
        .eq('user_id', userId);
    }

    // Check if this is the user's first address
    const { count } = await supabase
      .from('addresses')
      .select('id', { count: 'exact', head: true })
      .eq('user_id', userId);

    const makeDefault = is_default || count === 0;

    const { data: newAddress, error } = await supabase
      .from('addresses')
      .insert([{
        user_id: userId,
        name: name.trim(),
        phone: phone.trim(),
        address_line: address_line.trim(),
        landmark: landmark ? landmark.trim() : null,
        city: city.trim(),
        state: state.trim(),
        pincode: pincode.trim(),
        type: type || 'HOME',
        is_default: makeDefault
      }])
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({
      success: true,
      message: 'Address added successfully',
      address: newAddress
    });
  } catch (err) {
    next(err);
  }
};

// PUT /api/v1/addresses/:id - Update an existing address
const updateAddress = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { id } = req.params;
    const { name, phone, address_line, landmark, city, state, pincode, type, is_default } = req.body;

    const { data: existing } = await supabase
      .from('addresses')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (!existing) {
      return res.status(404).json({ success: false, message: 'Address not found' });
    }

    if (is_default) {
      await supabase
        .from('addresses')
        .update({ is_default: false })
        .eq('user_id', userId);
    }

    const updates = {};
    if (name !== undefined) updates.name = name.trim();
    if (phone !== undefined) updates.phone = phone.trim();
    if (address_line !== undefined) updates.address_line = address_line.trim();
    if (landmark !== undefined) updates.landmark = landmark ? landmark.trim() : null;
    if (city !== undefined) updates.city = city.trim();
    if (state !== undefined) updates.state = state.trim();
    if (pincode !== undefined) updates.pincode = pincode.trim();
    if (type !== undefined) updates.type = type;
    if (is_default !== undefined) updates.is_default = is_default;

    const { data: updatedAddress, error } = await supabase
      .from('addresses')
      .update(updates)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();

    if (error) throw error;

    res.json({
      success: true,
      message: 'Address updated successfully',
      address: updatedAddress
    });
  } catch (err) {
    next(err);
  }
};

// DELETE /api/v1/addresses/:id - Delete an address
const deleteAddress = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { id } = req.params;

    const { error } = await supabase
      .from('addresses')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);

    if (error) throw error;

    res.json({ success: true, message: 'Address deleted successfully' });
  } catch (err) {
    next(err);
  }
};

// POST /api/v1/addresses/:id/default - Set an address as default
const setDefaultAddress = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { id } = req.params;

    // Unset all defaults
    await supabase
      .from('addresses')
      .update({ is_default: false })
      .eq('user_id', userId);

    // Set target as default
    const { data: updatedAddress, error } = await supabase
      .from('addresses')
      .update({ is_default: true })
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();

    if (error || !updatedAddress) {
      return res.status(404).json({ success: false, message: 'Address not found' });
    }

    res.json({
      success: true,
      message: 'Default address updated',
      address: updatedAddress
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getAddresses,
  getAddressById,
  addAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress
};

const supabase = require('../config/supabase');

const getAgentDashboard = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: agent } = await supabase.from('delivery_agents').select('id').eq('user_id', userId).single();
    if (!agent) return res.status(403).json({ success: false, message: 'Not a delivery agent' });

    const { data: deliveries } = await supabase.from('deliveries')
      .select('*, orders(*)')
      .eq('agent_id', agent.id)
      .in('status', ['READY_FOR_DELIVERY', 'ASSIGNED', 'ACCEPTED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'ARRIVED']);

    res.json({ success: true, deliveries });
  } catch(err) { next(err); }
};

const updateDeliveryStatus = async (id, status, timestampField, req, res) => {
  const { data: delivery, error } = await supabase.from('deliveries').update({
    status,
    [timestampField]: new Date(),
    updated_at: new Date()
  }).eq('id', id).select('*').single();

  if (error || !delivery) return res.status(400).json({ success: false, message: 'Failed to update delivery' });

  await supabase.from('delivery_events').insert([{
    delivery_id: id,
    status,
    actor_id: req.user.id
  }]);

  if (['PICKED_UP', 'OUT_FOR_DELIVERY', 'ARRIVED', 'DELIVERED'].includes(status)) {
    await supabase.from('orders').update({ delivery_status: status }).eq('id', delivery.order_id);
  }

  res.json({ success: true, delivery });
};

const acceptDelivery = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: agent } = await supabase.from('delivery_agents').select('id').eq('user_id', userId).single();
    if (!agent) return res.status(403).json({ success: false, message: 'Not a delivery agent' });

    await supabase.from('deliveries').update({ agent_id: agent.id }).eq('id', req.params.id);
    await updateDeliveryStatus(req.params.id, 'ACCEPTED', 'accepted_at', req, res);
  } catch(err) { next(err); }
};

const pickupDelivery = async (req, res, next) => {
  try { await updateDeliveryStatus(req.params.id, 'PICKED_UP', 'picked_up_at', req, res); } catch(err) { next(err); }
};

const startDelivery = async (req, res, next) => {
  try { await updateDeliveryStatus(req.params.id, 'OUT_FOR_DELIVERY', 'started_at', req, res); } catch(err) { next(err); }
};

const arrivedDelivery = async (req, res, next) => {
  try { await updateDeliveryStatus(req.params.id, 'ARRIVED', 'arrived_at', req, res); } catch(err) { next(err); }
};

const completeDelivery = async (req, res, next) => {
  try {
    const { delivery_otp } = req.body;
    const { data: delivery } = await supabase.from('deliveries').select('delivery_otp, order_id').eq('id', req.params.id).single();
    
    if (!delivery || delivery.delivery_otp !== delivery_otp) {
      return res.status(400).json({ success: false, message: 'Invalid OTP' });
    }

    await supabase.from('deliveries').update({
      status: 'DELIVERED',
      delivered_at: new Date(),
      updated_at: new Date()
    }).eq('id', req.params.id);

    try {
      const actorId = (req.user && req.user.id !== '00000000-0000-0000-0000-000000000000') ? req.user.id : null;
      await supabase.from('delivery_events').insert([{
        delivery_id: req.params.id,
        status: 'DELIVERED',
        actor_id: actorId
      }]);
    } catch (_) {}

    await supabase.from('orders').update({ delivery_status: 'DELIVERED', status: 'COMPLETED' }).eq('id', delivery.order_id);

    res.json({ success: true, message: 'Delivery completed' });
  } catch(err) { next(err); }
};

const updateLocation = async (req, res, next) => {
  try {
    const { latitude, longitude, progress_percent, eta_minutes } = req.body;
    await supabase.from('delivery_live_locations').upsert({
      delivery_id: req.params.id,
      latitude, longitude, progress_percent, eta_minutes,
      updated_at: new Date()
    }, { onConflict: 'delivery_id' });
    res.json({ success: true, message: 'Location updated' });
  } catch(err) { next(err); }
};

const simulateLocation = async (req, res, next) => {
  try {
    const route = [
      { p: 0, eta: 30, lat: 28.6139, lng: 77.2090 },
      { p: 25, eta: 22, lat: 28.6145, lng: 77.2100 },
      { p: 50, eta: 15, lat: 28.6150, lng: 77.2120 },
      { p: 75, eta: 7, lat: 28.6160, lng: 77.2140 },
      { p: 90, eta: 3, lat: 28.6170, lng: 77.2155 },
      { p: 100, eta: 0, lat: 28.6180, lng: 77.2165 }
    ];
    let index = 0;
    const interval = setInterval(async () => {
      if (index >= route.length) {
        clearInterval(interval);
        return;
      }
      const pt = route[index];
      await supabase.from('delivery_live_locations').upsert({
        delivery_id: req.params.id,
        latitude: pt.lat, longitude: pt.lng, progress_percent: pt.p, eta_minutes: pt.eta,
        updated_at: new Date()
      }, { onConflict: 'delivery_id' });
      index++;
    }, 2000);
    res.json({ success: true, message: 'Simulation started' });
  } catch(err) { next(err); }
};

const resetDemoDelivery = async (req, res, next) => {
  try {
    const { data: order } = await supabase.from('orders').select('id').eq('order_number', '#CC-DEMO-1001').single();
    if (!order) return res.status(404).json({ success: false, message: 'Demo order not found' });

    await supabase.from('orders').update({
      status: 'PAID',
      order_status: 'READY_FOR_DELIVERY',
      delivery_status: 'READY_FOR_DELIVERY'
    }).eq('id', order.id);

    await supabase.from('deliveries').update({
      status: 'READY_FOR_DELIVERY',
      accepted_at: null,
      picked_up_at: null,
      started_at: null,
      arrived_at: null,
      delivered_at: null
    }).eq('order_id', order.id);

    const { data: delivery } = await supabase.from('deliveries').select('id').eq('order_id', order.id).single();
    if (delivery) {
      await supabase.from('delivery_events').delete().eq('delivery_id', delivery.id);
      await supabase.from('delivery_live_locations').delete().eq('delivery_id', delivery.id);
    }

    res.json({ success: true, message: 'Demo delivery reset' });
  } catch(err) { next(err); }
};

const getOrderTracking = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { id } = req.params;

    const { data: order } = await supabase.from('orders').select('*').eq('id', id).single();
    if (!order) return res.status(404).json({ success: false, message: 'Order not found' });

    const isRecipient = order.recipient_user_id === userId;
    const isBuyer = order.buyer_id === userId;
    const isOwner = order.user_id === userId;
    if (!isRecipient && !isBuyer && !isOwner) return res.status(403).json({ success: false, message: 'Unauthorized' });

    const { data: delivery } = await supabase.from('deliveries').select('*, delivery_agents(name, phone)').eq('order_id', id).single();
    let location = null;
    let events = [];
    if (delivery) {
      const locRes = await supabase.from('delivery_live_locations').select('*').eq('delivery_id', delivery.id).single();
      if (locRes.data) location = locRes.data;

      const evtsRes = await supabase.from('delivery_events').select('*').eq('delivery_id', delivery.id).order('timestamp', { ascending: true });
      if (evtsRes.data) events = evtsRes.data;
    }

    res.json({
      success: true,
      order: {
        id: order.id,
        order_number: order.order_number,
        status: order.status,
        delivery_status: order.delivery_status
      },
      delivery: delivery ? {
        status: delivery.status,
        agent: delivery.delivery_agents,
        delivery_otp: isRecipient ? delivery.delivery_otp : null
      } : null,
      location,
      events
    });
  } catch(err) { next(err); }
};

module.exports = {
  getAgentDashboard,
  acceptDelivery,
  pickupDelivery,
  startDelivery,
  arrivedDelivery,
  completeDelivery,
  updateLocation,
  simulateLocation,
  resetDemoDelivery,
  getOrderTracking
};

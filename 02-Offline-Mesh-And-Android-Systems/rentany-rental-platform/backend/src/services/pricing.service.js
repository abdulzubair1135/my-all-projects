export const pricingService = {
  calculateRentalDays(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Clear times for exact day calculations
    start.setHours(0, 0, 0, 0);
    end.setHours(0, 0, 0, 0);
    
    const diffTime = end.getTime() - start.getTime();
    if (diffTime < 0) return 0;
    
    // Convert ms to days. Add 1 because renting from Monday to Monday is 1 day (or is it 2? usually: 1 day minimum).
    // Let's compute: 1 day minimum. (end - start) in days.
    // If start is 2026-08-20 and end is 2026-08-21, diff is 1 day. Let's return Math.max(1, diffDays).
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(1, diffDays);
  },

  calculatePrice({ pricePerDay, rentalDays, quantity = 1, deliveryAvailable, deliveryType, deliveryFee = 0.00, depositPerItem = 0.00 }) {
    const subtotal = Number((pricePerDay * rentalDays * quantity).toFixed(2));
    
    // Calculate service fee (e.g. 5% platform fee)
    const serviceFee = Number((subtotal * 0.05).toFixed(2));
    
    // Calculate delivery fee
    const finalDeliveryFee = (deliveryAvailable && deliveryType === 'Delivery') ? Number(deliveryFee) : 0.00;
    
    // Security deposit (tracked separately but paid upfront usually)
    const depositAmount = Number((depositPerItem * quantity).toFixed(2));
    
    // Grand total
    const totalAmount = Number((subtotal + finalDeliveryFee + serviceFee + depositAmount).toFixed(2));

    return {
      rentalDays,
      pricePerDay: Number(pricePerDay),
      subtotal,
      deliveryFee: finalDeliveryFee,
      serviceFee,
      discount: 0.00,
      depositAmount,
      totalAmount
    };
  }
};

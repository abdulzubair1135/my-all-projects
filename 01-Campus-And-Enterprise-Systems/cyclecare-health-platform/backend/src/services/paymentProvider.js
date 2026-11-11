class PaymentProvider {
    async createPayment(orderId, amount, currency, metadata) {
        throw new Error("Method not implemented.");
    }
    
    async processPayment(paymentId, status, metadata) {
        throw new Error("Method not implemented.");
    }
    
    async refundPayment(paymentId, amount, reason) {
        throw new Error("Method not implemented.");
    }
}

class DemoPaymentProvider extends PaymentProvider {
    async createPayment(orderId, amount, currency = 'INR', metadata = {}) {
        return {
            id: `demo_pay_${Date.now()}_${Math.random().toString(36).substring(7)}`,
            orderId,
            amount,
            currency,
            status: 'CREATED',
            provider: 'DEMO',
            paymentMethod: metadata.paymentMethod || 'DEMO_UPI',
            metadata
        };
    }

    async processPayment(paymentId, status, metadata = {}) {
        return {
            id: paymentId,
            status: status === 'SUCCESS' ? 'SUCCESS' : status === 'CANCELLED' ? 'CANCELLED' : 'FAILED',
            transactionId: `txn_demo_${Date.now()}`,
            processedAt: new Date(),
            metadata
        };
    }

    async refundPayment(paymentId, amount, reason) {
        return {
            id: paymentId,
            status: 'REFUNDED',
            refundAmount: amount,
            reason,
            refundId: `ref_demo_${Date.now()}`,
            processedAt: new Date()
        };
    }
}

module.exports = { PaymentProvider, DemoPaymentProvider };

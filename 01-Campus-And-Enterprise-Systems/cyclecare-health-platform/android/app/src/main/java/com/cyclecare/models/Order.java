package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

public class Order implements Serializable {
    @SerializedName("id")
    private String id;

    @SerializedName("order_number")
    private String orderNumber;

    @SerializedName("user_id")
    private String userId;

    @SerializedName("address_id")
    private String addressId;

    @SerializedName("subtotal")
    private double subtotal;

    @SerializedName("discount")
    private double discount;

    @SerializedName("delivery_fee")
    private double deliveryFee;

    @SerializedName("total_amount")
    private double totalAmount;

    @SerializedName("status")
    private String status;

    @SerializedName("order_status")
    private String orderStatus;

    @SerializedName("delivery_status")
    private String deliveryStatus;

    @SerializedName("payment_status")
    private String paymentStatus;

    @SerializedName("delivery_otp")
    private String deliveryOtp;

    @SerializedName("is_discreet_packaging")
    private boolean isDiscreetPackaging;

    @SerializedName("delivery_notes")
    private String deliveryNotes;

    @SerializedName("created_at")
    private String createdAt;

    @SerializedName("addresses")
    private UserAddress address;

    @SerializedName("order_items")
    private List<OrderItem> items;

    public Order() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getOrderNumber() { return orderNumber != null ? orderNumber : "CC-" + (id != null && id.length() > 6 ? id.substring(0, 6).toUpperCase() : "1001"); }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getAddressId() { return addressId; }
    public void setAddressId(String addressId) { this.addressId = addressId; }

    public double getSubtotal() { return subtotal; }
    public void setSubtotal(double subtotal) { this.subtotal = subtotal; }

    public double getDiscount() { return discount; }
    public void setDiscount(double discount) { this.discount = discount; }

    public double getDeliveryFee() { return deliveryFee; }
    public void setDeliveryFee(double deliveryFee) { this.deliveryFee = deliveryFee; }

    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getOrderStatus() { return orderStatus != null ? orderStatus : (status != null ? status : "PROCESSING"); }
    public void setOrderStatus(String orderStatus) { this.orderStatus = orderStatus; }

    public String getDeliveryStatus() { return deliveryStatus != null ? deliveryStatus : "ORDER_CONFIRMED"; }
    public void setDeliveryStatus(String deliveryStatus) { this.deliveryStatus = deliveryStatus; }

    public String getPaymentStatus() { return paymentStatus != null ? paymentStatus : "PENDING"; }
    public void setPaymentStatus(String paymentStatus) { this.paymentStatus = paymentStatus; }

    public String getDeliveryOtp() { return deliveryOtp != null ? deliveryOtp : "4821"; }
    public void setDeliveryOtp(String deliveryOtp) { this.deliveryOtp = deliveryOtp; }

    public boolean isDiscreetPackaging() { return isDiscreetPackaging; }
    public void setDiscreetPackaging(boolean discreetPackaging) { isDiscreetPackaging = discreetPackaging; }

    public String getDeliveryNotes() { return deliveryNotes; }
    public void setDeliveryNotes(String deliveryNotes) { this.deliveryNotes = deliveryNotes; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public UserAddress getAddress() { return address; }
    public void setAddress(UserAddress address) { this.address = address; }

    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }

    public static class OrderItem implements Serializable {
        @SerializedName("id")
        private String id;

        @SerializedName("product_id")
        private String productId;

        @SerializedName("product_name_snapshot")
        private String productNameSnapshot;

        @SerializedName("image_url")
        private String imageUrl;

        @SerializedName("unit_price")
        private double unitPrice;

        @SerializedName("quantity")
        private int quantity;

        @SerializedName("total")
        private double total;

        public OrderItem() {}

        public String getId() { return id; }
        public String getProductId() { return productId; }
        public String getProductNameSnapshot() { return productNameSnapshot != null ? productNameSnapshot : "Care Item"; }
        public String getImageUrl() { return imageUrl; }
        public double getUnitPrice() { return unitPrice; }
        public int getQuantity() { return quantity; }
        public double getTotal() { return total; }
    }
}

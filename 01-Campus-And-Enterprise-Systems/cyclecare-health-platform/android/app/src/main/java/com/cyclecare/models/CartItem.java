package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class CartItem implements Serializable {
    @SerializedName("id")
    private String id;

    @SerializedName("cart_id")
    private String cartId;

    @SerializedName("product_id")
    private String productId;

    @SerializedName("product_name")
    private String productName;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("quantity")
    private int quantity;

    @SerializedName("unit_price")
    private double unitPrice;

    @SerializedName("item_total")
    private double itemTotal;

    @SerializedName("stock")
    private int stock;

    public CartItem() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getCartId() { return cartId; }
    public void setCartId(String cartId) { this.cartId = cartId; }

    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }

    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public double getUnitPrice() { return unitPrice; }
    public void setUnitPrice(double unitPrice) { this.unitPrice = unitPrice; }

    public double getItemTotal() { return itemTotal; }
    public void setItemTotal(double itemTotal) { this.itemTotal = itemTotal; }

    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }
}

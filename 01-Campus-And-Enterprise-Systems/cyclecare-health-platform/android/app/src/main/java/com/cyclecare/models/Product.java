package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;
import java.util.Map;

public class Product {
    @SerializedName("id")
    private String id;

    @SerializedName("name")
    private String name;

    @SerializedName("brand")
    private String brand;

    @SerializedName("description")
    private String description;

    @SerializedName("price")
    private double price;

    @SerializedName("discount_price")
    private Double discountPrice;

    @SerializedName("stock")
    private int stock;

    @SerializedName("sku")
    private String sku;

    @SerializedName("category")
    private String category;

    @SerializedName("categories")
    private Map<String, Object> categoriesObj;

    @SerializedName("is_featured")
    private Boolean isFeatured;

    @SerializedName("is_new_arrival")
    private Boolean isNewArrival;

    @SerializedName("is_best_seller")
    private Boolean isBestSeller;

    @SerializedName("status")
    private String status;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("product_images")
    private List<Map<String, Object>> productImages;

    public Product() {}

    public Product(String id, String name, String description, double price, String category, int stock) {
        this(id, name, description, price, category, stock, null);
    }

    public Product(String id, String name, String description, double price, String category, int stock, String imageUrl) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.category = category;
        this.stock = stock;
        this.imageUrl = imageUrl;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getBrand() { return brand != null ? brand : "CycleCare Originals"; }
    public String getDescription() { return description != null ? description : "Pure organic comfort designed for cycle wellness."; }
    public double getPrice() { return price; }
    public Double getDiscountPrice() { return discountPrice; }
    public double getActivePrice() { return (discountPrice != null && discountPrice > 0) ? discountPrice : price; }
    public int getStock() { return stock; }
    public String getSku() { return sku != null ? sku : "CC-GEN-01"; }
    
    public String getCategory() {
        if (categoriesObj != null && categoriesObj.containsKey("name")) {
            return String.valueOf(categoriesObj.get("name"));
        }
        return category != null ? category : "Period Care";
    }

    public String getImageUrl() {
        if (productImages != null && !productImages.isEmpty()) {
            Object url = productImages.get(0).get("image_url");
            if (url != null && !url.toString().trim().isEmpty()) return url.toString().trim();
        }
        if (imageUrl != null && !imageUrl.trim().isEmpty()) {
            return imageUrl.trim();
        }
        return null;
    }

    public Boolean isFeatured() { return isFeatured != null && isFeatured; }
    public Boolean isNewArrival() { return isNewArrival != null && isNewArrival; }
    public Boolean isBestSeller() { return isBestSeller != null && isBestSeller; }
    public String getStatus() { return status != null ? status : "PUBLISHED"; }
}

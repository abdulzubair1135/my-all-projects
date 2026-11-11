package com.cyclecare.models;

import java.io.Serializable;

public class QuickCareItem implements Serializable {
    private String id;
    private String name;
    private String category;
    private int price;
    private String image_url;
    private String description;

    public QuickCareItem() {}

    public QuickCareItem(String id, String name, String category, int price, String image_url, String description) {
        this.id = id;
        this.name = name;
        this.category = category;
        this.price = price;
        this.image_url = image_url;
        this.description = description;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getCategory() { return category; }
    public int getPrice() { return price; }
    public String getImageUrl() { return image_url; }
    public String getDescription() { return description; }
}

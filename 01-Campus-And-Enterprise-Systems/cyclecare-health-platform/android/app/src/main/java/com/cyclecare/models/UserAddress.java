package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class UserAddress implements Serializable {
    @SerializedName("id")
    private String id;

    @SerializedName("user_id")
    private String userId;

    @SerializedName("name")
    private String name;

    @SerializedName("phone")
    private String phone;

    @SerializedName("address_line")
    private String addressLine;

    @SerializedName("landmark")
    private String landmark;

    @SerializedName("city")
    private String city;

    @SerializedName("state")
    private String state;

    @SerializedName("pincode")
    private String pincode;

    @SerializedName("type")
    private String type; // HOME, WORK, PARTNER, OTHER

    @SerializedName("is_default")
    private boolean isDefault;

    public UserAddress() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getAddressLine() { return addressLine; }
    public void setAddressLine(String addressLine) { this.addressLine = addressLine; }

    public String getLandmark() { return landmark; }
    public void setLandmark(String landmark) { this.landmark = landmark; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getState() { return state; }
    public void setState(String state) { this.state = state; }

    public String getPincode() { return pincode; }
    public void setPincode(String pincode) { this.pincode = pincode; }

    public String getType() { return type != null ? type : "HOME"; }
    public void setType(String type) { this.type = type; }

    public boolean isDefault() { return isDefault; }
    public void setDefault(boolean aDefault) { isDefault = aDefault; }

    public String getFormattedAddress() {
        StringBuilder sb = new StringBuilder();
        if (addressLine != null) sb.append(addressLine);
        if (landmark != null && !landmark.trim().isEmpty()) sb.append(", Near ").append(landmark);
        if (city != null) sb.append(", ").append(city);
        if (state != null) sb.append(", ").append(state);
        if (pincode != null) sb.append(" - ").append(pincode);
        return sb.toString();
    }
}

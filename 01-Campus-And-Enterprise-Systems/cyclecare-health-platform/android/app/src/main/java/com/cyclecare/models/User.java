package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;

public class User {
    @SerializedName("id")
    private String id;

    @SerializedName("email")
    private String email;

    @SerializedName("role")
    private String role;

    @SerializedName("display_name")
    private String displayName;

    public String getId() { return id; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    public String getDisplayName() { return displayName; }
}

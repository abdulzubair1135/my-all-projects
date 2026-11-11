package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;

public class ApiResponse<T> {
    @SerializedName("success")
    private boolean success;

    @SerializedName("message")
    private String message;

    @SerializedName("code")
    private String code;

    @SerializedName("token")
    private String token;

    @SerializedName("user")
    private User user;

    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public String getCode() { return code; }
    public String getToken() { return token; }
    public User getUser() { return user; }
}

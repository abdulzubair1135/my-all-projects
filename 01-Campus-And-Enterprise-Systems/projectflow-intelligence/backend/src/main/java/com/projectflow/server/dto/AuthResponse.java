package com.projectflow.server.dto;

public class AuthResponse {
    private String accessToken;
    private String tokenType = "Bearer";
    private UserProfileDto user;

    public AuthResponse() {
    }

    public AuthResponse(String accessToken, UserProfileDto user) {
        this.accessToken = accessToken;
        this.tokenType = "Bearer";
        this.user = user;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getTokenType() {
        return tokenType;
    }

    public void setTokenType(String tokenType) {
        this.tokenType = tokenType;
    }

    public UserProfileDto getUser() {
        return user;
    }

    public void setUser(UserProfileDto user) {
        this.user = user;
    }
}

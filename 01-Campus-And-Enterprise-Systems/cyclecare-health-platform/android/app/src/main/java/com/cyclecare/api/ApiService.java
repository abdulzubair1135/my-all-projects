package com.cyclecare.api;

import com.cyclecare.models.ApiResponse;
import com.cyclecare.models.PeriodLog;
import com.cyclecare.models.Product;

import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.PATCH;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {

    @POST("auth/register")
    Call<ApiResponse<Void>> register(@Body Map<String, String> body);

    @POST("auth/login")
    Call<ApiResponse<Void>> login(@Body Map<String, String> body);

    @POST("auth/forgot-password")
    Call<Map<String, Object>> forgotPassword(@Body Map<String, String> body);

    @POST("auth/reset-password")
    Call<Map<String, Object>> resetPassword(@Body Map<String, String> body);

    @PUT("auth/profile")
    Call<Map<String, Object>> updateProfile(@Body Map<String, String> body);

    @GET("cycle")
    Call<Map<String, Object>> getCycleData();

    @GET("cycle/history")
    Call<Map<String, Object>> getCycleHistory();

    @GET("cycle/prediction")
    Call<Map<String, Object>> getCyclePrediction();

    @POST("cycle/period")
    Call<ApiResponse<PeriodLog>> addPeriodLog(@Body PeriodLog periodLog);

    @PUT("cycle/period/{id}")
    Call<Map<String, Object>> updatePeriodLog(@Path("id") String id, @Body Map<String, String> body);

    @DELETE("cycle/period/{id}")
    Call<ApiResponse<Void>> deletePeriodLog(@Path("id") String id);

    @GET("symptoms")
    Call<Map<String, Object>> getSymptoms();

    @POST("symptoms/log")
    Call<Map<String, Object>> logSymptom(@Body Map<String, Object> body);

    @GET("moods")
    Call<Map<String, Object>> getMoods();

    @POST("moods/log")
    Call<Map<String, Object>> logMood(@Body Map<String, Object> body);

    @GET("reminders")
    Call<Map<String, Object>> getReminders();

    @POST("reminders")
    Call<Map<String, Object>> createReminder(@Body Map<String, Object> body);

    @GET("store/products")
    Call<Map<String, Object>> getProducts(@Query("category_id") String categoryId, @Query("search") String search);

    @GET("products/{id}")
    Call<Map<String, Object>> getProductDetails(@Path("id") String id);

    @GET("store/products/{id}")
    Call<Map<String, Object>> getStoreProductDetails(@Path("id") String id);

    @GET("store/cart")
    Call<Map<String, Object>> getCart();

    @POST("store/cart/items")
    Call<Map<String, Object>> addToCart(@Body Map<String, Object> body);

    @PUT("store/cart/items/{id}")
    Call<Map<String, Object>> updateCartItem(@Path("id") String id, @Body Map<String, Object> body);

    @DELETE("store/cart/items/{id}")
    Call<Map<String, Object>> removeFromCart(@Path("id") String id);

    // Addresses
    @GET("addresses")
    Call<Map<String, Object>> getAddresses();

    @POST("addresses")
    Call<Map<String, Object>> addAddress(@Body Map<String, Object> body);

    @PUT("addresses/{id}")
    Call<Map<String, Object>> updateAddress(@Path("id") String id, @Body Map<String, Object> body);

    @DELETE("addresses/{id}")
    Call<Map<String, Object>> deleteAddress(@Path("id") String id);

    @POST("addresses/{id}/default")
    Call<Map<String, Object>> setDefaultAddress(@Path("id") String id);

    // Orders
    @POST("orders")
    Call<Map<String, Object>> createOrder(@Body Map<String, Object> body);

    @GET("orders")
    Call<Map<String, Object>> getUserOrders();

    @GET("orders/{id}")
    Call<Map<String, Object>> getOrderById(@Path("id") String id);

    @POST("orders/{id}/cancel")
    Call<Map<String, Object>> cancelOrder(@Path("id") String id);

    // Payments
    @POST("payments/demo/create")
    Call<Map<String, Object>> createDemoPayment(@Body Map<String, Object> body);

    @POST("payments/demo/success")
    Call<Map<String, Object>> demoPaymentSuccess(@Body Map<String, Object> body);

    @POST("payments/razorpay/create")
    Call<Map<String, Object>> createRazorpayOrder(@Body Map<String, Object> body);

    @POST("payments/razorpay/verify")
    Call<Map<String, Object>> verifyRazorpayPayment(@Body Map<String, Object> body);

    @GET("care-kits")
    Call<Map<String, Object>> getCareKits();

    @POST("ai/chat")
    Call<Map<String, Object>> askAI(@Body Map<String, Object> body);

    // Partner Care Mode
    @GET("partners/search")
    Call<Map<String, Object>> searchPartner(@Query("cyclecare_id") String cyclecareId);

    @POST("partners/invite")
    Call<Map<String, Object>> createPartnerInvite();

    @POST("partners/request")
    Call<Map<String, Object>> sendPartnerRequest(@Body Map<String, Object> body);

    @GET("partners/requests")
    Call<Map<String, Object>> getPartnerRequests();

    @GET("partners/connections")
    Call<Map<String, Object>> getPartnerConnections();

    @PATCH("partners/{id}/relationship")
    Call<Map<String, Object>> updatePartnerRelationship(@Path("id") String connectionId, @Body Map<String, Object> body);

    @GET("partners/{id}/member-status")
    Call<Map<String, Object>> getMemberStatus(@Path("id") String connectionId);

    @GET("partners/{id}/audit-trail")
    Call<Map<String, Object>> getPartnerAuditTrail(@Path("id") String connectionId);

    @POST("partners/requests/{id}/accept")
    Call<Map<String, Object>> acceptPartnerRequest(@Path("id") String requestId);

    @POST("partners/requests/{id}/decline")
    Call<Map<String, Object>> declinePartnerRequest(@Path("id") String requestId);

    @DELETE("partners/{id}")
    Call<Map<String, Object>> revokePartnerConnection(@Path("id") String connectionId);

    @POST("partners/{id}/block")
    Call<Map<String, Object>> blockPartner(@Path("id") String connectionId);

    @GET("partners/{id}/permissions")
    Call<Map<String, Object>> getPartnerPermissions(@Path("id") String connectionId);

    @PUT("partners/{id}/permissions")
    Call<Map<String, Object>> updatePartnerPermissions(@Path("id") String connectionId, @Body Map<String, Object> body);

    @GET("partners/{id}/shared-cycle")
    Call<Map<String, Object>> getSharedCycle(@Path("id") String connectionId);

    @GET("partners/{id}/care-kit")
    Call<Map<String, Object>> getSharedCareKit(@Path("id") String connectionId);

    @GET("partners/{id}/wishlist")
    Call<Map<String, Object>> getSharedWishlist(@Path("id") String connectionId);

    @POST("partners/{id}/care-package")
    Call<Map<String, Object>> createCarePackage(@Path("id") String connectionId, @Body Map<String, Object> body);

    // Delivery Endpoints
    @GET("delivery/dashboard")
    Call<Map<String, Object>> getDeliveryDashboard();

    @POST("delivery/{id}/accept")
    Call<Map<String, Object>> acceptDelivery(@Path("id") String id);

    @POST("delivery/{id}/pickup")
    Call<Map<String, Object>> pickupDelivery(@Path("id") String id);

    @POST("delivery/{id}/start")
    Call<Map<String, Object>> startDelivery(@Path("id") String id);

    @POST("delivery/{id}/simulate")
    Call<Map<String, Object>> simulateDelivery(@Path("id") String id, @Query("step") int step);

    @POST("delivery/{id}/arrive")
    Call<Map<String, Object>> arriveDelivery(@Path("id") String id);

    @POST("delivery/{id}/complete")
    Call<Map<String, Object>> completeDelivery(@Path("id") String id, @Body Map<String, Object> body);

    @GET("delivery/order/{orderId}")
    Call<Map<String, Object>> getOrderTracking(@Path("orderId") String orderId);

    @POST("delivery/demo/reset")
    Call<Map<String, Object>> resetDemoDelivery();

    // Circle Care Chat & Care/Medical Item Sharing
    @GET("chat/contacts")
    Call<Map<String, Object>> getCircleContacts();

    @GET("chat/quick-items")
    Call<Map<String, Object>> getQuickCareItems();

    @GET("chat/messages/{connection_id}")
    Call<Map<String, Object>> getChatMessages(@Path("connection_id") String connectionId);

    @POST("chat/send")
    Call<Map<String, Object>> sendChatMessage(@Body Map<String, Object> body);

    @POST("chat/send-item")
    Call<Map<String, Object>> sendChatCareItem(@Body Map<String, Object> body);

    // Social Follow / Following & User Search
    @GET("chat/users/search")
    Call<Map<String, Object>> searchUsers(@Query("query") String query);

    @POST("chat/users/follow")
    Call<Map<String, Object>> followUser(@Body Map<String, String> body);

    @POST("chat/users/unfollow")
    Call<Map<String, Object>> unfollowUser(@Body Map<String, String> body);

    @GET("chat/users/{userId}/social-stats")
    Call<Map<String, Object>> getUserSocialStats(@Path("userId") String userId);

    @GET("chat/users/{userId}/followers")
    Call<Map<String, Object>> getFollowers(@Path("userId") String userId);

    @GET("chat/users/{userId}/following")
    Call<Map<String, Object>> getFollowing(@Path("userId") String userId);

    @POST("chat/set-tag")
    Call<Map<String, Object>> setContactTag(@Body Map<String, String> body);

    @DELETE("chat/messages/{messageId}")
    Call<Map<String, Object>> deleteChatMessage(@Path("messageId") String messageId);

    @DELETE("chat/connections/{connection_id}")
    Call<Map<String, Object>> deleteCircleConnection(@Path("connection_id") String connectionId);

    // Global Error Monitoring & Crash Reporting
    @POST("monitoring/errors")
    Call<Map<String, Object>> reportError(@Body Map<String, Object> body);

    // FCM Device Push Token Registration
    @POST("notifications/register-token")
    Call<Map<String, Object>> registerDeviceToken(@Body Map<String, Object> body);
}

package com.example.meshlink.social;

import android.content.Context;
import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FollowManager {

    private static final String PREF_NAME = "meshlink_social_graph";
    private static final String KEY_FOLLOWING_LIST = "following_peers_json";

    public static class FollowedPeer {
        public String peerId;          // e.g. mesh@8f3a1b
        public String displayName;     // e.g. Abdul
        public String publicKeyBase64; // for E2EE
        public String avatarEmoji;     // e.g. 👤
        public String bio;             // e.g. Emergency Volunteer
        public long followedAt;

        public FollowedPeer(String peerId, String displayName, String publicKeyBase64, String avatarEmoji, String bio, long followedAt) {
            this.peerId = peerId;
            this.displayName = displayName;
            this.publicKeyBase64 = publicKeyBase64;
            this.avatarEmoji = avatarEmoji;
            this.bio = bio;
            this.followedAt = followedAt;
        }

        public JSONObject toJson() {
            try {
                JSONObject obj = new JSONObject();
                obj.put("peer_id", peerId);
                obj.put("name", displayName);
                obj.put("pub", publicKeyBase64);
                obj.put("avatar", avatarEmoji);
                obj.put("bio", bio);
                obj.put("time", followedAt);
                return obj;
            } catch (Exception e) {
                return new JSONObject();
            }
        }

        public static FollowedPeer fromJson(JSONObject obj) {
            return new FollowedPeer(
                    obj.optString("peer_id"),
                    obj.optString("name"),
                    obj.optString("pub"),
                    obj.optString("avatar", "👤"),
                    obj.optString("bio", ""),
                    obj.optLong("time", System.currentTimeMillis())
            );
        }
    }

    private static FollowManager instance;
    private final SharedPreferences prefs;
    private final Map<String, FollowedPeer> followingMap = new HashMap<>();

    public static synchronized FollowManager getInstance(Context context) {
        if (instance == null) {
            instance = new FollowManager(context.getApplicationContext());
        }
        return instance;
    }

    private FollowManager(Context context) {
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        loadFollowing();
    }

    private void loadFollowing() {
        followingMap.clear();
        String jsonStr = prefs.getString(KEY_FOLLOWING_LIST, "[]");
        try {
            JSONArray arr = new JSONArray(jsonStr);
            for (int i = 0; i < arr.length(); i++) {
                FollowedPeer p = FollowedPeer.fromJson(arr.getJSONObject(i));
                followingMap.put(p.peerId, p);
            }
        } catch (Exception ignored) {}
    }

    private void saveFollowing() {
        JSONArray arr = new JSONArray();
        for (FollowedPeer p : followingMap.values()) {
            arr.put(p.toJson());
        }
        prefs.edit().putString(KEY_FOLLOWING_LIST, arr.toString()).apply();
    }

    public boolean isFollowing(String peerId) {
        return followingMap.containsKey(peerId);
    }

    public void followPeer(String peerId, String name, String publicKeyBase64, String avatar, String bio) {
        FollowedPeer p = new FollowedPeer(peerId, name, publicKeyBase64, avatar, bio, System.currentTimeMillis());
        followingMap.put(peerId, p);
        if (name != null && !name.isEmpty()) {
            followingMap.put(name, p);
            followingMap.put(name.toLowerCase(), p);
        }
        saveFollowing();
    }

    public void unfollowPeer(String peerId) {
        followingMap.remove(peerId);
        saveFollowing();
    }

    public FollowedPeer getPeer(String peerId) {
        if (peerId == null || peerId.isEmpty()) return null;
        if (followingMap.containsKey(peerId)) return followingMap.get(peerId);
        String clean = peerId.trim().toLowerCase();
        if (followingMap.containsKey(clean)) return followingMap.get(clean);
        for (FollowedPeer p : followingMap.values()) {
            if (p.displayName != null && (p.displayName.equalsIgnoreCase(peerId) || p.displayName.equalsIgnoreCase(clean))) return p;
            if (p.peerId != null && (p.peerId.equalsIgnoreCase(peerId) || p.peerId.equalsIgnoreCase(clean))) return p;
        }
        return null;
    }

    public List<FollowedPeer> getAllFollowing() {
        return new ArrayList<>(followingMap.values());
    }

    public int getFollowingCount() {
        return followingMap.size();
    }
}

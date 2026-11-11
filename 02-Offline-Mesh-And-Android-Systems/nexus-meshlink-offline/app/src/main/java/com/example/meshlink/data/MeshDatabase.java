package com.example.meshlink.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

public class MeshDatabase extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "meshlink_store.db";
    private static final int DATABASE_VERSION = 2;

    public static final String TABLE_MESSAGES = "messages";
    public static final String COL_MSG_ID = "msg_id";
    public static final String COL_SENDER = "sender";
    public static final String COL_TARGET = "target";
    public static final String COL_CONTENT = "content";
    public static final String COL_TIMESTAMP = "timestamp";
    public static final String COL_STATUS = "status";
    public static final String COL_MSG_TYPE = "msg_type";
    public static final String COL_MEDIA_PATH = "media_path";
    public static final String COL_ROUTING = "routing_mode";
    public static final String COL_HOP_COUNT = "hop_count";

    public static final String TABLE_SOS = "local_sos";
    public static final String COL_EVENT_ID = "event_id";
    public static final String COL_ORIGIN_DEV = "origin_dev";
    public static final String COL_USER_ID = "user_id";
    public static final String COL_USER_NAME = "user_name";
    public static final String COL_USER_PHONE = "user_phone";
    public static final String COL_SOS_TYPE = "sos_type";
    public static final String COL_SEVERITY = "severity";
    public static final String COL_DESCRIPTION = "description";
    public static final String COL_PEOPLE_COUNT = "people_count";
    public static final String COL_INJURED_COUNT = "injured_count";
    public static final String COL_LATITUDE = "latitude";
    public static final String COL_LONGITUDE = "longitude";
    public static final String COL_ACCURACY = "accuracy";
    public static final String COL_SOS_STATUS = "status";
    public static final String COL_SOURCE = "source";
    public static final String COL_SOS_HOP = "hop_count";
    public static final String COL_RELAY_PATH = "relay_path";
    public static final String COL_CREATED_AT = "created_at";
    public static final String COL_SYNCED = "synced";

    public static final String TABLE_CALLS = "call_logs";
    public static final String COL_CALL_ID = "call_id";
    public static final String COL_CALL_PEER_ID = "peer_id";
    public static final String COL_CALL_PEER_NAME = "peer_name";
    public static final String COL_CALL_TYPE = "call_type";
    public static final String COL_CALL_DIR = "direction";
    public static final String COL_CALL_DURATION = "duration_seconds";
    public static final String COL_CALL_TIMESTAMP = "timestamp";
    public static final String COL_CALL_TRANSPORT = "transport";

    public MeshDatabase(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String createMessagesTable = "CREATE TABLE " + TABLE_MESSAGES + " ("
                + COL_MSG_ID + " TEXT PRIMARY KEY, "
                + COL_SENDER + " TEXT, "
                + COL_TARGET + " TEXT, "
                + COL_CONTENT + " TEXT, "
                + COL_TIMESTAMP + " INTEGER, "
                + COL_STATUS + " TEXT, "
                + COL_MSG_TYPE + " TEXT, "
                + COL_MEDIA_PATH + " TEXT, "
                + COL_ROUTING + " TEXT, "
                + COL_HOP_COUNT + " INTEGER)";
        db.execSQL(createMessagesTable);

        String createSosTable = "CREATE TABLE IF NOT EXISTS " + TABLE_SOS + " ("
                + COL_EVENT_ID + " TEXT PRIMARY KEY, "
                + COL_ORIGIN_DEV + " TEXT, "
                + COL_USER_ID + " TEXT, "
                + COL_USER_NAME + " TEXT, "
                + COL_USER_PHONE + " TEXT, "
                + COL_SOS_TYPE + " TEXT, "
                + COL_SEVERITY + " TEXT, "
                + COL_DESCRIPTION + " TEXT, "
                + COL_PEOPLE_COUNT + " INTEGER, "
                + COL_INJURED_COUNT + " INTEGER, "
                + COL_LATITUDE + " REAL, "
                + COL_LONGITUDE + " REAL, "
                + COL_ACCURACY + " REAL, "
                + COL_SOS_STATUS + " TEXT, "
                + COL_SOURCE + " TEXT, "
                + COL_SOS_HOP + " INTEGER, "
                + COL_RELAY_PATH + " TEXT, "
                + COL_CREATED_AT + " INTEGER, "
                + COL_SYNCED + " INTEGER)";
        db.execSQL(createSosTable);

        String createCallsTable = "CREATE TABLE IF NOT EXISTS " + TABLE_CALLS + " ("
                + COL_CALL_ID + " TEXT PRIMARY KEY, "
                + COL_CALL_PEER_ID + " TEXT, "
                + COL_CALL_PEER_NAME + " TEXT, "
                + COL_CALL_TYPE + " TEXT, "
                + COL_CALL_DIR + " TEXT, "
                + COL_CALL_DURATION + " INTEGER, "
                + COL_CALL_TIMESTAMP + " INTEGER, "
                + COL_CALL_TRANSPORT + " TEXT)";
        db.execSQL(createCallsTable);
    }

    @Override
    public void onOpen(SQLiteDatabase db) {
        super.onOpen(db);
        String createCallsTable = "CREATE TABLE IF NOT EXISTS " + TABLE_CALLS + " ("
                + COL_CALL_ID + " TEXT PRIMARY KEY, "
                + COL_CALL_PEER_ID + " TEXT, "
                + COL_CALL_PEER_NAME + " TEXT, "
                + COL_CALL_TYPE + " TEXT, "
                + COL_CALL_DIR + " TEXT, "
                + COL_CALL_DURATION + " INTEGER, "
                + COL_CALL_TIMESTAMP + " INTEGER, "
                + COL_CALL_TRANSPORT + " TEXT)";
        db.execSQL(createCallsTable);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        String createCallsTable = "CREATE TABLE IF NOT EXISTS " + TABLE_CALLS + " ("
                + COL_CALL_ID + " TEXT PRIMARY KEY, "
                + COL_CALL_PEER_ID + " TEXT, "
                + COL_CALL_PEER_NAME + " TEXT, "
                + COL_CALL_TYPE + " TEXT, "
                + COL_CALL_DIR + " TEXT, "
                + COL_CALL_DURATION + " INTEGER, "
                + COL_CALL_TIMESTAMP + " INTEGER, "
                + COL_CALL_TRANSPORT + " TEXT)";
        db.execSQL(createCallsTable);
    }

    public void insertOrUpdateMessage(ChatMessageModel msg) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_MSG_ID, msg.msgId);
        cv.put(COL_SENDER, msg.sender);
        cv.put(COL_TARGET, msg.target);
        cv.put(COL_CONTENT, msg.content);
        cv.put(COL_TIMESTAMP, msg.timestamp);
        cv.put(COL_STATUS, msg.status);
        cv.put(COL_MSG_TYPE, msg.msgType);
        cv.put(COL_MEDIA_PATH, msg.mediaPath);
        cv.put(COL_ROUTING, msg.routingMode);
        cv.put(COL_HOP_COUNT, msg.hopCount);
        db.insertWithOnConflict(TABLE_MESSAGES, null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public void updateMessageStatus(String msgId, String status) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_STATUS, status);
        db.update(TABLE_MESSAGES, cv, COL_MSG_ID + "=?", new String[]{msgId});
    }

    public boolean messageExists(String msgId) {
        if (msgId == null || msgId.isEmpty()) return false;
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = null;
        try {
            cursor = db.rawQuery("SELECT 1 FROM " + TABLE_MESSAGES + " WHERE " + COL_MSG_ID + "=? LIMIT 1", new String[]{msgId});
            return cursor != null && cursor.moveToFirst();
        } catch (Exception e) {
            return false;
        } finally {
            if (cursor != null) cursor.close();
        }
    }

    public List<ChatMessageModel> getConversation(String myId, String peerId) {
        List<ChatMessageModel> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        String query;
        String[] args;

        if (peerId.equals("ALL")) {
            query = "SELECT * FROM " + TABLE_MESSAGES + " WHERE " + COL_TARGET + "='ALL' ORDER BY " + COL_TIMESTAMP + " ASC";
            args = null;
        } else {
            String cleanPeer = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(peerId);
            String cleanMy = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(myId);

            query = "SELECT * FROM " + TABLE_MESSAGES + " WHERE "
                    + "(" + COL_TARGET + "!='ALL') AND ("
                    + "(LOWER(" + COL_SENDER + ")=LOWER(?) AND LOWER(" + COL_TARGET + ")=LOWER(?)) OR "
                    + "(LOWER(" + COL_SENDER + ")=LOWER(?) AND LOWER(" + COL_TARGET + ")=LOWER(?)) OR "
                    + "(LOWER(" + COL_SENDER + ")=LOWER(?) AND LOWER(" + COL_TARGET + ")=LOWER(?)) OR "
                    + "(LOWER(" + COL_SENDER + ")=LOWER(?) AND LOWER(" + COL_TARGET + ")=LOWER(?))"
                    + ") ORDER BY " + COL_TIMESTAMP + " ASC";
            args = new String[]{myId, peerId, peerId, myId, cleanMy, cleanPeer, cleanPeer, cleanMy};
        }

        Cursor c = db.rawQuery(query, args);
        if (c.moveToFirst()) {
            do {
                list.add(cursorToMessage(c));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public List<ContactModel> getRecentChats(String myId) {
        List<ContactModel> contacts = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();

        String cleanMy = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(myId);

        // Query messages ordered by timestamp descending
        String query = "SELECT " + COL_SENDER + ", " + COL_TARGET + ", " + COL_CONTENT + ", " 
                + COL_TIMESTAMP + ", " + COL_STATUS + ", " + COL_ROUTING + ", " + COL_MSG_TYPE 
                + " FROM " + TABLE_MESSAGES 
                + " ORDER BY " + COL_TIMESTAMP + " DESC";

        Cursor c = db.rawQuery(query, null);
        java.util.Set<String> seenCleanPeers = new java.util.HashSet<>();

        if (c.moveToFirst()) {
            do {
                String sender = c.getString(0);
                String target = c.getString(1);

                String rawPeer = (sender.equalsIgnoreCase(myId) || sender.equalsIgnoreCase(cleanMy)) ? target : sender;
                String cleanPeer = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(rawPeer);

                if ("ALL".equalsIgnoreCase(rawPeer)) {
                    cleanPeer = "ALL";
                }

                // Never display the current user as a chat contact
                if (cleanPeer.equalsIgnoreCase(myId) || cleanPeer.equalsIgnoreCase(cleanMy)) {
                    continue;
                }

                if (!seenCleanPeers.contains(cleanPeer.toLowerCase())) {
                    seenCleanPeers.add(cleanPeer.toLowerCase());
                    String content = c.getString(2);
                    long time = c.getLong(3);
                    String routing = c.getString(5);
                    String msgType = c.getString(6);

                    String preview = content;
                    if (ChatMessageModel.TYPE_IMAGE.equals(msgType)) preview = "[Photo]";
                    else if (ChatMessageModel.TYPE_VOICE.equals(msgType)) preview = "[Voice message]";
                    else if (ChatMessageModel.TYPE_CALL.equals(msgType)) preview = "[Call]";

                    String avatar = cleanPeer.equals("ALL") ? "ALL" : cleanPeer.substring(0, Math.min(1, cleanPeer.length())).toUpperCase();
                    String displayName = cleanPeer.equals("ALL") ? "Public Broadcast Channel" : cleanPeer;

                    contacts.add(new ContactModel(cleanPeer, displayName, avatar, preview, time, 0, false, routing));
                }
            } while (c.moveToNext());
        }
        c.close();
        return contacts;
    }

    private ChatMessageModel cursorToMessage(Cursor c) {
        return new ChatMessageModel(
                c.getString(c.getColumnIndexOrThrow(COL_MSG_ID)),
                c.getString(c.getColumnIndexOrThrow(COL_SENDER)),
                c.getString(c.getColumnIndexOrThrow(COL_TARGET)),
                c.getString(c.getColumnIndexOrThrow(COL_CONTENT)),
                c.getLong(c.getColumnIndexOrThrow(COL_TIMESTAMP)),
                c.getString(c.getColumnIndexOrThrow(COL_STATUS)),
                c.getString(c.getColumnIndexOrThrow(COL_MSG_TYPE)),
                c.getString(c.getColumnIndexOrThrow(COL_MEDIA_PATH)),
                c.getString(c.getColumnIndexOrThrow(COL_ROUTING)),
                c.getInt(c.getColumnIndexOrThrow(COL_HOP_COUNT))
        );
    }

    public void insertOrUpdateSOS(LocalSosModel sos) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_EVENT_ID, sos.eventId);
        cv.put(COL_ORIGIN_DEV, sos.originDeviceId);
        cv.put(COL_USER_ID, sos.userId);
        cv.put(COL_USER_NAME, sos.userName);
        cv.put(COL_USER_PHONE, sos.userPhone);
        cv.put(COL_SOS_TYPE, sos.type);
        cv.put(COL_SEVERITY, sos.severity);
        cv.put(COL_DESCRIPTION, sos.description);
        cv.put(COL_PEOPLE_COUNT, sos.peopleCount);
        cv.put(COL_INJURED_COUNT, sos.injuredCount);
        cv.put(COL_LATITUDE, sos.latitude);
        cv.put(COL_LONGITUDE, sos.longitude);
        cv.put(COL_ACCURACY, sos.accuracy);
        cv.put(COL_SOS_STATUS, sos.status);
        cv.put(COL_SOURCE, sos.source);
        cv.put(COL_SOS_HOP, sos.hopCount);
        cv.put(COL_RELAY_PATH, sos.relayPath);
        cv.put(COL_CREATED_AT, sos.createdAt);
        cv.put(COL_SYNCED, sos.synced ? 1 : 0);
        db.insertWithOnConflict(TABLE_SOS, null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public void insertCallLog(CallModel call) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_CALL_ID, call.callId);
        cv.put(COL_CALL_PEER_ID, call.peerId);
        cv.put(COL_CALL_PEER_NAME, call.peerName);
        cv.put(COL_CALL_TYPE, call.callType);
        cv.put(COL_CALL_DIR, call.direction);
        cv.put(COL_CALL_DURATION, call.durationSeconds);
        cv.put(COL_CALL_TIMESTAMP, call.timestamp);
        cv.put(COL_CALL_TRANSPORT, call.transport);
        db.insertWithOnConflict(TABLE_CALLS, null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public List<CallModel> getAllCalls() {
        List<CallModel> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM " + TABLE_CALLS + " ORDER BY " + COL_CALL_TIMESTAMP + " DESC", null);
        if (c.moveToFirst()) {
            do {
                list.add(new CallModel(
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_ID)),
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_PEER_ID)),
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_PEER_NAME)),
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_TYPE)),
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_DIR)),
                        c.getInt(c.getColumnIndexOrThrow(COL_CALL_DURATION)),
                        c.getLong(c.getColumnIndexOrThrow(COL_CALL_TIMESTAMP)),
                        c.getString(c.getColumnIndexOrThrow(COL_CALL_TRANSPORT))
                ));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public void clearAllData() {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_MESSAGES, null, null);
        db.delete(TABLE_SOS, null, null);
        db.delete(TABLE_CALLS, null, null);
    }
}

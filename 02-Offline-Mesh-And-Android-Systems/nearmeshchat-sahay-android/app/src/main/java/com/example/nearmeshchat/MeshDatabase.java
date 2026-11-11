package com.example.nearmeshchat;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

public class MeshDatabase extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "nearmesh_store.db";
    private static final int DATABASE_VERSION = 2;

    public static final String TABLE_MESSAGES = "messages";
    public static final String COL_MSG_ID = "msg_id";
    public static final String COL_SENDER = "sender";
    public static final String COL_TARGET = "target";
    public static final String COL_CONTENT = "content";
    public static final String COL_TIMESTAMP = "timestamp";
    public static final String COL_STATUS = "status"; // PENDING, DELIVERED, SEEN

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
    public static final String COL_HOP_COUNT = "hop_count";
    public static final String COL_RELAY_PATH = "relay_path";
    public static final String COL_CREATED_AT = "created_at";
    public static final String COL_SYNCED = "synced";

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
                + COL_STATUS + " TEXT)";
        db.execSQL(createMessagesTable);

        createSosTable(db);
    }

    private void createSosTable(SQLiteDatabase db) {
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
                + COL_HOP_COUNT + " INTEGER, "
                + COL_RELAY_PATH + " TEXT, "
                + COL_CREATED_AT + " INTEGER, "
                + COL_SYNCED + " INTEGER)";
        db.execSQL(createSosTable);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        if (oldVersion < 2) {
            createSosTable(db);
        }
    }

    public void insertOrUpdateMessage(String msgId, String sender, String target, String content, long timestamp, String status) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_MSG_ID, msgId);
        cv.put(COL_SENDER, sender);
        cv.put(COL_TARGET, target);
        cv.put(COL_CONTENT, content);
        cv.put(COL_TIMESTAMP, timestamp);
        cv.put(COL_STATUS, status);
        db.insertWithOnConflict(TABLE_MESSAGES, null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public void updateMessageStatus(String msgId, String status) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_STATUS, status);
        db.update(TABLE_MESSAGES, cv, COL_MSG_ID + "=?", new String[]{msgId});
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
            query = "SELECT * FROM " + TABLE_MESSAGES + " WHERE (" + COL_SENDER + "=? AND " + COL_TARGET + "=?) OR ("
                    + COL_SENDER + "=? AND " + COL_TARGET + "=?) ORDER BY " + COL_TIMESTAMP + " ASC";
            args = new String[]{myId, peerId, peerId, myId};
        }

        Cursor c = db.rawQuery(query, args);
        if (c.moveToFirst()) {
            do {
                list.add(new ChatMessageModel(
                        c.getString(c.getColumnIndexOrThrow(COL_MSG_ID)),
                        c.getString(c.getColumnIndexOrThrow(COL_SENDER)),
                        c.getString(c.getColumnIndexOrThrow(COL_TARGET)),
                        c.getString(c.getColumnIndexOrThrow(COL_CONTENT)),
                        c.getLong(c.getColumnIndexOrThrow(COL_TIMESTAMP)),
                        c.getString(c.getColumnIndexOrThrow(COL_STATUS))
                ));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public List<ChatMessageModel> getPendingMessagesForPeer(String peerId) {
        List<ChatMessageModel> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM " + TABLE_MESSAGES + " WHERE " + COL_TARGET + "=? AND " + COL_STATUS + "='PENDING'", new String[]{peerId});
        if (c.moveToFirst()) {
            do {
                list.add(new ChatMessageModel(
                        c.getString(c.getColumnIndexOrThrow(COL_MSG_ID)),
                        c.getString(c.getColumnIndexOrThrow(COL_SENDER)),
                        c.getString(c.getColumnIndexOrThrow(COL_TARGET)),
                        c.getString(c.getColumnIndexOrThrow(COL_CONTENT)),
                        c.getLong(c.getColumnIndexOrThrow(COL_TIMESTAMP)),
                        c.getString(c.getColumnIndexOrThrow(COL_STATUS))
                ));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public void removeGarbagePacket(String msgId) {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_MESSAGES, COL_MSG_ID + "=? AND " + COL_STATUS + "='PENDING'", new String[]{msgId});
    }

    // --- SOS Operations ---

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
        cv.put(COL_HOP_COUNT, sos.hopCount);
        cv.put(COL_RELAY_PATH, sos.relayPath);
        cv.put(COL_CREATED_AT, sos.createdAt);
        cv.put(COL_SYNCED, sos.synced ? 1 : 0);
        db.insertWithOnConflict(TABLE_SOS, null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public void markSOSSynced(String eventId) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put(COL_SYNCED, 1);
        db.update(TABLE_SOS, cv, COL_EVENT_ID + "=?", new String[]{eventId});
    }

    public List<LocalSosModel> getPendingSOS() {
        List<LocalSosModel> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM " + TABLE_SOS + " WHERE " + COL_SYNCED + "=0", null);
        if (c.moveToFirst()) {
            do {
                list.add(cursorToSOS(c));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public List<LocalSosModel> getAllSOS() {
        List<LocalSosModel> list = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM " + TABLE_SOS + " ORDER BY " + COL_CREATED_AT + " DESC", null);
        if (c.moveToFirst()) {
            do {
                list.add(cursorToSOS(c));
            } while (c.moveToNext());
        }
        c.close();
        return list;
    }

    public LocalSosModel getLatestSOS() {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor c = db.rawQuery("SELECT * FROM " + TABLE_SOS + " ORDER BY " + COL_CREATED_AT + " DESC LIMIT 1", null);
        LocalSosModel model = null;
        if (c.moveToFirst()) {
            model = cursorToSOS(c);
        }
        c.close();
        return model;
    }

    private LocalSosModel cursorToSOS(Cursor c) {
        return new LocalSosModel(
                c.getString(c.getColumnIndexOrThrow(COL_EVENT_ID)),
                c.getString(c.getColumnIndexOrThrow(COL_ORIGIN_DEV)),
                c.getString(c.getColumnIndexOrThrow(COL_USER_ID)),
                c.getString(c.getColumnIndexOrThrow(COL_USER_NAME)),
                c.getString(c.getColumnIndexOrThrow(COL_USER_PHONE)),
                c.getString(c.getColumnIndexOrThrow(COL_SOS_TYPE)),
                c.getString(c.getColumnIndexOrThrow(COL_SEVERITY)),
                c.getString(c.getColumnIndexOrThrow(COL_DESCRIPTION)),
                c.getInt(c.getColumnIndexOrThrow(COL_PEOPLE_COUNT)),
                c.getInt(c.getColumnIndexOrThrow(COL_INJURED_COUNT)),
                c.getDouble(c.getColumnIndexOrThrow(COL_LATITUDE)),
                c.getDouble(c.getColumnIndexOrThrow(COL_LONGITUDE)),
                c.getFloat(c.getColumnIndexOrThrow(COL_ACCURACY)),
                c.getString(c.getColumnIndexOrThrow(COL_SOS_STATUS)),
                c.getString(c.getColumnIndexOrThrow(COL_SOURCE)),
                c.getInt(c.getColumnIndexOrThrow(COL_HOP_COUNT)),
                c.getString(c.getColumnIndexOrThrow(COL_RELAY_PATH)),
                c.getLong(c.getColumnIndexOrThrow(COL_CREATED_AT)),
                c.getInt(c.getColumnIndexOrThrow(COL_SYNCED)) == 1
        );
    }
}
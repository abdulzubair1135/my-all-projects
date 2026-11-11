package com.example.emergencyrecorder.call

import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.CallLog
import android.provider.ContactsContract
import android.util.Log
import androidx.core.content.ContextCompat

data class CallerDetails(
    val name: String?,
    val number: String?
)

object ContactHelper {

    private const val TAG = "ContactHelper"

    fun getContactName(context: Context, phoneNumber: String?): String? {
        if (phoneNumber.isNullOrBlank()) return null

        val hasPermission = ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.READ_CONTACTS
        ) == PackageManager.PERMISSION_GRANTED

        if (!hasPermission) return null

        val uri = Uri.withAppendedPath(
            ContactsContract.PhoneLookup.CONTENT_FILTER_URI,
            Uri.encode(phoneNumber)
        )
        val projection = arrayOf(ContactsContract.PhoneLookup.DISPLAY_NAME)

        try {
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val nameIndex = cursor.getColumnIndex(ContactsContract.PhoneLookup.DISPLAY_NAME)
                    if (nameIndex != -1) {
                        val name = cursor.getString(nameIndex)
                        if (!name.isNullOrBlank()) return name
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error looking up contact for $phoneNumber", e)
        }

        return null
    }

    /**
     * Queries CallLog.Calls to get the most recent incoming or outgoing call details.
     * Works reliably on modern Android for both incoming and outgoing calls.
     */
    fun getLatestCallDetails(context: Context): CallerDetails? {
        val hasPermission = ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.READ_CALL_LOG
        ) == PackageManager.PERMISSION_GRANTED

        if (!hasPermission) return null

        val projection = arrayOf(
            CallLog.Calls.NUMBER,
            CallLog.Calls.CACHED_NAME,
            CallLog.Calls.DATE
        )

        try {
            context.contentResolver.query(
                CallLog.Calls.CONTENT_URI,
                projection,
                null,
                null,
                "${CallLog.Calls.DATE} DESC"
            )?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val numberCol = cursor.getColumnIndex(CallLog.Calls.NUMBER)
                    val nameCol = cursor.getColumnIndex(CallLog.Calls.CACHED_NAME)

                    val number = if (numberCol != -1) cursor.getString(numberCol) else null
                    var name = if (nameCol != -1) cursor.getString(nameCol) else null

                    if (name.isNullOrBlank() && !number.isNullOrBlank()) {
                        name = getContactName(context, number)
                    }

                    Log.d(TAG, "Found latest call: name=$name, number=$number")
                    return CallerDetails(name, number)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error querying CallLog for latest call", e)
        }

        return null
    }

    fun sanitizeForFilename(input: String): String {
        return input.replace(Regex("[^a-zA-Z0-9_-]"), "_").take(30)
    }
}

package com.example.lifevault.collector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.provider.CallLog
import android.provider.Telephony
import androidx.core.content.ContextCompat
import com.example.lifevault.repository.VaultRepository

class TelecomCollector(
    private val context: Context,
    private val repository: VaultRepository
) {

    suspend fun scanSmsLogs(sinceTimestamp: Long = System.currentTimeMillis() - 30 * 86400000L) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_SMS) != PackageManager.PERMISSION_GRANTED) {
            return
        }

        try {
            val projection = arrayOf(
                Telephony.Sms._ID,
                Telephony.Sms.ADDRESS,
                Telephony.Sms.BODY,
                Telephony.Sms.DATE,
                Telephony.Sms.TYPE
            )
            val selection = "${Telephony.Sms.DATE} > ?"
            val selectionArgs = arrayOf(sinceTimestamp.toString())

            val cursor = context.contentResolver.query(
                Telephony.Sms.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                "${Telephony.Sms.DATE} ASC"
            )

            cursor?.use { c ->
                val addressIdx = c.getColumnIndex(Telephony.Sms.ADDRESS)
                val bodyIdx = c.getColumnIndex(Telephony.Sms.BODY)
                val dateIdx = c.getColumnIndex(Telephony.Sms.DATE)

                while (c.moveToNext()) {
                    val party = if (addressIdx >= 0) c.getString(addressIdx) else null
                    val body = if (bodyIdx >= 0) c.getString(bodyIdx) else null
                    val timestamp = if (dateIdx >= 0) c.getLong(dateIdx) else System.currentTimeMillis()

                    repository.enqueueTelecom(
                        type = "sms",
                        party = party,
                        body = body,
                        duration = null,
                        timestamp = timestamp
                    )
                }
            }
        } catch (_: SecurityException) {
            // Graceful failure when permissions or OEM restrictions prevent telecom access
        } catch (_: Exception) {
            // Ignore format errors
        }
    }

    suspend fun scanCallLogs(sinceTimestamp: Long = System.currentTimeMillis() - 30 * 86400000L) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) != PackageManager.PERMISSION_GRANTED) {
            return
        }

        try {
            val projection = arrayOf(
                CallLog.Calls._ID,
                CallLog.Calls.NUMBER,
                CallLog.Calls.DURATION,
                CallLog.Calls.DATE,
                CallLog.Calls.TYPE
            )
            val selection = "${CallLog.Calls.DATE} > ?"
            val selectionArgs = arrayOf(sinceTimestamp.toString())

            val cursor = context.contentResolver.query(
                CallLog.Calls.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                "${CallLog.Calls.DATE} ASC"
            )

            cursor?.use { c ->
                val numberIdx = c.getColumnIndex(CallLog.Calls.NUMBER)
                val durationIdx = c.getColumnIndex(CallLog.Calls.DURATION)
                val dateIdx = c.getColumnIndex(CallLog.Calls.DATE)
                val typeIdx = c.getColumnIndex(CallLog.Calls.TYPE)

                while (c.moveToNext()) {
                    val number = if (numberIdx >= 0) c.getString(numberIdx) else null
                    val duration = if (durationIdx >= 0) c.getLong(durationIdx) else null
                    val timestamp = if (dateIdx >= 0) c.getLong(dateIdx) else System.currentTimeMillis()
                    val callType = if (typeIdx >= 0) {
                        when (c.getInt(typeIdx)) {
                            CallLog.Calls.INCOMING_TYPE -> "call_incoming"
                            CallLog.Calls.OUTGOING_TYPE -> "call_outgoing"
                            CallLog.Calls.MISSED_TYPE -> "call_missed"
                            else -> "call"
                        }
                    } else "call"

                    repository.enqueueTelecom(
                        type = callType,
                        party = number,
                        body = null,
                        duration = duration,
                        timestamp = timestamp
                    )
                }
            }
        } catch (_: SecurityException) {
            // Graceful failure on restricted call log access
        } catch (_: Exception) {
            // Ignore format errors
        }
    }
}

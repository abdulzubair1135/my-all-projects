package com.example.emergencyrecorder.call

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.telephony.TelephonyManager
import android.util.Log
import com.example.emergencyrecorder.recording.RecordingController
import com.example.emergencyrecorder.settings.AppSettings

class CallReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != TelephonyManager.ACTION_PHONE_STATE_CHANGED) {
            return
        }

        val settings = AppSettings.getInstance(context)
        if (!settings.isAutoCallRecordingEnabled) {
            return
        }

        val stateStr = intent.getStringExtra(TelephonyManager.EXTRA_STATE) ?: return
        val incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)

        Log.d(TAG, "Phone state changed: state=$stateStr, incomingNumber=$incomingNumber")

        when (stateStr) {
            TelephonyManager.EXTRA_STATE_RINGING -> {
                if (!incomingNumber.isNullOrBlank()) {
                    cachedNumber = incomingNumber
                    cachedName = ContactHelper.getContactName(context, incomingNumber)
                    Log.d(TAG, "Incoming ringing: number=$cachedNumber, name=$cachedName")
                }
            }

            TelephonyManager.EXTRA_STATE_OFFHOOK -> {
                // Call connected (either incoming answered or outgoing placed)
                if (!isCallRecordingActive) {
                    // If outgoing, cachedNumber is null. Query CallLog to resolve the dialed number!
                    if (cachedNumber.isNullOrBlank()) {
                        val latest = ContactHelper.getLatestCallDetails(context)
                        if (latest != null) {
                            cachedNumber = latest.number
                            cachedName = latest.name
                            Log.d(TAG, "Resolved outgoing call from CallLog: number=$cachedNumber, name=$cachedName")
                        }
                    }

                    val nameTag = if (!cachedName.isNullOrBlank()) {
                        ContactHelper.sanitizeForFilename(cachedName!!)
                    } else if (!cachedNumber.isNullOrBlank()) {
                        val resolved = ContactHelper.getContactName(context, cachedNumber)
                        if (!resolved.isNullOrBlank()) ContactHelper.sanitizeForFilename(resolved) else "Unknown"
                    } else {
                        "Unknown"
                    }

                    val numberTag = if (!cachedNumber.isNullOrBlank()) {
                        ContactHelper.sanitizeForFilename(cachedNumber!!)
                    } else {
                        "Call"
                    }

                    val prefix = "Call_${nameTag}_$numberTag"
                    Log.i(TAG, "Starting auto-call recording with prefix: $prefix")

                    isCallRecordingActive = true
                    RecordingController.requestStartRecording(context, prefix)
                }
            }

            TelephonyManager.EXTRA_STATE_IDLE -> {
                // Call ended
                if (isCallRecordingActive) {
                    Log.i(TAG, "Call ended. Stopping auto-call recording.")
                    isCallRecordingActive = false
                    cachedNumber = null
                    cachedName = null
                    RecordingController.requestStopRecording(context)
                }
            }
        }
    }

    companion object {
        private const val TAG = "CallReceiver"
        private var cachedNumber: String? = null
        private var cachedName: String? = null
        private var isCallRecordingActive = false
    }
}

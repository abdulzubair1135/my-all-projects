package com.example.emergencyrecorder.accessibility

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.media.VolumeProvider
import android.media.session.MediaSession
import android.media.session.PlaybackState
import android.os.Build
import android.os.IBinder
import android.os.SystemClock
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.emergencyrecorder.MainActivity
import com.example.emergencyrecorder.R
import com.example.emergencyrecorder.recording.RecordingController
import com.example.emergencyrecorder.settings.AppSettings

/**
 * Foreground service that maintains an active MediaSession with a VolumeProvider
 * and a silent AudioTrack. This guarantees that Android routes KEYCODE_VOLUME_DOWN
 * to our application even when the phone screen is completely OFF and black.
 */
class BackgroundTriggerService : Service() {

    private var mediaSession: MediaSession? = null
    private var audioTrack: AudioTrack? = null
    private var isPlayingSilence = false
    private var silentThread: Thread? = null

    private lateinit var appSettings: AppSettings
    private lateinit var detector: DoublePressDetector

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "BackgroundTriggerService onCreate")
        appSettings = AppSettings.getInstance(this)
        detector = DoublePressDetector(windowMs = appSettings.doublePressIntervalMs)

        createNotificationChannel()
        startInForeground()
        setupMediaSessionWithVolumeProvider()
        startSilentAudioTrack()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Emergency Shortcut Listener",
                NotificationManager.IMPORTANCE_MIN
            ).apply {
                description = "Keeps hardware Volume Down shortcut active while screen is off."
                setShowBadge(false)
                lockscreenVisibility = Notification.VISIBILITY_SECRET
            }
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
    }

    private fun startInForeground() {
        val openIntent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_mic)
            .setContentTitle("Emergency Shortcut Ready")
            .setContentText("Volume Down double-press active (Screen-off enabled)")
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun setupMediaSessionWithVolumeProvider() {
        try {
            val session = MediaSession(this, "EmergencyRecorderMediaSession")

            val volumeProvider = object : VolumeProvider(
                VOLUME_CONTROL_RELATIVE,
                100,
                50
            ) {
                override fun onAdjustVolume(direction: Int) {
                    Log.i(TAG, "onAdjustVolume received: direction=$direction (screen-off active)")
                    // direction < 0 indicates Volume Down pressed
                    if (direction < 0) {
                        detector.updateWindow(appSettings.doublePressIntervalMs)
                        val now = SystemClock.elapsedRealtime()
                        val triggered = detector.onKeyDown(now)

                        Log.i(TAG, "Volume Down via VolumeProvider! Triggered=$triggered")
                        if (triggered) {
                            Log.i(TAG, "EMERGENCY TRIGGER: Screen-Off Double-press Volume Down!")
                            RecordingController.toggleRecording(applicationContext)
                        }
                    }
                }
            }

            session.setPlaybackToRemote(volumeProvider)

            val state = PlaybackState.Builder()
                .setState(PlaybackState.STATE_PLAYING, 0, 1.0f)
                .setActions(PlaybackState.ACTION_PLAY or PlaybackState.ACTION_PAUSE)
                .build()

            session.setPlaybackState(state)
            session.isActive = true
            this.mediaSession = session
            Log.i(TAG, "MediaSession and Remote VolumeProvider initialized successfully")

        } catch (e: Exception) {
            Log.e(TAG, "Failed to setup MediaSession", e)
        }
    }

    private fun startSilentAudioTrack() {
        try {
            val sampleRate = 8000
            val bufferSize = AudioTrack.getMinBufferSize(
                sampleRate,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )

            val track = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(bufferSize)
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build()

            track.play()
            this.audioTrack = track
            this.isPlayingSilence = true

            // Send silent zeros in a low-priority thread
            silentThread = Thread {
                val silentBuffer = ByteArray(bufferSize) // all zeros = absolute silence
                while (isPlayingSilence) {
                    try {
                        track.write(silentBuffer, 0, silentBuffer.size)
                        Thread.sleep(100)
                    } catch (e: InterruptedException) {
                        break
                    } catch (e: Exception) {
                        Log.w(TAG, "Silent audio write loop interrupted", e)
                    }
                }
            }.apply {
                isDaemon = true
                priority = Thread.MIN_PRIORITY
                start()
            }

            Log.i(TAG, "Silent audio track started to keep media session active during screen-off")

        } catch (e: Exception) {
            Log.e(TAG, "Failed to start silent audio track", e)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onDestroy() {
        Log.d(TAG, "BackgroundTriggerService onDestroy")
        isPlayingSilence = false
        silentThread?.interrupt()
        silentThread = null

        try {
            audioTrack?.stop()
            audioTrack?.release()
        } catch (ignored: Exception) {}
        audioTrack = null

        try {
            mediaSession?.isActive = false
            mediaSession?.release()
        } catch (ignored: Exception) {}
        mediaSession = null

        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val TAG = "BackgroundTriggerSvc"
        private const val CHANNEL_ID = "emergency_trigger_channel"
        private const val NOTIFICATION_ID = 2002

        fun start(context: Context) {
            val intent = Intent(context, BackgroundTriggerService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            val intent = Intent(context, BackgroundTriggerService::class.java)
            context.stopService(intent)
        }
    }
}

package com.projectx2.porncontroller.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.projectx2.porncontroller.MainActivity
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.R
import com.projectx2.porncontroller.domain.rules.DomainDetectionEngine
import com.projectx2.porncontroller.features.intervention.InterventionActivity
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.FileInputStream
import java.io.FileOutputStream
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.nio.ByteBuffer

class LocalVpnService : VpnService() {

    companion object {
        const val TAG = "LocalVpnService"
        const val NOTIFICATION_ID = 1001
        const val CHANNEL_ID = "vpn_protection_channel"
        const val ACTION_START = "com.projectx2.porncontroller.ACTION_START_VPN"
        const val ACTION_STOP = "com.projectx2.porncontroller.ACTION_STOP_VPN"

        @Volatile
        var isRunning: Boolean = false
            private set

        private val _isRunningFlow = MutableStateFlow(false)
        val isRunningFlow: StateFlow<Boolean> = _isRunningFlow.asStateFlow()
    }

    private var vpnInterface: ParcelFileDescriptor? = null
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)
    private val domainEngine = DomainDetectionEngine()

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                stopVpn()
                stopSelf()
                return START_NOT_STICKY
            }
            else -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ServiceCompat.startForeground(
                        this,
                        NOTIFICATION_ID,
                        buildNotification(),
                        ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
                    )
                } else {
                    startForeground(NOTIFICATION_ID, buildNotification())
                }
                startVpn()
            }
        }
        return START_STICKY
    }

    private fun startVpn() {
        if (isRunning) return
        isRunning = true
        _isRunningFlow.value = true

        serviceScope.launch {
            // Load enabled domains into detection engine
            val app = application as PornControllerApp
            val domains = app.repository.getEnabledDomains()
            domainEngine.updateDomainList(domains)

            try {
                val builder = Builder()
                    .setSession("P.RN Controller Shield")
                    .addAddress("10.1.10.1", 24)
                    .addDnsServer("10.1.10.1")
                    .addDnsServer("1.1.1.3")
                    .addDnsServer("1.0.0.3")
                    .addRoute("10.1.10.1", 32)
                    .addRoute("1.1.1.3", 32)
                    .addRoute("1.0.0.3", 32)
                    .addRoute("8.8.8.8", 32)
                    .addRoute("8.8.4.4", 32)
                    .addRoute("9.9.9.9", 32)
                    .addRoute("208.67.222.222", 32)
                    .addRoute("208.67.220.220", 32)
                    .setMtu(1500)

                val pfd = builder.establish()
                if (pfd == null) {
                    Log.e(TAG, "Failed to establish VPN interface - establish() returned null")
                    isRunning = false
                    _isRunningFlow.value = false
                    stopSelf()
                    return@launch
                }
                vpnInterface = pfd
                Log.i(TAG, "Local loopback VPN established successfully")

                // Launch packet processing loop
                runPacketLoop(pfd)
            } catch (e: Exception) {
                Log.e(TAG, "VPN startup error", e)
                stopVpn()
            }
        }
    }

    private fun runPacketLoop(pfd: ParcelFileDescriptor) {
        val inputStream = FileInputStream(pfd.fileDescriptor)
        val outputStream = FileOutputStream(pfd.fileDescriptor)
        val packet = ByteBuffer.allocate(32767)

        val upstreamSocket: DatagramSocket? = try {
            val s = DatagramSocket()
            protect(s)
            s.soTimeout = 2000
            s
        } catch (e: Exception) {
            Log.w(TAG, "Running in pure offline DNS sinkhole mode: ${e.message}")
            null
        }

        val upstreamDns: InetAddress? = try {
            InetAddress.getByName("1.1.1.3")
        } catch (_: Exception) {
            null
        }

        while (isRunning && !serviceScope.coroutineContext[Job]!!.isCancelled) {
            try {
                val length = inputStream.read(packet.array())
                if (length > 0) {
                    packet.limit(length)
                    packet.position(0)

                    // Process IPv4 UDP DNS packet
                    handlePacket(packet, length, outputStream, upstreamSocket, upstreamDns)
                    packet.clear()
                }
            } catch (e: Exception) {
                if (isRunning) {
                    Log.e(TAG, "Packet loop read error", e)
                }
                break
            }
        }

        try {
            upstreamSocket?.close()
        } catch (_: Exception) {}
    }

    private fun handlePacket(
        packet: ByteBuffer,
        length: Int,
        outputStream: FileOutputStream,
        upstreamSocket: DatagramSocket?,
        upstreamDns: InetAddress?
    ) {
        val buffer = packet.array()
        // Check if IPv4
        val versionAndIHL = buffer[0].toInt() and 0xFF
        val version = versionAndIHL shr 4
        if (version != 4) return

        val ihl = (versionAndIHL and 0x0F) * 4
        val protocol = buffer[9].toInt() and 0xFF

        // Check UDP (17)
        if (protocol != 17) return

        val udpHeaderOffset = ihl
        val destPort = ((buffer[udpHeaderOffset + 2].toInt() and 0xFF) shl 8) or
                (buffer[udpHeaderOffset + 3].toInt() and 0xFF)

        // DNS port 53
        if (destPort == 53) {
            val dnsOffset = udpHeaderOffset + 8
            val dnsLength = length - dnsOffset
            if (dnsLength <= 12) return

            val domainName = parseDnsQuestionDomain(buffer, dnsOffset)
            if (domainName.isNotBlank()) {
                if (domainEngine.isDomainBlocked(domainName)) {
                    Log.d(TAG, "BLOCKED adult domain offline: $domainName")
                    // Record in database
                    val app = application as PornControllerApp
                    serviceScope.launch {
                        app.repository.recordDomainBlocked(domainName)
                    }

                    // Kick out offensive app & pop intervention
                    try {
                        AccessibilityMonitorService.instance?.performGlobalAction(android.accessibilityservice.AccessibilityService.GLOBAL_ACTION_HOME)
                    } catch (_: Exception) {}
                    try {
                        val interventionIntent = Intent(this@LocalVpnService, InterventionActivity::class.java).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                            putExtra(InterventionActivity.EXTRA_TRIGGER_SOURCE, domainName)
                            putExtra(InterventionActivity.EXTRA_CATEGORY, "STRICT")
                            putExtra(InterventionActivity.EXTRA_CUSTOM_MSG, "Adult content is blocked. Access to '$domainName' has been terminated.")
                        }
                        startActivity(interventionIntent)
                    } catch (_: Exception) {}

                    // Return NXDOMAIN synthesized DNS response
                    val fakeResponse = createNxDomainResponse(buffer, dnsOffset, dnsLength)
                    if (fakeResponse != null) {
                        // Construct synthetic IP + UDP packet
                        val replyPacket = createUdpReplyPacket(buffer, ihl, fakeResponse)
                        outputStream.write(replyPacket)
                        return
                    }
                } else if (upstreamSocket != null && upstreamDns != null) {
                    // Safe domain: Forward to upstream safe DNS if socket available
                    try {
                        val sendData = buffer.copyOfRange(dnsOffset, length)
                        val outPacket = DatagramPacket(sendData, sendData.size, upstreamDns, 53)
                        upstreamSocket.send(outPacket)

                        val receiveBuffer = ByteArray(1500)
                        val inPacket = DatagramPacket(receiveBuffer, receiveBuffer.size)
                        upstreamSocket.receive(inPacket)

                        val replyDnsData = receiveBuffer.copyOf(inPacket.length)
                        val replyPacket = createUdpReplyPacket(buffer, ihl, replyDnsData)
                        outputStream.write(replyPacket)
                    } catch (_: Exception) {
                        // Pass-through
                    }
                }
            }
        }
    }

    private fun parseDnsQuestionDomain(buffer: ByteArray, dnsOffset: Int): String {
        val sb = StringBuilder()
        var pos = dnsOffset + 12 // Skip DNS header (12 bytes)
        val limit = buffer.size

        while (pos < limit) {
            val labelLen = buffer[pos].toInt() and 0xFF
            if (labelLen == 0) break
            if ((labelLen and 0xC0) == 0xC0) {
                // Compression pointer
                break
            }
            pos++
            if (pos + labelLen > limit) break

            for (i in 0 until labelLen) {
                sb.append(buffer[pos + i].toInt().toChar())
            }
            sb.append('.')
            pos += labelLen
        }

        return sb.toString().trimEnd('.')
    }

    private fun createNxDomainResponse(buffer: ByteArray, dnsOffset: Int, dnsLength: Int): ByteArray? {
        if (dnsLength < 12) return null
        val response = ByteArray(dnsLength)
        System.arraycopy(buffer, dnsOffset, response, 0, dnsLength)

        // Flags: QR=1 (response), Opcode=0, AA=0, TC=0, RD=1, RA=1, RCODE=3 (NXDOMAIN)
        response[2] = 0x81.toByte()
        response[3] = 0x83.toByte()

        return response
    }

    private fun createUdpReplyPacket(reqBuffer: ByteArray, ihl: Int, dnsPayload: ByteArray): ByteArray {
        val totalLength = 20 + 8 + dnsPayload.size
        val reply = ByteArray(totalLength)

        // IP Header (20 bytes)
        reply[0] = 0x45.toByte()
        reply[1] = 0x00.toByte()
        reply[2] = ((totalLength shr 8) and 0xFF).toByte()
        reply[3] = (totalLength and 0xFF).toByte()
        reply[4] = 0x00.toByte()
        reply[5] = 0x00.toByte()
        reply[6] = 0x40.toByte() // Don't fragment
        reply[7] = 0x00.toByte()
        reply[8] = 0x40.toByte() // TTL = 64
        reply[9] = 17.toByte()   // UDP

        // Swap IP addresses (dest becomes source, source becomes dest)
        System.arraycopy(reqBuffer, 16, reply, 12, 4) // Source IP = Req Dest IP
        System.arraycopy(reqBuffer, 12, reply, 16, 4) // Dest IP = Req Source IP

        // Compute IP checksum
        var sum = 0
        for (i in 0 until 20 step 2) {
            if (i == 10) continue // Skip checksum field
            sum += ((reply[i].toInt() and 0xFF) shl 8) or (reply[i + 1].toInt() and 0xFF)
        }
        while (sum shr 16 > 0) {
            sum = (sum and 0xFFFF) + (sum shr 16)
        }
        val ipChecksum = sum.inv() and 0xFFFF
        reply[10] = (ipChecksum shr 8).toByte()
        reply[11] = (ipChecksum and 0xFF).toByte()

        // UDP Header (8 bytes)
        // Swap ports
        reply[20] = reqBuffer[ihl + 2]
        reply[21] = reqBuffer[ihl + 3]
        reply[22] = reqBuffer[ihl]
        reply[23] = reqBuffer[ihl + 1]

        val udpLen = 8 + dnsPayload.size
        reply[24] = ((udpLen shr 8) and 0xFF).toByte()
        reply[25] = (udpLen and 0xFF).toByte()
        reply[26] = 0x00.toByte() // Checksum 0
        reply[27] = 0x00.toByte()

        // DNS Payload
        System.arraycopy(dnsPayload, 0, reply, 28, dnsPayload.size)

        return reply
    }

    private fun stopVpn() {
        isRunning = false
        _isRunningFlow.value = false
        serviceJob.cancel()
        try {
            vpnInterface?.close()
        } catch (_: Exception) {}
        vpnInterface = null
        stopForeground(STOP_FOREGROUND_REMOVE)
    }

    override fun onDestroy() {
        stopVpn()
        super.onDestroy()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.vpn_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.vpn_channel_desc)
                setShowBadge(false)
            }
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Adult Content Protection Active")
            .setContentText("Local offline DNS filtering is shielding your device.")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
}

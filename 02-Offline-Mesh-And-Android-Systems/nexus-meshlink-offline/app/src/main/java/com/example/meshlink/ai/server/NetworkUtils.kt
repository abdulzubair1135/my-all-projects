package com.example.meshlink.ai.server

import android.content.Context
import android.net.ConnectivityManager
import android.net.wifi.WifiManager
import android.util.Log
import java.net.Inet4Address
import java.net.NetworkInterface
import java.util.Collections

object NetworkUtils {

    private const val TAG = "PocketAI_Network"

    data class NetworkInterfaceInfo(
        val name: String,
        val displayName: String,
        val ipAddress: String,
        val isHotspotCandidate: Boolean
    )

    /**
     * Retrieves all active non-loopback IPv4 network interfaces on the device.
     */
    fun getAvailableNetworkInterfaces(): List<NetworkInterfaceInfo> {
        val list = mutableListOf<NetworkInterfaceInfo>()
        try {
            val interfaces = Collections.list(NetworkInterface.getNetworkInterfaces())
            for (iface in interfaces) {
                if (!iface.isUp || iface.isLoopback) continue

                val addrs = Collections.list(iface.inetAddresses)
                for (addr in addrs) {
                    if (addr is Inet4Address && !addr.isLoopbackAddress) {
                        val host = addr.hostAddress ?: continue
                        val name = iface.name.lowercase()
                        val isHotspot = name.contains("ap") ||
                                name.contains("swlan") ||
                                name.contains("wlan") ||
                                name.contains("softap") ||
                                host.startsWith("192.168.43.")

                        list.add(
                            NetworkInterfaceInfo(
                                name = iface.name,
                                displayName = iface.displayName,
                                ipAddress = host,
                                isHotspotCandidate = isHotspot
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error enumerating network interfaces: ${e.message}", e)
        }
        return list
    }

    /**
     * Determines the most appropriate primary IP address for PocketAI Server.
     * Prioritizes Hotspot (192.168.43.1 or AP interfaces), then Wi-Fi, then USB tethering.
     */
    fun getPrimaryIpAddress(context: Context): String {
        val interfaces = getAvailableNetworkInterfaces()
        if (interfaces.isEmpty()) {
            return "127.0.0.1"
        }

        // 1. Check for standard Android Hotspot IP (192.168.43.1 or 192.168.43.x)
        for (iface in interfaces) {
            if (iface.ipAddress.startsWith("192.168.43.")) {
                return iface.ipAddress
            }
        }

        // 2. Check for hotspot interface names (ap0, swlan0, softap0)
        for (iface in interfaces) {
            val name = iface.name.lowercase()
            if (name.contains("ap") || name.contains("softap") || name.contains("swlan")) {
                return iface.ipAddress
            }
        }

        // 3. Check for wlan0 (connected to Wi-Fi LAN)
        for (iface in interfaces) {
            if (iface.name.lowercase().contains("wlan")) {
                return iface.ipAddress
            }
        }

        // 4. Check for usb0 / rndis0 (USB tethering)
        for (iface in interfaces) {
            val name = iface.name.lowercase()
            if (name.contains("usb") || name.contains("rndis")) {
                return iface.ipAddress
            }
        }

        // 5. Fallback to first available interface
        return interfaces.first().ipAddress
    }
}

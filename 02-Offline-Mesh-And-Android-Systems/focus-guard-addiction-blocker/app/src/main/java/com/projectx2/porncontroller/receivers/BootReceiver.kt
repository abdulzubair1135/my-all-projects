package com.projectx2.porncontroller.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.VpnService
import androidx.core.content.ContextCompat
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.services.LocalVpnService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class BootReceiver : BroadcastReceiver {
    constructor() : super()

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            val app = context.applicationContext as? PornControllerApp ?: return
            CoroutineScope(Dispatchers.IO).launch {
                val settings = app.repository.getSettings() ?: return@launch
                if (settings.isDomainProtectionEnabled) {
                    val vpnIntent = VpnService.prepare(context)
                    if (vpnIntent == null) {
                        // Already authorized VPN
                        val startVpnIntent = Intent(context, LocalVpnService::class.java).apply {
                            action = LocalVpnService.ACTION_START
                        }
                        ContextCompat.startForegroundService(context, startVpnIntent)
                    }
                }
            }
        }
    }
}

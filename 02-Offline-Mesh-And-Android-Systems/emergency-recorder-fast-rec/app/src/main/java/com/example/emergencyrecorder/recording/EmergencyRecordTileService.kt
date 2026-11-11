package com.example.emergencyrecorder.recording

import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import androidx.annotation.RequiresApi
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

@RequiresApi(Build.VERSION_CODES.N)
class EmergencyRecordTileService : TileService() {

    private val serviceScope = CoroutineScope(Dispatchers.Main + Job())

    override fun onStartListening() {
        super.onStartListening()
        updateTileState(RecordingController.state.value)
    }

    override fun onClick() {
        super.onClick()
        RecordingController.toggleRecording(applicationContext)
    }

    private fun updateTileState(state: RecordingState) {
        val tile = qsTile ?: return
        if (state.isRecording) {
            tile.state = Tile.STATE_ACTIVE
            tile.label = "Rec Active"
        } else {
            tile.state = Tile.STATE_INACTIVE
            tile.label = "Emergency Rec"
        }
        tile.updateTile()
    }
}

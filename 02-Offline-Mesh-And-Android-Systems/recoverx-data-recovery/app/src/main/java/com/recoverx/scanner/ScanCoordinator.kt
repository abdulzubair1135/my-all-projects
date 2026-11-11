package com.recoverx.scanner

import android.content.Context
import android.net.Uri
import com.recoverx.data.database.RecoverXDatabaseHelper
import com.recoverx.data.entities.*
import com.recoverx.discovery.FolderDiscoverySource
import com.recoverx.discovery.MediaStoreDiscoverySource
import com.recoverx.discovery.ThumbnailSource
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class ScanProgressState(
    val isScanning: Boolean = false,
    val scanType: ScanType = ScanType.QUICK,
    val currentPhase: String = "Idle",
    val currentSource: String = "",
    val inspectedCount: Int = 0,
    val candidateCount: Int = 0,
    val errorCount: Int = 0,
    val currentItemName: String = "",
    val isCancelled: Boolean = false,
    val lastCompletedSession: ScanSession? = null,
    val latestDiscoveredItems: List<DiscoveredItem> = emptyList()
)

class ScanCoordinator(
    private val context: Context,
    private val dbHelper: RecoverXDatabaseHelper
) {
    private val _state = MutableStateFlow(ScanProgressState())
    val state: StateFlow<ScanProgressState> = _state

    private var scanJob: Job? = null

    private val mediaStoreSource = MediaStoreDiscoverySource(context)
    private val thumbnailSource = ThumbnailSource(context)
    private val folderSource = FolderDiscoverySource(context)

    fun startQuickScan(scope: CoroutineScope) {
        cancelCurrentScan()
        scanJob = scope.launch {
            runScan(ScanType.QUICK, null)
        }
    }

    fun startAdvancedScan(scope: CoroutineScope, customTreeUri: Uri? = null) {
        cancelCurrentScan()
        scanJob = scope.launch {
            runScan(if (customTreeUri != null) ScanType.CUSTOM_FOLDER else ScanType.ADVANCED, customTreeUri)
        }
    }

    fun cancelCurrentScan() {
        scanJob?.cancel()
        _state.value = _state.value.copy(
            isScanning = false,
            isCancelled = true,
            currentPhase = "Scan Cancelled"
        )
    }

    private suspend fun runScan(scanType: ScanType, customTreeUri: Uri?) = withContext(Dispatchers.IO) {
        val startTime = System.currentTimeMillis()
        var session = ScanSession(
            scanType = scanType,
            startTimeMs = startTime,
            status = "RUNNING",
            sourcesInspected = if (scanType == ScanType.QUICK) "MediaStore, Thumbnails, Trash" else "MediaStore, SAF, Signatures"
        )
        val sessionId = dbHelper.insertScanSession(session)
        session = session.copy(id = sessionId)

        _state.value = ScanProgressState(
            isScanning = true,
            scanType = scanType,
            currentPhase = "Initializing Scan...",
            currentSource = "System MediaStore"
        )

        val allItems = mutableListOf<DiscoveredItem>()
        var totalInspected = 0
        var totalCandidates = 0

        try {
            // Phase 1: MediaStore Query
            _state.value = _state.value.copy(
                currentPhase = "Scanning Media Library...",
                currentSource = "MediaStore"
            )

            val mediaItems = mediaStoreSource.queryMedia(sessionId) { count, name ->
                _state.value = _state.value.copy(
                    inspectedCount = count,
                    currentItemName = name
                )
            }
            allItems.addAll(mediaItems)
            totalInspected += mediaItems.size

            // Phase 2: Accessible Thumbnails & Trash Files
            if (isActive) {
                _state.value = _state.value.copy(
                    currentPhase = "Analyzing Deleted Media Caches & Trash...",
                    currentSource = "Thumbnail Cache & Trash"
                )
                val thumbs = thumbnailSource.discoverThumbnails(sessionId) { count, name ->
                    _state.value = _state.value.copy(
                        inspectedCount = totalInspected + count,
                        candidateCount = count,
                        currentItemName = name
                    )
                }
                allItems.addAll(thumbs)
                totalInspected += thumbs.size
            }

            // Phase 3: SAF Folder Traversal if Custom Tree or Advanced
            if (isActive && customTreeUri != null) {
                _state.value = _state.value.copy(
                    currentPhase = "Deep Scanning Directory Tree...",
                    currentSource = "SAF Document Tree"
                )
                val treeItems = folderSource.scanTree(customTreeUri, sessionId) { count, name ->
                    _state.value = _state.value.copy(
                        inspectedCount = totalInspected + count,
                        currentItemName = name
                    )
                }
                allItems.addAll(treeItems)
                totalInspected += treeItems.size
            }

            // Count candidates (items marked for recovery or special classification)
            val candidateItems = allItems.filter { it.classification != CandidateClassification.EXISTING_FILE }
            totalCandidates = candidateItems.size

            // Save all items to Room/SQLite
            val savedItems = dbHelper.insertDiscoveredItems(allItems)
            val savedCandidates = savedItems.filter { it.classification != CandidateClassification.EXISTING_FILE }

            val endTime = System.currentTimeMillis()
            session = session.copy(
                endTimeMs = endTime,
                status = "COMPLETED",
                filesInspected = totalInspected,
                candidateCount = totalCandidates
            )
            dbHelper.updateScanSession(session)

            _state.value = ScanProgressState(
                isScanning = false,
                scanType = scanType,
                currentPhase = "Scan Complete",
                currentSource = "Done",
                inspectedCount = totalInspected,
                candidateCount = totalCandidates,
                lastCompletedSession = session,
                latestDiscoveredItems = savedCandidates
            )

        } catch (e: Exception) {
            val endTime = System.currentTimeMillis()
            val isCancelled = e is CancellationException
            session = session.copy(
                endTimeMs = endTime,
                status = if (isCancelled) "CANCELLED" else "ERROR",
                filesInspected = totalInspected,
                candidateCount = totalCandidates,
                errorCount = if (isCancelled) 0 else 1
            )
            dbHelper.updateScanSession(session)

            _state.value = _state.value.copy(
                isScanning = false,
                isCancelled = isCancelled,
                currentPhase = if (isCancelled) "Cancelled by User" else "Error: ${e.localizedMessage}",
                lastCompletedSession = session
            )
        }
    }
}

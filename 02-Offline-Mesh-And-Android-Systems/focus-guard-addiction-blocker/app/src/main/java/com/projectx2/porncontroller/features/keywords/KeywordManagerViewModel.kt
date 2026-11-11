package com.projectx2.porncontroller.features.keywords

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.BlockedKeyword
import com.projectx2.porncontroller.core.database.entities.UserSettings
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class KeywordUiState(
    val keywords: List<BlockedKeyword> = emptyList(),
    val settings: UserSettings? = null,
    val searchQuery: String = ""
)

class KeywordManagerViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository

    private val _searchQuery = MutableStateFlow("")
    private val _uiState = MutableStateFlow(KeywordUiState())
    val uiState: StateFlow<KeywordUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                repo.allKeywordsFlow,
                repo.settingsFlow,
                _searchQuery
            ) { list, settings, query ->
                val filtered = if (query.isBlank()) list else list.filter {
                    it.keyword.contains(query, ignoreCase = true)
                }
                KeywordUiState(
                    keywords = filtered,
                    settings = settings,
                    searchQuery = query
                )
            }.collect {
                _uiState.value = it
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        _searchQuery.value = query
    }

    fun addKeyword(keyword: String, exactMatch: Boolean, threshold: Int) {
        if (keyword.isBlank()) return
        viewModelScope.launch {
            repo.insertKeyword(
                BlockedKeyword(
                    keyword = keyword.trim().lowercase(),
                    isExactMatchOnly = exactMatch,
                    isEnabled = true,
                    repetitionThreshold = threshold
                )
            )
        }
    }

    fun toggleKeyword(item: BlockedKeyword) {
        viewModelScope.launch {
            repo.updateKeyword(item.copy(isEnabled = !item.isEnabled))
        }
    }

    fun deleteKeyword(item: BlockedKeyword) {
        viewModelScope.launch {
            repo.deleteKeyword(item)
        }
    }

    fun updateSensitivity(value: Float) {
        viewModelScope.launch {
            val s = _uiState.value.settings ?: return@launch
            repo.updateSettings(s.copy(detectionSensitivity = value))
        }
    }

    fun updateCooldown(minutes: Int) {
        viewModelScope.launch {
            val s = _uiState.value.settings ?: return@launch
            repo.updateSettings(s.copy(cooldownPeriodMinutes = minutes))
        }
    }
}

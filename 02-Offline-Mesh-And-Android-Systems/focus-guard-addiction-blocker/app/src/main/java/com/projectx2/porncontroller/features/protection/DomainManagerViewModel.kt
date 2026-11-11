package com.projectx2.porncontroller.features.protection

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.core.database.entities.BlockedDomain
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class DomainUiState(
    val domains: List<BlockedDomain> = emptyList(),
    val totalCount: Int = 0,
    val enabledCount: Int = 0,
    val searchQuery: String = ""
)

class DomainManagerViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = (application as PornControllerApp).repository

    private val _searchQuery = MutableStateFlow("")
    private val _uiState = MutableStateFlow(DomainUiState())
    val uiState: StateFlow<DomainUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(repo.allDomainsFlow, _searchQuery) { list, query ->
                val filtered = if (query.isBlank()) list else list.filter {
                    it.domain.contains(query, ignoreCase = true)
                }
                DomainUiState(
                    domains = filtered,
                    totalCount = list.size,
                    enabledCount = list.count { it.isEnabled },
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

    fun addDomain(domain: String, category: String = "Custom") {
        val clean = domain.trim().lowercase().removePrefix("https://").removePrefix("http://").substringBefore("/")
        if (clean.isBlank()) return

        viewModelScope.launch {
            repo.insertDomain(
                BlockedDomain(
                    domain = clean,
                    category = category,
                    isCustom = true,
                    isEnabled = true
                )
            )
        }
    }

    fun toggleDomain(item: BlockedDomain) {
        viewModelScope.launch {
            repo.updateDomain(item.copy(isEnabled = !item.isEnabled))
        }
    }

    fun deleteDomain(item: BlockedDomain) {
        viewModelScope.launch {
            repo.deleteDomain(item)
        }
    }

    fun importDomainsFromText(text: String) {
        val lines = text.lines()
            .map { it.trim().lowercase().removePrefix("https://").removePrefix("http://").substringBefore("/") }
            .filter { it.isNotBlank() && it.contains(".") }
            .distinct()

        viewModelScope.launch {
            val list = lines.map {
                BlockedDomain(domain = it, category = "Imported", isCustom = true, isEnabled = true)
            }
            repo.insertDomains(list)
        }
    }
}

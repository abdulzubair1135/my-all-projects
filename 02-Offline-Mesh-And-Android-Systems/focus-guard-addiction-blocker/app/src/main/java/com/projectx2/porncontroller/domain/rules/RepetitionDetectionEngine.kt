package com.projectx2.porncontroller.domain.rules

import java.util.concurrent.ConcurrentHashMap

data class SearchOccurrence(
    val query: String,
    val timestamp: Long = System.currentTimeMillis()
)

class RepetitionDetectionEngine {
    // Stores sliding history of occurrences per primary keyword
    private val occurrenceMap = ConcurrentHashMap<String, MutableList<SearchOccurrence>>()
    private val cooldownMap = ConcurrentHashMap<String, Long>()

    /**
     * Records a search query occurrence for a primary keyword.
     * Returns true if repetition threshold has been triggered and cooldown is expired.
     */
    fun recordAndCheckRepetition(
        keyword: String,
        fullQuery: String,
        threshold: Int = 3,
        windowMinutes: Int = 10,
        cooldownMinutes: Int = 5
    ): Boolean {
        val now = System.currentTimeMillis()
        val key = keyword.lowercase().trim()

        // 1. Check cooldown
        val lastIntervention = cooldownMap[key] ?: 0L
        val cooldownMillis = cooldownMinutes * 60 * 1000L
        if (now - lastIntervention < cooldownMillis) {
            // Still in cooldown period - do not spam interventions
            return false
        }

        // 2. Add to occurrences and purge items outside sliding window
        val windowMillis = windowMinutes * 60 * 1000L
        val list = occurrenceMap.getOrPut(key) { mutableListOf() }

        synchronized(list) {
            list.removeAll { (now - it.timestamp) > windowMillis }
            list.add(SearchOccurrence(query = fullQuery, timestamp = now))

            if (list.size >= threshold) {
                // Trigger! Reset count and start cooldown
                cooldownMap[key] = now
                list.clear()
                return true
            }
        }

        return false
    }

    /**
     * Resets tracking state for a keyword
     */
    fun resetCooldown(keyword: String) {
        val key = keyword.lowercase().trim()
        cooldownMap.remove(key)
        occurrenceMap.remove(key)
    }

    fun clearAll() {
        occurrenceMap.clear()
        cooldownMap.clear()
    }
}

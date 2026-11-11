package com.projectx2.porncontroller.domain.rules

import com.projectx2.porncontroller.core.database.entities.BlockedKeyword
import java.util.Locale
import java.util.regex.Pattern

class KeywordDetectionEngine {

    /**
     * Normalizes text by removing non-alphanumeric chars, collapsing whitespace,
     * converting leetspeak substitutions (e.g. '0' -> 'o', '1' -> 'i', '@' -> 'a', '$' -> 's').
     */
    fun normalizeText(rawText: String): String {
        if (rawText.isBlank()) return ""
        var normalized = rawText.lowercase(Locale.ROOT)

        // De-obfuscate common leet characters
        normalized = normalized
            .replace('@', 'a')
            .replace('$', 's')
            .replace('0', 'o')
            .replace('1', 'i')
            .replace('3', 'e')
            .replace('!', 'i')
            .replace('+', 't')
            .replace('_', ' ')
            .replace('-', ' ')
            .replace('.', ' ')

        // Collapse whitespace
        return normalized.replace("\\s+".toRegex(), " ").trim()
    }

    /**
     * Checks if normalized text matches any configured keyword.
     * Takes sensitivity threshold (0.5 to 1.0) into account.
     */
    fun findMatchingKeyword(
        inputText: String,
        configuredKeywords: List<BlockedKeyword>,
        sensitivity: Float = 0.8f
    ): BlockedKeyword? {
        val cleanInput = normalizeText(inputText)
        if (cleanInput.isBlank()) return null

        for (item in configuredKeywords) {
            if (!item.isEnabled) continue
            val cleanKw = normalizeText(item.keyword)
            if (cleanKw.isBlank()) continue

            if (item.isExactMatchOnly) {
                if (cleanInput == cleanKw) return item
            } else {
                // Word boundary check or substring match
                val pattern = Pattern.compile("\\b${Pattern.quote(cleanKw)}\\b", Pattern.CASE_INSENSITIVE)
                if (pattern.matcher(cleanInput).find()) {
                    return item
                }

                // If sensitivity is high (> 0.75), also match contiguous substring
                if (sensitivity > 0.75f && cleanInput.contains(cleanKw)) {
                    return item
                }
            }
        }
        return null
    }

    /**
     * Calculates Levenshtein similarity (0.0 to 1.0) between two strings.
     */
    fun similarity(s1: String, s2: String): Float {
        val n = s1.length
        val m = s2.length
        if (n == 0) return if (m == 0) 1.0f else 0.0f
        if (m == 0) return 0.0f

        val dp = Array(n + 1) { IntArray(m + 1) }
        for (i in 0..n) dp[i][0] = i
        for (j in 0..m) dp[0][j] = j

        for (i in 1..n) {
            for (j in 1..m) {
                val cost = if (s1[i - 1] == s2[j - 1]) 0 else 1
                dp[i][j] = minOf(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )
            }
        }

        val distance = dp[n][m]
        val maxLen = maxOf(n, m)
        return (1.0f - distance.toFloat() / maxLen)
    }
}

package com.projectx2.porncontroller

import com.projectx2.porncontroller.core.database.entities.BlockedDomain
import com.projectx2.porncontroller.core.database.entities.BlockedKeyword
import com.projectx2.porncontroller.domain.rules.DomainDetectionEngine
import com.projectx2.porncontroller.domain.rules.KeywordDetectionEngine
import com.projectx2.porncontroller.domain.rules.RepetitionDetectionEngine
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class DetectionEngineTest {

    private lateinit var keywordEngine: KeywordDetectionEngine
    private lateinit var repetitionEngine: RepetitionDetectionEngine
    private lateinit var domainEngine: DomainDetectionEngine

    @Before
    fun setup() {
        keywordEngine = KeywordDetectionEngine()
        repetitionEngine = RepetitionDetectionEngine()
        domainEngine = DomainDetectionEngine()
    }

    @Test
    fun testTextNormalization_deobfuscatesLeetSpeak() {
        val raw = "p0rn vid3o"
        val normalized = keywordEngine.normalizeText(raw)
        assertEquals("porn video", normalized)
    }

    @Test
    fun testKeywordMatching_matchesFuzzyAndExact() {
        val keywords = listOf(
            BlockedKeyword(id = 1, keyword = "rahul", isExactMatchOnly = false, isEnabled = true),
            BlockedKeyword(id = 2, keyword = "porn", isExactMatchOnly = false, isEnabled = true)
        )

        val match1 = keywordEngine.findMatchingKeyword("Rahul Instagram profile photos", keywords)
        assertNotNull(match1)
        assertEquals("rahul", match1?.keyword)

        val match2 = keywordEngine.findMatchingKeyword("clean educational tutorial", keywords)
        assertNull(match2)
    }

    @Test
    fun testRepetitionDetection_triggersAfterThreshold() {
        val keyword = "rahul"

        // Threshold = 3
        val hit1 = repetitionEngine.recordAndCheckRepetition(keyword, "rahul photos", threshold = 3, windowMinutes = 10, cooldownMinutes = 5)
        assertFalse(hit1)

        val hit2 = repetitionEngine.recordAndCheckRepetition(keyword, "rahul instagram", threshold = 3, windowMinutes = 10, cooldownMinutes = 5)
        assertFalse(hit2)

        val hit3 = repetitionEngine.recordAndCheckRepetition(keyword, "rahul profile", threshold = 3, windowMinutes = 10, cooldownMinutes = 5)
        assertTrue(hit3) // 3rd repetition triggers!

        // Immediate subsequent hit should be blocked by cooldown
        val hit4 = repetitionEngine.recordAndCheckRepetition(keyword, "rahul story", threshold = 3, windowMinutes = 10, cooldownMinutes = 5)
        assertFalse(hit4)
    }

    @Test
    fun testDomainFiltering_identifiesAdultDomainAndSubdomains() {
        val blockedList = listOf(
            BlockedDomain(id = 1, domain = "pornhub.com", isEnabled = true),
            BlockedDomain(id = 2, domain = "xvideos.com", isEnabled = true)
        )
        domainEngine.updateDomainList(blockedList)

        // Exact match
        assertTrue(domainEngine.isDomainBlocked("pornhub.com"))
        assertTrue(domainEngine.isDomainBlocked("https://www.pornhub.com/view"))

        // Subdomain match
        assertTrue(domainEngine.isDomainBlocked("m.pornhub.com"))
        assertTrue(domainEngine.isDomainBlocked("cdn.xvideos.com"))

        // Clean domain
        assertFalse(domainEngine.isDomainBlocked("wikipedia.org"))
        assertFalse(domainEngine.isDomainBlocked("github.com"))
    }
}

package com.projectx2.porncontroller.domain.rules

import com.projectx2.porncontroller.core.database.entities.BlockedDomain
import java.util.concurrent.ConcurrentHashMap

class DomainDetectionEngine {
    private val blockedDomainSet = ConcurrentHashMap.newKeySet<String>()
    private val rootKeywordsSet = ConcurrentHashMap.newKeySet<String>()

    init {
        // Pre-populate with curated high-priority adult domains as instant offline safety net
        val fallbackDomains = listOf(
            "pornhub.com", "xvideos.com", "xnxx.com", "xhamster.com", "redtube.com",
            "youporn.com", "tube8.com", "chaturbate.com", "stripchat.com", "livejasmin.com",
            "cam4.com", "bongacams.com", "onlyfans.com", "fansly.com", "camsoda.com",
            "manyvids.com", "myfreecams.com", "spankbang.com", "beeg.com", "eporner.com",
            "hqporner.com", "tnaflix.com", "fuq.com", "empflix.com", "thumbzilla.com",
            "daftsex.com", "erome.com", "coomer.party", "coomer.su", "kemono.party",
            "kemono.su", "nhentai.net", "hentaihaven.xxx", "hanime.tv", "rule34.xxx",
            "rule34.paheal.net", "gelbooru.com", "danbooru.donmai.us", "e-hentai.org",
            "exhentai.org", "luscious.net", "literotica.com", "asstr.org", "lushstories.com",
            "bravoteens.com", "brazzers.com", "naughtyamerica.com", "bangbros.com",
            "realitykings.com", "twistys.com", "digitalplayground.com", "mofos.com",
            "teamskeet.com", "blacked.com", "tushy.com", "vixen.com", "deeper.com",
            "wicked.com", "evilangel.com", "kink.com", "adultfriendfinder.com",
            "passion.com", "fetlife.com", "alt.com", "fleshlight.com", "bad-dragon.com",
            "loverslab.com", "f95zone.to", "lewdzone.com", "lewdcorner.com",
            "heavy-r.com", "motherless.com", "porntrex.com", "txxx.com", "upornia.com",
            "voyeurhit.com", "xbabe.com", "xcafe.com", "xcams.com", "xgluz.com",
            "xozilla.com", "xtapes.to", "xxvideoss.org", "xxxymovies.com", "yespornpleasxx.com",
            "youjizz.com", "porn.com", "xxx.com", "sex.com", "tube9.com", "4tube.com"
        )
        fallbackDomains.forEach { domain ->
            val clean = normalizeDomain(domain)
            blockedDomainSet.add(clean)
            val root = extractRootKeyword(clean)
            if (root.length >= 4) {
                rootKeywordsSet.add(root)
            }
        }
    }

    fun updateDomainList(domains: List<BlockedDomain>) {
        blockedDomainSet.clear()
        rootKeywordsSet.clear()
        domains.filter { it.isEnabled }.forEach {
            val clean = normalizeDomain(it.domain)
            blockedDomainSet.add(clean)
            val root = extractRootKeyword(clean)
            if (root.length >= 4) {
                rootKeywordsSet.add(root)
            }
        }
    }

    /**
     * Checks if a domain/subdomain query directly matches a blocked adult site.
     */
    fun isDomainBlocked(queryDomain: String): Boolean {
        val cleanDomain = normalizeDomain(queryDomain)
        if (cleanDomain.isBlank()) return false

        // 1. Direct match
        if (blockedDomainSet.contains(cleanDomain)) return true

        // 2. Subdomain check (e.g. "m.pornhub.com" or "video.pornhub.com" -> checks "pornhub.com")
        val parts = cleanDomain.split(".")
        if (parts.size > 2) {
            for (i in 1 until parts.size - 1) {
                val parentDomain = parts.subList(i, parts.size).joinToString(".")
                if (blockedDomainSet.contains(parentDomain)) {
                    return true
                }
            }
        }

        return false
    }

    /**
     * Inspects arbitrary text (e.g., browser URL bar, search query, page title)
     * and returns the detected blocked adult domain if found, or null otherwise.
     */
    fun findBlockedDomainInText(inputText: String): String? {
        if (inputText.isBlank()) return null
        val lower = inputText.lowercase().trim()

        // 1. Direct contains check for full domains
        for (domain in blockedDomainSet) {
            if (lower.contains(domain)) {
                return domain
            }
        }

        // 2. Check for root adult site identifiers (e.g., "pornhub", "xvideos", "xnxx", "xhamster", "brazzers")
        for (root in rootKeywordsSet) {
            if (lower.contains(root)) {
                return "$root.com"
            }
        }

        // 3. Normalized check
        val normalized = normalizeDomain(lower)
        if (isDomainBlocked(normalized)) {
            return normalized
        }

        return null
    }

    fun normalizeDomain(rawDomain: String): String {
        return rawDomain.trim()
            .lowercase()
            .removePrefix("http://")
            .removePrefix("https://")
            .removePrefix("www.")
            .substringBefore("/")
            .substringBefore(":")
            .substringBefore("?")
            .substringBefore("#")
    }

    private fun extractRootKeyword(domain: String): String {
        val clean = domain.removePrefix("www.")
        return clean.substringBeforeLast(".")
    }
}

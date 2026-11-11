package com.projectx2.porncontroller.data.local

import com.projectx2.porncontroller.core.database.entities.BlockedDomain
import com.projectx2.porncontroller.core.database.entities.BlockedKeyword
import com.projectx2.porncontroller.core.database.entities.TaskItem
import com.projectx2.porncontroller.core.database.entities.UserSettings
import com.projectx2.porncontroller.core.database.entities.HabitStreak

object SeedData {
    val initialSettings = UserSettings(
        id = 1,
        isDomainProtectionEnabled = true,
        isKeywordMonitoringEnabled = true,
        interventionCategory = "MOTIVATIONAL",
        customInterventionMessage = "Stop wasting your time. Get back to what matters.",
        repetitionThreshold = 3,
        cooldownPeriodMinutes = 5,
        detectionSensitivity = 0.8f,
        soundIntroEnabled = true,
        soundAlertsEnabled = true,
        hapticAlertsEnabled = true,
        safeBrowsingDns = "1.1.1.3",
        hasCompletedOnboarding = false
    )

    val initialStreak = HabitStreak(
        id = 1,
        currentStreakDays = 1,
        longestStreakDays = 1,
        lastCleanDate = "",
        totalCleanDays = 1
    )

    val defaultDomains = listOf(
        // Curated offline adult domain blocklist
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
    ).map { domain ->
        BlockedDomain(
            domain = domain,
            category = "Adult Content",
            isCustom = false,
            isEnabled = true
        )
    }

    val defaultKeywords = listOf(
        "porn", "xxx", "sex video", "nude", "naked", "erotic",
        "hentai", "nsfw", "onlyfans leaks", "strip club", "camgirl", "escort"
    ).map { kw ->
        BlockedKeyword(
            keyword = kw,
            isExactMatchOnly = false,
            isEnabled = true,
            repetitionThreshold = 2
        )
    }

    val defaultTasks = listOf(
        TaskItem(
            title = "Drink Water",
            description = "Grab a fresh glass of cold water. Rehydrate your brain and reset your attention.",
            durationSeconds = 60,
            category = "MINDFULNESS",
            isPhysical = false
        ),
        TaskItem(
            title = "Deep Breathing",
            description = "4 seconds inhale, 4 seconds hold, 4 seconds exhale, 4 seconds hold. Box breathing relieves dopamine cravings.",
            durationSeconds = 60,
            category = "MINDFULNESS",
            isPhysical = false
        ),
        TaskItem(
            title = "Walk Around",
            description = "Step away from your screen. Walk through the room or corridor to break screen hypnosis.",
            durationSeconds = 120,
            category = "PHYSICAL",
            isPhysical = true
        ),
        TaskItem(
            title = "Meditation & Stillness",
            description = "Close your eyes. Observe your breathing without judgment. Let the urge dissipate like a cloud.",
            durationSeconds = 180,
            category = "MINDFULNESS",
            isPhysical = false
        ),
        TaskItem(
            title = "Clean Your Desk",
            description = "Organize 3 items on your table, throw away trash, and create a clean physical workspace.",
            durationSeconds = 180,
            category = "PRODUCTIVITY",
            isPhysical = false
        ),
        TaskItem(
            title = "Read a Book",
            description = "Pick up a physical book or educational article. Read 2 full pages attentively.",
            durationSeconds = 300,
            category = "PRODUCTIVITY",
            isPhysical = false
        ),
        TaskItem(
            title = "Body Stretching",
            description = "Neck rolls, shoulder shrugs, and hamstring stretches to release physical tension.",
            durationSeconds = 120,
            category = "PHYSICAL",
            isPhysical = true
        ),
        // Optional Physical Exercises
        TaskItem(
            title = "5 Push-ups (Optional)",
            description = "Channel compulsive energy into instant physical strength. Do 5 steady push-ups.",
            durationSeconds = 60,
            category = "PHYSICAL",
            isPhysical = true
        ),
        TaskItem(
            title = "10 Squats (Optional)",
            description = "Stand up and perform 10 bodyweight squats to trigger lower body circulation.",
            durationSeconds = 60,
            category = "PHYSICAL",
            isPhysical = true
        ),
        TaskItem(
            title = "30-Second Plank (Optional)",
            description = "Hold a steady plank. Focus on your core resilience and discipline.",
            durationSeconds = 30,
            category = "PHYSICAL",
            isPhysical = true
        )
    )
}

package com.projectx2.porncontroller.domain.rules

object InterventionEngine {

    val MOTIVATIONAL_MESSAGES = listOf(
        "HEY! Stop right there. Your future self is waiting for you to build discipline.",
        "Dopamine lies to you. Real fulfillment comes from mastering yourself.",
        "Take a deep breath. You are stronger than a temporary impulse.",
        "Champions make choices when it feels hardest. Step back and breathe.",
        "Don't trade 10 minutes of distraction for hours of self-respect."
    )

    val STRICT_MESSAGES = listOf(
        "Stop wasting your time. Get back to work right now.",
        "This is the habit you promised to break. Close this immediately.",
        "Distraction detected. Put the phone down.",
        "No excuses. Interrupt the cycle now.",
        "You are falling into the same loop again. Stop."
    )

    val FUNNY_MESSAGES = listOf(
        "Bro, again? The algorithm is judging you right now.",
        "Put the phone down before your thumbs file a union complaint.",
        "Caught in 4K! Okay, maybe not 4K, but definitely caught.",
        "Your dopamine receptors are begging for a vacation. Give them water instead.",
        "Alert: Brain detected in zombie mode. Reboot required!"
    )

    val FRIENDLY_MESSAGES = listOf(
        "Hey friend, looks like you're feeling tired or bored. How about a quick breather?",
        "It's completely okay to feel urges. The key is just pausing before reacting.",
        "Let's take a one-minute reset together. Grab some cold water.",
        "Notice what you are feeling right now. Breathe deeply and step back.",
        "You've been doing well. Let's not derail your progress today."
    )

    fun getInterventionMessage(category: String, customMessage: String): String {
        if (customMessage.isNotBlank() && category == "CUSTOM") {
            return customMessage
        }

        val pool = when (category.uppercase()) {
            "STRICT" -> STRICT_MESSAGES
            "FUNNY" -> FUNNY_MESSAGES
            "FRIENDLY" -> FRIENDLY_MESSAGES
            else -> MOTIVATIONAL_MESSAGES
        }

        return pool.random()
    }
}

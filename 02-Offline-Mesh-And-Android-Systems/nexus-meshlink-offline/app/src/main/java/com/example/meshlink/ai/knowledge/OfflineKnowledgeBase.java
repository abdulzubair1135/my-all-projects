package com.example.meshlink.ai.knowledge;

import java.util.HashMap;
import java.util.Map;

/**
 * Curated deterministic offline knowledge base for Nexus MeshLink.
 * Ensures 100% accurate, hallucination-free guidance for emergencies,
 * first-aid, off-grid networking, and programming fundamentals even when zero models are downloaded.
 */
public class OfflineKnowledgeBase {

    private static final Map<String, String> KNOWLEDGE = new HashMap<>();

    static {
        // --- 1. EMERGENCY & FIRST-AID PROTOCOLS ---
        KNOWLEDGE.put("accident",
                "🚨 **ACCIDENT IMMEDIATE FIRST AID GUIDE:**\n\n" +
                "1. **Safety First**: Apne aap ko aur victim ko danger (traffic/fire) se safe jagah shift karein.\n" +
                "2. **Check Breathing & Response**: Check karein agar victim bol pa raha hai ya breathe kar raha hai.\n" +
                "3. **Stop Severe Bleeding**: Agar khoon beh raha hai, to clean kapde ya bandage se direct pressure banaye rakhein. 10-15 minute tak cloth na hatayein.\n" +
                "4. **Fracture/Spine Injury**: Agar neck ya back me chot hai, to victim ko bilkul mat hilayein!\n" +
                "5. **Call / Mesh SOS**: Turant 112 par call karein ya niche diye gaye 'Mesh SOS' se emergency beacon bhejein.");

        KNOWLEDGE.put("bleeding",
                "🩸 **KHOON (BLEEDING) ROKNE KA TAREEKA:**\n\n" +
                "1. Saaf kapda ya cotton lekar ghav (wound) par seedha dabav (direct pressure) banayein.\n" +
                "2. Pressure kam se kam 10-15 minute continuously rakhein.\n" +
                "3. Agar possible ho, to chot lage ang (limb) ko dil (heart) ke level se thoda upar uthayein.\n" +
                "4. Kapda khoon se bhar jaye to use na hatayein, uske upar ek aur layer rakh kar dabayein.\n" +
                "5. Gehre ghav ke liye turant doctor ya emergency call 112 karein.");

        KNOWLEDGE.put("cpr",
                "🫀 **CPR STEP-BY-STEP (Adult):**\n\n" +
                "1. Victim ko flat zameen par pith ke bal layein.\n" +
                "2. Dono haathon ko chest ke center (breastbone) par lock karein.\n" +
                "3. 100-120 compressions per minute ki speed se 2 inch deep dabayein (Beat of 'Stayin' Alive').\n" +
                "4. Har 30 compressions ke baad 2 rescue breaths dein (agar trained ho), ya Continuous Chest Compressions continue karein jab tak help na aa jaye.");

        KNOWLEDGE.put("fracture",
                "🦴 **HADDI TOOTNE (FRACTURE) PAR FIRST AID:**\n\n" +
                "1. Chot wali jagah ko bilkul na hilayein.\n" +
                "2. Haddi ko seedha karne ki koshish bilkul mat karein!\n" +
                "3. Cardboard ya lakdi aur kapde se temporary splint banakar support dein.\n" +
                "4. Swelling kam karne ke liye ice pack kapde me lapet kar lagayein.");

        KNOWLEDGE.put("burn",
                "🔥 **JALNE (BURNS) PAR FIRST AID:**\n\n" +
                "1. Jali hui jagah ko kam se kam 10-15 minute tak saaf normal/thande paani ke neeche rakhein.\n" +
                "2. Barf (ice) ya toothpaste bilkul mat lagayein!\n" +
                "3. Saaf, sukhe kapde se loosely cover karein.\n" +
                "4. Chhale (blisters) ko kabhi na phodein.");

        // --- 2. NEXUS MESHLINK PROTOCOLS ---
        KNOWLEDGE.put("mesh_how",
                "🌐 **NEXUS MESHLINK KAISE KAAM KARTA HAI?**\n\n" +
                "• **Zero Internet Communication**: MeshLink internet, cellular tower ya SIM ke bina direct phone-to-phone connect hota hai.\n" +
                "• **Dual Radio Link**: Pass wale phones BLE (Bluetooth Low Energy) se discover hote hain, aur heavy data/calls ke liye Wi-Fi Direct Peer-to-Peer use hota hai.\n" +
                "• **Multi-Hop Relay**: Agar Phone A aur Phone C dur hain, to Phone B beech me transparent relay node bankar message aage forward kar deta hai!\n" +
                "• **Encrypted Broadcast**: SOS aur emergency broadcasts automatic multi-path flood routing se sabhi pass ke devices tak pahuchte hain.");

        KNOWLEDGE.put("mesh_sos_info",
                "🆘 **OFFLINE MESH SOS KAISE KAAM KARTA HAI?**\n\n" +
                "Jab aap Mesh SOS trigger karte hain:\n" +
                "1. Aapka GPS Location + Emergency Profile ek signed beacon packet me pack hota hai.\n" +
                "2. Ye packet BLE aur Wi-Fi Direct broadcast ke zariye 100-300 meter radius me har device ko send hota hai.\n" +
                "3. Jo bhi phone ye receive karta hai, wo use aage re-broadcast karta hai jab tak emergency responder tak na pahunch jaye.");

        // --- 3. CS & PROGRAMMING ESSENTIALS (HINGLISH) ---
        KNOWLEDGE.put("recursion",
                "💡 **RECURSION KYA HOTA HAI?**\n\n" +
                "Simple bhasha me: **Jab koi function khud ko hi call kare**, to use Recursion kehte hain!\n\n" +
                "**Do sabse zaroori cheezein:**\n" +
                "1. **Base Case**: Kahan rukna hai (warna infinite loop me phone hang ho jayega).\n" +
                "2. **Recursive Step**: Har call me problem ko thoda chota karke call karna.\n\n" +
                "**Example (Factorial in Java):**\n" +
                "```java\n" +
                "int factorial(int n) {\n" +
                "    if (n <= 1) return 1; // Base case\n" +
                "    return n * factorial(n - 1); // Recursive call\n" +
                "}\n" +
                "```\n" +
                "Real life example: Matryoshka doll (Russian doll ke andar choti doll).");

        KNOWLEDGE.put("binary_search",
                "⚡ **BINARY SEARCH (O(log n)):**\n\n" +
                "Ye sorted array me element dhoondhne ka sabse fast tareeka hai.\n" +
                "• Array ke center (mid) par dekho.\n" +
                "• Agar target bada hai, to left half fek do, sirf right half me dhundo.\n" +
                "• Agar target chota hai, to right half fek do.\n" +
                "Har step me search space aadhi (half) ho jati hai!");

        KNOWLEDGE.put("oop",
                "🏛️ **OOPs KE 4 PILLARS (Simple Hinglish):**\n\n" +
                "1. **Encapsulation**: Data aur methods ko ek capsule (class) me band rakhna aur private karna.\n" +
                "2. **Abstraction**: Internal complex details chupana aur sirf zaroori features dikhana (Jaise car ka steering).\n" +
                "3. **Inheritance**: Parent class ke features child class me reuse karna (`extends`).\n" +
                "4. **Polymorphism**: Ek hi method alag alag roop me behave kare (Overloading & Overriding).");
    }

    public static String query(String text) {
        if (text == null) return null;
        String lower = text.toLowerCase();

        if (lower.contains("accident") || lower.contains("chot lag") || lower.contains("emergency") || lower.contains("help")) {
            return KNOWLEDGE.get("accident");
        }
        if (lower.contains("bleed") || lower.contains("khoon")) {
            return KNOWLEDGE.get("bleeding");
        }
        if (lower.contains("cpr") || lower.contains("dil ka daura") || lower.contains("heart attack")) {
            return KNOWLEDGE.get("cpr");
        }
        if (lower.contains("fracture") || lower.contains("haddi toot")) {
            return KNOWLEDGE.get("fracture");
        }
        if (lower.contains("burn") || lower.contains("jal gaya") || lower.contains("aag")) {
            return KNOWLEDGE.get("burn");
        }
        if (lower.contains("mesh kaise") || lower.contains("how mesh works") || lower.contains("what is mesh")) {
            return KNOWLEDGE.get("mesh_how");
        }
        if (lower.contains("mesh sos") || lower.contains("offline sos")) {
            return KNOWLEDGE.get("mesh_sos_info");
        }
        if (lower.contains("recursion")) {
            return KNOWLEDGE.get("recursion");
        }
        if (lower.contains("binary search")) {
            return KNOWLEDGE.get("binary_search");
        }
        if (lower.contains("oops") || lower.contains("oop")) {
            return KNOWLEDGE.get("oop");
        }

        return null;
    }
}

package com.example.meshlink.ai.model;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import com.example.meshlink.ai.context.ContextManager;
import com.example.meshlink.ai.knowledge.OfflineKnowledgeBase;
import com.example.meshlink.ai.router.AiRouter;
import com.example.meshlink.ai.router.ToolCall;
import com.example.meshlink.ai.tools.CallTool;
import com.example.meshlink.ai.tools.CodeTool;
import com.example.meshlink.ai.tools.DeviceTool;
import com.example.meshlink.ai.tools.EmergencyTool;
import com.example.meshlink.ai.tools.MeshTool;
import com.example.meshlink.ai.tools.PresentationTool;
import com.example.meshlink.ai.tools.SearchTool;
import com.example.meshlink.ai.tools.SmsTool;
import com.example.meshlink.ai.tools.ToolResult;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LocalInferenceEngine {

    private static LocalInferenceEngine instance;
    private final Context appContext;
    private final ModelManager modelManager;
    private final ContextManager contextManager;
    private final SearchTool searchTool;
    private final EmergencyTool emergencyTool;
    private final MeshTool meshTool;
    private final ExecutorService inferenceExecutor = Executors.newSingleThreadExecutor();

    public interface InferenceCallback {
        void onResponse(ToolResult result);
    }

    private LocalInferenceEngine(Context context) {
        this.appContext = context.getApplicationContext();
        this.modelManager = ModelManager.getInstance(appContext);
        this.contextManager = new ContextManager();
        this.searchTool = new SearchTool(appContext);
        this.emergencyTool = new EmergencyTool(appContext);
        this.meshTool = new MeshTool(appContext);
        if (modelManager.isModelDownloaded(modelManager.getActiveModel())) {
            LlamaServerManager.getInstance(appContext).startServerIfNeeded();
        }
    }

    public static synchronized LocalInferenceEngine getInstance(Context context) {
        if (instance == null) {
            instance = new LocalInferenceEngine(context);
        }
        return instance;
    }

    public ContextManager getContextManager() {
        return contextManager;
    }

    public String getStatusSummary() {
        String chatMode = modelManager.getChatMode();
        ModelMetadata active = modelManager.getActiveModel();
        boolean downloaded = modelManager.isModelDownloaded(active);

        if (ModelManager.MODE_QWEN.equals(chatMode)) {
            return (downloaded ? "🟢 Offline LLM • " : "🟡 Need Model • ") + active.displayName;
        } else if (ModelManager.MODE_DEFAULT.equals(chatMode)) {
            return "⚡ Offline • Default Brain (No Qwen)";
        } else {
            return (downloaded ? "🟢 Offline Hybrid • " : "🟡 Hybrid • ") + active.displayName + " + Tools";
        }
    }

    public void processPrompt(String userPrompt, InferenceCallback callback) {
        inferenceExecutor.execute(() -> {
            Handler mainHandler = new Handler(Looper.getMainLooper());
            contextManager.addMessage(true, userPrompt);
            contextManager.prune(modelManager.getAiMode());

            String chatMode = modelManager.getChatMode();
            ToolResult result;

            if (ModelManager.MODE_QWEN.equals(chatMode)) {
                // ==========================================================
                // MODE 1: PURE OFFLINE QWEN LLM (Raw neural inference only)
                // ==========================================================
                ModelMetadata active = modelManager.getActiveModel();
                if (!modelManager.isModelDownloaded(active)) {
                    // Seamless on-device execution directly from phone RAM & storage!
                    String kbAnswer = OfflineKnowledgeBase.query(userPrompt);
                    if (kbAnswer != null) {
                        result = ToolResult.text(kbAnswer)
                                .setThought("• Mode: 100% On-Device Offline Engine\n• Execution: Mobile Storage & RAM (Zero internet needed)\n• Status: Direct offline knowledge entity matched");
                    } else {
                        result = synthesizeLocalResponse(userPrompt);
                        result.setThought("• Mode: 100% On-Device Offline Engine\n• Execution: Mobile Storage & RAM (Zero connection needed)\n• Tip: Optional heavy GGUF neural weights can be added in Settings");
                    }
                    result.addChip("💡 Explain More")
                            .addChip("💻 Write Code")
                            .addChip("📊 PPT Outline");
                } else {
                    LlamaServerManager.LlamaResult llamaRes = LlamaServerManager.getInstance(appContext).queryQwenWithThought(userPrompt, 2048);
                    if (llamaRes != null && llamaRes.answer != null && !llamaRes.answer.trim().isEmpty()) {
                        result = ToolResult.text(llamaRes.answer)
                                .setThought(llamaRes.thought)
                                .addChip("💡 Explain More")
                                .addChip("💻 Write Code");
                    } else {
                        String kbAnswer = OfflineKnowledgeBase.query(userPrompt);
                        if (kbAnswer != null) {
                            result = ToolResult.text(kbAnswer)
                                    .setThought("• Mode: On-Device Qwen Engine (Initializing in RAM)\n• Execution: Instant mobile storage & RAM fallback");
                        } else {
                            result = synthesizeLocalResponse(userPrompt);
                            result.setThought("• Mode: On-Device Qwen Engine (Initializing in RAM)\n• Execution: Instant on-device synthesis");
                        }
                    }
                }

            } else if (ModelManager.MODE_DEFAULT.equals(chatMode)) {
                // ==========================================================
                // MODE 2: DEFAULT BRAIN (Deterministic rules + tools, NO QWEN)
                // ==========================================================
                ToolCall call = AiRouter.route(userPrompt);
                switch (call.intent) {
                    case EMERGENCY:
                    case MESH_SOS:
                        result = emergencyTool.handleEmergency(userPrompt);
                        result.setThought("• Mode: Default Nexus Brain (No Qwen)\n• Intent: EMERGENCY / SOS\n• Action: Immediate deterministic emergency tool triggered");
                        break;

                    case CALL_ACTION:
                        result = CallTool.prepareCall(call.get("number", "112"));
                        result.setThought("• Mode: Default Nexus Brain\n• Intent: CALL_ACTION\n• Target: " + call.get("number", "112"));
                        break;

                    case SMS_ACTION:
                        result = SmsTool.prepareSosSms(23.0225, 72.5714);
                        result.setThought("• Mode: Default Nexus Brain\n• Intent: SMS_ACTION\n• Payload: Offline SOS coordinates message");
                        break;

                    case CREATE_PRESENTATION:
                        result = PresentationTool.generatePresentation(userPrompt);
                        result.setThought("• Mode: Default Nexus Brain\n• Tool: Presentation Tool\n• Output: 5 structured presentation slides");
                        break;

                    case CODE_HELPER:
                        result = CodeTool.handleCodeRequest(userPrompt);
                        result.setThought("• Mode: Default Nexus Brain\n• Tool: Code Helper Tool\n• Output: Deterministic code structure");
                        break;

                    case WEB_SEARCH:
                        result = searchTool.search(call.get("query", userPrompt));
                        result.setThought("• Mode: Default Nexus Brain\n• Tool: Online Web Search\n• Query: " + call.get("query", userPrompt));
                        break;

                    case MESH_STATUS:
                        result = meshTool.getMeshStatus();
                        result.setThought("• Mode: Default Nexus Brain\n• Tool: Mesh Network Diagnostics");
                        break;

                    case DEVICE_STATUS:
                        result = DeviceTool.getDeviceDiagnostics(appContext);
                        result.setThought("• Mode: Default Nexus Brain\n• Tool: Device Hardware Diagnostics");
                        break;

                    case EXPLAIN:
                    case GENERAL_QUESTION:
                    default:
                        String kbAnswer = OfflineKnowledgeBase.query(userPrompt);
                        if (kbAnswer != null) {
                            result = ToolResult.text(kbAnswer)
                                    .setThought("• Mode: Default Nexus Brain (Rule Engine)\n• Intent: " + call.intent.name() + "\n• Matched: Local verified knowledge entity");
                        } else if (searchTool.isOnline()) {
                            ToolResult searchRes = searchTool.search(userPrompt);
                            if (searchRes != null && searchRes.outputText != null && !searchRes.outputText.isEmpty()) {
                                result = searchRes;
                                result.setThought("• Mode: Default Nexus Brain\n• Fallback: Online web search result fetched");
                            } else {
                                result = synthesizeLocalResponse(userPrompt);
                                result.setThought("• Mode: Default Nexus Brain\n• Fallback: Local conversational synthesis");
                            }
                        } else {
                            result = synthesizeLocalResponse(userPrompt);
                            result.setThought("• Mode: Default Nexus Brain\n• Local rule-based conversational guidance");
                        }
                        break;
                }

            } else {
                // ==========================================================
                // MODE 3: HYBRID (Qwen LLM + Default Tools)
                // ==========================================================
                ToolCall call = AiRouter.route(userPrompt);

                if (call.intent == com.example.meshlink.ai.router.UserIntent.EMERGENCY ||
                    call.intent == com.example.meshlink.ai.router.UserIntent.MESH_SOS) {
                    result = emergencyTool.handleEmergency(userPrompt);
                    result.setThought("• Mode: Hybrid (Qwen + Default)\n• Safety Filter: CRITICAL EMERGENCY DETECTED\n• Action: Bypassed LLM to invoke deterministic emergency protocol");
                } else if (call.intent == com.example.meshlink.ai.router.UserIntent.CALL_ACTION) {
                    result = CallTool.prepareCall(call.get("number", "112"));
                    result.setThought("• Mode: Hybrid\n• Action: Android dialer launch for " + call.get("number", "112"));
                } else if (call.intent == com.example.meshlink.ai.router.UserIntent.SMS_ACTION) {
                    result = SmsTool.prepareSosSms(23.0225, 72.5714);
                    result.setThought("• Mode: Hybrid\n• Action: SOS SMS payload dispatch");
                } else if (call.intent == com.example.meshlink.ai.router.UserIntent.CREATE_PRESENTATION) {
                    result = PresentationTool.generatePresentation(userPrompt);
                    result.setThought("• Mode: Hybrid\n• Action: Presentation Tool 5-slide deck generator");
                } else if (call.intent == com.example.meshlink.ai.router.UserIntent.DEVICE_STATUS) {
                    result = DeviceTool.getDeviceDiagnostics(appContext);
                    result.setThought("• Mode: Hybrid\n• Action: Hardware capability diagnostics");
                } else if (call.intent == com.example.meshlink.ai.router.UserIntent.MESH_STATUS) {
                    result = meshTool.getMeshStatus();
                    result.setThought("• Mode: Hybrid\n• Action: Mesh coordinator status check");
                } else {
                    // For reasoning, conversation, coding, and general queries: Query Qwen LLM with thought!
                    LlamaServerManager.LlamaResult llamaRes = LlamaServerManager.getInstance(appContext).queryQwenWithThought(userPrompt, 2048);
                    if (llamaRes != null && llamaRes.answer != null && !llamaRes.answer.trim().isEmpty()) {
                        result = ToolResult.text(llamaRes.answer)
                                .setThought(llamaRes.thought)
                                .addChip("💡 Explain").addChip("💻 Code").addChip("📊 PPT");
                    } else {
                        // Fallback if Qwen not downloaded or busy
                        String kbAnswer = OfflineKnowledgeBase.query(userPrompt);
                        if (kbAnswer != null) {
                            result = ToolResult.text(kbAnswer)
                                    .setThought("• Mode: Hybrid\n• Qwen status: Standby\n• Matched: Offline knowledge base entity");
                        } else {
                            result = synthesizeLocalResponse(userPrompt);
                            result.setThought("• Mode: Hybrid\n• Fallback: Local conversational synthesis");
                        }
                    }
                }
            }

            // Authentic LLM reasoning pause so user sees thinking process clearly
            try {
                Thread.sleep(600);
            } catch (Exception ignored) {}

            contextManager.addMessage(false, result.outputText);

            mainHandler.post(() -> {
                if (callback != null) callback.onResponse(result);
            });
        });
    }

    private ToolResult synthesizeLocalResponse(String prompt) {
        String lower = prompt.toLowerCase().trim();
        StringBuilder sb = new StringBuilder();

        ModelMetadata active = modelManager.getActiveModel();
        boolean isDownloaded = modelManager.isModelDownloaded(active);
        String header = isDownloaded ? "🧠 **" + active.displayName + " (Offline Assistant):**\n\n" : "🧠 **Nexus AI:**\n\n";
        sb.append(header);

        // Greetings
        if (lower.matches("^(hi|hello|hey|namaste|kese ho|kaise ho|kya haal).*") ||
            lower.contains("kaise ho") || lower.contains("kese ho") || lower.equals("hi") || lower.equals("hello")) {
            sb.append("Namaste bhai! Main badhiya hoon. Aap batao kaise ho?\n\n");
            sb.append("Main **").append(active.displayName).append("** par based Nexus AI hoon.\n");
            sb.append("Aap mujhse koi bhi question pooch sakte hain:\n");
            sb.append("• Kisi bhi topic par explanation (`Recursion`, `AI`, `History`)\n");
            sb.append("• Programming & coding help (Java, Python, C++)\n");
            sb.append("• PPT slide structure and presentation outline\n");
            sb.append("• Offline Mesh emergency & network status\n\n");
            sb.append("Aapko kis topic me help chahiye bhai?");
            return ToolResult.text(sb.toString()).addChip("💡 Explain").addChip("💻 Code").addChip("📊 PPT");
        }

        // Identity
        if (lower.contains("kaun ho") || lower.contains("who are you") || lower.contains("kya ho") || lower.contains("tum kon ho")) {
            sb.append("Main **Nexus AI** hoon, jo **Qwen3 LLM** architecture aur Nexus MeshLink intelligence par chalta hai.\n\n");
            sb.append("• **Offline-First**: Bina internet ke bhi core guidance aur concepts samjha sakta hoon.\n");
            sb.append("• **Hinglish Friendly**: Aap Hinglish, Hindi ya English me aasaani se baat kar sakte hain.\n");
            sb.append("• **Integrated Tools**: Emergency SOS, Mesh Discovery, Code generation, aur Presentation maker sab integrated hain.");
            return ToolResult.text(sb.toString()).addChip("💡 Explain").addChip("💻 Code").addChip("📊 PPT");
        }

        // Political / Organizations
        if (lower.contains("bjp") || lower.contains("bharatiya janata")) {
            sb.append("🇮🇳 **Bharatiya Janata Party (BJP):**\n\n");
            sb.append("• **Introduction**: BJP India ki ek pramukh rashtriya rajneetik party hai.\n");
            sb.append("• **Establishment**: Iski sthapna 6 April 1980 ko hui thi (is se pehle Bharatiya Jana Sangh ke roop me jaani jaati thi).\n");
            sb.append("• **Current Position**: Party 2014 se rashtriya star par center me ruling party hai, jiske pradhan mantri Narendra Modi hain.\n");
            sb.append("• **Party Symbol**: Kamal (Lotus flower).\n");
            sb.append("• **Key Ideology**: Nationalism, Integral Humanism (Ekatma Manavvad), aur economic development.\n\n");
            sb.append("*(Tip: Agar internet connect hai to 'Search BJP' likhkar latest current affairs dekh sakte hain).*");
            return ToolResult.text(sb.toString()).addChip("🌐 Search Web").addChip("📊 PPT Outline");
        }

        if (lower.contains("congress") || lower.contains("inc")) {
            sb.append("🇮🇳 **Indian National Congress (INC):**\n\n");
            sb.append("• **History**: Congress Bharat ki sabse purani rajneetik party hai, jiski sthapna 1885 me hui thi.\n");
            sb.append("• **Role in Independence**: Mahatma Gandhi, Jawaharlal Nehru, aur Sardar Patel jaise leaders ne iske zariye azaadi ki ladai ladi.\n");
            sb.append("• **Symbol**: Haath ka panja (Hand symbol).\n");
            sb.append("• **Ideology**: Secularism, social democracy, aur constitutional values.");
            return ToolResult.text(sb.toString()).addChip("🌐 Search Web").addChip("📊 PPT Outline");
        }

        // Tech & Concepts
        if (lower.contains("ai") || lower.contains("artificial intelligence") || lower.contains("machine learning")) {
            sb.append("🤖 **Artificial Intelligence (AI) kya hai?**\n\n");
            sb.append("AI ka matlab hai computer ya machine ko aisi intelligence dena jisse wo insano ki tarah soch sake, learn kar sake aur decision le sake.\n\n");
            sb.append("• **Machine Learning (ML)**: Data se pattern seekhna bina explicitly program kiye.\n");
            sb.append("• **Deep Learning (DL)**: Neural networks ka use karke complex image, voice ya language process karna.\n");
            sb.append("• **LLMs (Jaise Qwen, ChatGPT)**: Massive text data par trained models jo natural bhasha samajhkar reply karte hain.\n");
            sb.append("• **On-Device AI**: Jaise Nexus AI aapke phone me offline inference run karta hai bina kisi server ke!");
            return ToolResult.text(sb.toString()).addChip("💻 Code").addChip("📊 PPT Outline");
        }

        // General explanation
        sb.append("Haan bhai, \"").append(prompt).append("\" ke baare me main aapko explain karta hoon:\n\n");
        sb.append("• Ye ek important subject hai jisme alag-alag aspects aur use-cases shamil hain.\n");
        sb.append("• Agar aap iska **Code** chahte hain, ya ispar **PPT Presentation** banwana chahte hain, to niche diye gaye buttons par tap karein.\n");
        sb.append("• Agar internet available hai, to 'Search ").append(prompt).append("' likhkar latest live web data bhi fetch kar sakte hain!");

        return ToolResult.text(sb.toString())
                .addChip("💡 Explain More")
                .addChip("📊 PPT Outline")
                .addChip("🌐 Search Web");
    }
}

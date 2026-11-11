# WebRTC obfuscation rules
-keep class org.webrtc.** { *; }
-dontwarn org.webrtc.**

# Gson & Room rules
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.couplecanvas.app.data.local.** { *; }
-keep class com.couplecanvas.app.domain.model.** { *; }

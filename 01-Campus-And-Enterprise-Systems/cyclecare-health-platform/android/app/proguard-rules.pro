# CycleCare Proguard Rules
-keep class com.cyclecare.models.** { *; }
-keep class com.cyclecare.database.entity.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

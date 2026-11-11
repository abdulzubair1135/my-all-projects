# Proguard rules for Personal Life Vault
-keepclassmembers class * {
    @androidx.room.Entity *;
    @androidx.room.Dao *;
}
-keepattributes Signature
-keepattributes *Annotation*

@rem Basic Gradle Wrapper Invoker for Windows
@echo off
where gradle >nul 2>nul
if %ERRORLEVEL% equ 0 (
    gradle %*
) else (
    echo [NOTE] Gradle is not in PATH. Please run in Android Studio or install Gradle.
)

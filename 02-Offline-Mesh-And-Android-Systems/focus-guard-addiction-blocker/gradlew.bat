@echo off
chcp 65001 >nul
if not defined JAVA_HOME (
    set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
)
"%JAVA_HOME%\bin\java.exe" -Xmx2048m -Dfile.encoding=UTF-8 -jar "C:\Users\abdul\.gradle\installed-gradle\gradle-8.7\lib\gradle-launcher-8.7.jar" %*

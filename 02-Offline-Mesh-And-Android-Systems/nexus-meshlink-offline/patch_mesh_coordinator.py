import os

path = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\app\src\main\java\com\example\meshlink\mesh\MeshCoordinator.java"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add import
imp_target = "import com.example.meshlink.social.FollowManager;"
imp_repl = "import com.example.meshlink.social.FollowManager;\nimport com.example.meshlink.browser.LocalHttpServer;"
if imp_target in text and "import com.example.meshlink.browser.LocalHttpServer;" not in text:
    text = text.replace(imp_target, imp_repl, 1)

# 2. Add field
fld_target = "private DatagramSocket voiceRelaySocket;"
fld_repl = "private LocalHttpServer localHttpServer;\n    private DatagramSocket voiceRelaySocket;"
if fld_target in text and "private LocalHttpServer localHttpServer;" not in text:
    text = text.replace(fld_target, fld_repl, 1)

# 3. Add start in startMesh
st_target = "startVoiceRelay();"
st_repl = """startVoiceRelay();
        try {
            if (localHttpServer == null) {
                localHttpServer = new LocalHttpServer(8888, context, this);
                localHttpServer.start();
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to launch LocalHttpServer: " + e.getMessage());
        }"""
if st_target in text and "localHttpServer = new LocalHttpServer" not in text:
    text = text.replace(st_target, st_repl, 1)

# 4. Add stop in stopMesh
sp_target = "closeVoiceRelaySocket();"
sp_repl = """closeVoiceRelaySocket();
        if (localHttpServer != null) {
            localHttpServer.stop();
            localHttpServer = null;
        }"""
if sp_target in text and "localHttpServer.stop();" not in text:
    text = text.replace(sp_target, sp_repl, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("MeshCoordinator successfully patched with LocalHttpServer!")

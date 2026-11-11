import os

# 1. Patch VoiceCallActivity.java
voice_path = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\app\src\main\java\com\example\meshlink\calls\VoiceCallActivity.java"
with open(voice_path, "r", encoding="utf-8") as f:
    v_text = f.read()

v_text = v_text.replace(
    'private volatile String peerIp = "192.168.49.1";',
    'private volatile String peerIp = null;'
)

with open(voice_path, "w", encoding="utf-8") as f:
    f.write(v_text)
print("VoiceCallActivity.java patched!")

# 2. Patch VideoCallActivity.java
video_path = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\app\src\main\java\com\example\meshlink\calls\VideoCallActivity.java"
with open(video_path, "r", encoding="utf-8") as f:
    vid_text = f.read()

vid_text = vid_text.replace(
    'private volatile String peerIp = "192.168.49.1";',
    'private volatile String peerIp = null;'
)

oppo_check = """        initViews();
        checkAndRequestPermissions();

        // Hardware Check: If device is Oppo Reno2 F (CPH1989) or front camera is broken, default to Back Camera!
        if (Build.MODEL.contains("CPH1989") || Build.MANUFACTURER.equalsIgnoreCase("oppo")) {
            currentCameraId = Camera.CameraInfo.CAMERA_FACING_BACK;
            Log.i(TAG, "Oppo device detected: Defaulting to Back Camera (front camera bypass).");
        }"""

if 'Build.MODEL.contains("CPH1989")' not in vid_text:
    vid_text = vid_text.replace(
        """        initViews();
        checkAndRequestPermissions();""",
        oppo_check
    )

with open(video_path, "w", encoding="utf-8") as f:
    f.write(vid_text)
print("VideoCallActivity.java patched with Oppo back camera logic!")

# 3. Patch CallsFragment.java
calls_frag_path = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\app\src\main\java\com\example\meshlink\calls\CallsFragment.java"
with open(calls_frag_path, "r", encoding="utf-8") as f:
    cf_text = f.read()

old_voice_btn = """            btnVoice.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VoiceCallActivity.class);
                intent.putExtra("PEER_NAME", "P2P Peer (Test)");
                intent.putExtra("PEER_IP", com.example.meshlink.mesh.MeshCoordinator.getLocalIpAddress());
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });"""

new_voice_btn = """            btnVoice.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VoiceCallActivity.class);
                intent.putExtra("PEER_NAME", "Broadcast Mesh");
                intent.putExtra("PEER_ID", "ALL");
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });"""

old_video_btn = """            btnVideo.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VideoCallActivity.class);
                intent.putExtra("PEER_NAME", "P2P Peer (Test)");
                intent.putExtra("PEER_IP", com.example.meshlink.mesh.MeshCoordinator.getLocalIpAddress());
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });"""

new_video_btn = """            btnVideo.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VideoCallActivity.class);
                intent.putExtra("PEER_NAME", "Broadcast Mesh");
                intent.putExtra("PEER_ID", "ALL");
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });"""

cf_text = cf_text.replace(old_voice_btn, new_voice_btn).replace(old_video_btn, new_video_btn)
with open(calls_frag_path, "w", encoding="utf-8") as f:
    f.write(cf_text)
print("CallsFragment.java patched!")

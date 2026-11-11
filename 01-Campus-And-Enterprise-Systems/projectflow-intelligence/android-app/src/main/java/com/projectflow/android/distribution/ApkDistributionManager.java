package com.projectflow.android.distribution;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import androidx.core.content.FileProvider;
import com.projectflow.android.data.remote.ApiClient;
import com.projectflow.android.data.remote.ApiService;
import com.projectflow.android.data.remote.model.DtoModels.ReleaseDto;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import java.io.*;
import java.security.MessageDigest;

public class ApkDistributionManager {

    public interface ReleaseCallback {
        void onSuccess(ReleaseDto release);
        void onError(String message);
    }

    public interface ShareCallback {
        void onProgress(String status);
        void onReady();
        void onError(String message);
    }

    public static void fetchLatestRelease(Context context, ReleaseCallback callback) {
        ApiService api = ApiClient.getService(context);
        api.getLatestRelease("com.projectflow.android").enqueue(new Callback<ReleaseDto>() {
            @Override
            public void onResponse(Call<ReleaseDto> call, Response<ReleaseDto> response) {
                if (response.isSuccessful() && response.body() != null) {
                    callback.onSuccess(response.body());
                } else {
                    callback.onError("No remote release metadata found on server.");
                }
            }

            @Override
            public void onFailure(Call<ReleaseDto> call, Throwable t) {
                callback.onError("Network error fetching release: " + t.getMessage());
            }
        });
    }

    public static void prepareAndShareApk(Activity activity, ReleaseDto release, ShareCallback callback) {
        new Thread(() -> {
            Handler mainHandler = new Handler(Looper.getMainLooper());
            File releasesDir = new File(activity.getCacheDir(), "releases");
            if (!releasesDir.exists()) {
                releasesDir.mkdirs();
            }

            File targetApk = null;

            // Step 1: Check if remote release is available
            if (release != null && release.id != null) {
                mainHandler.post(() -> callback.onProgress("Verifying official release package..."));
                String filename = release.artifactFilename != null ? release.artifactFilename : "ProjectFlow-Intelligence-Release.apk";
                File cachedFile = new File(releasesDir, filename);

                boolean validCache = false;
                if (cachedFile.exists() && cachedFile.length() > 0) {
                    String hash = computeSha256(cachedFile);
                    if (release.sha256Checksum == null || release.sha256Checksum.equalsIgnoreCase(hash)) {
                        validCache = true;
                        targetApk = cachedFile;
                    }
                }

                if (!validCache) {
                    mainHandler.post(() -> callback.onProgress("Downloading official signed APK release..."));
                    try {
                        ApiService api = ApiClient.getService(activity);
                        Response<ResponseBody> resp = api.downloadRelease(release.id).execute();
                        if (resp.isSuccessful() && resp.body() != null) {
                            saveStreamToFile(resp.body().byteStream(), cachedFile);
                            if (cachedFile.exists() && cachedFile.length() > 0) {
                                String downloadedHash = computeSha256(cachedFile);
                                if (release.sha256Checksum != null && !release.sha256Checksum.equalsIgnoreCase(downloadedHash)) {
                                    mainHandler.post(() -> callback.onError("Downloaded APK SHA-256 checksum mismatch."));
                                    return;
                                }
                                targetApk = cachedFile;
                            }
                        }
                    } catch (Exception e) {
                        // Fallback to installed APK if network or download fails
                    }
                }
            }

            // Step 2: Fallback to verified installed standalone APK if remote download not available
            if (targetApk == null || !targetApk.exists() || targetApk.length() == 0) {
                mainHandler.post(() -> callback.onProgress("Preparing verified installed standalone APK..."));
                try {
                    String sourceApkPath = activity.getApplicationInfo().sourceDir;
                    File sourceFile = new File(sourceApkPath);
                    if (sourceFile.exists() && sourceFile.length() > 0) {
                        File fallbackFile = new File(releasesDir, "ProjectFlow-Intelligence-v2.0.0.apk");
                        copyFile(sourceFile, fallbackFile);

                        // Validate standalone installability via PackageParser check
                        PackageManager pm = activity.getPackageManager();
                        PackageInfo pi = pm.getPackageArchiveInfo(fallbackFile.getAbsolutePath(), 0);
                        if (pi != null) {
                            targetApk = fallbackFile;
                        } else {
                            mainHandler.post(() -> callback.onError("Installed APK is not a complete standalone package."));
                            return;
                        }
                    }
                } catch (Exception e) {
                    mainHandler.post(() -> callback.onError("Failed preparing installed APK: " + e.getMessage()));
                    return;
                }
            }

            if (targetApk == null || !targetApk.exists()) {
                mainHandler.post(() -> callback.onError("No valid APK installer available to share."));
                return;
            }

            // Step 3: Secure content URI generation via FileProvider
            final File finalApk = targetApk;
            mainHandler.post(() -> {
                try {
                    Uri apkUri = FileProvider.getUriForFile(
                            activity,
                            activity.getPackageName() + ".fileprovider",
                            finalApk
                    );

                    Intent shareIntent = new Intent(Intent.ACTION_SEND);
                    shareIntent.setType("application/vnd.android.package-archive");
                    shareIntent.putExtra(Intent.EXTRA_STREAM, apkUri);
                    shareIntent.putExtra(Intent.EXTRA_SUBJECT, "ProjectFlow Intelligence APK Installer");
                    shareIntent.putExtra(Intent.EXTRA_TEXT, "Here is the official ProjectFlow Intelligence APK installer. Tap to download and install on your device.");
                    shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

                    callback.onReady();
                    activity.startActivity(Intent.createChooser(shareIntent, "Share ProjectFlow Intelligence APK via"));
                } catch (Exception e) {
                    callback.onError("Error launching share sheet: " + e.getMessage());
                }
            });
        }).start();
    }

    private static void saveStreamToFile(InputStream in, File target) throws IOException {
        try (OutputStream out = new FileOutputStream(target)) {
            byte[] buf = new byte[8192];
            int len;
            while ((len = in.read(buf)) != -1) {
                out.write(buf, 0, len);
            }
            out.flush();
        }
    }

    private static void copyFile(File src, File dst) throws IOException {
        try (InputStream in = new FileInputStream(src); OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[8192];
            int len;
            while ((len = in.read(buf)) != -1) {
                out.write(buf, 0, len);
            }
            out.flush();
        }
    }

    public static String computeSha256(File file) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            try (InputStream is = new FileInputStream(file)) {
                byte[] buffer = new byte[8192];
                int read;
                while ((read = is.read(buffer)) > 0) {
                    digest.update(buffer, 0, read);
                }
            }
            byte[] hash = digest.digest();
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }
}

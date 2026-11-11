package com.cyclecare.utils;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.LruCache;
import android.widget.ImageView;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ImageLoader {
    private static ImageLoader instance;
    private final LruCache<String, Bitmap> memoryCache;
    private final ExecutorService executor;
    private final Handler mainHandler;

    private ImageLoader() {
        int maxMemory = (int) (Runtime.getRuntime().maxMemory() / 1024);
        int cacheSize = maxMemory / 8; // 1/8th of memory for cache
        memoryCache = new LruCache<String, Bitmap>(cacheSize) {
            @Override
            protected int sizeOf(String key, Bitmap bitmap) {
                return bitmap.getByteCount() / 1024;
            }
        };
        executor = Executors.newFixedThreadPool(4);
        mainHandler = new Handler(Looper.getMainLooper());
    }

    public static synchronized ImageLoader getInstance() {
        if (instance == null) {
            instance = new ImageLoader();
        }
        return instance;
    }

    public interface ImageCallback {
        void onLoaded(Bitmap bitmap);
        void onError();
    }

    public void loadImage(String imageUrl, ImageView imageView, int placeholderResId) {
        if (placeholderResId != 0) {
            imageView.setImageResource(placeholderResId);
        }

        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            return;
        }

        Bitmap cached = memoryCache.get(imageUrl);
        if (cached != null) {
            imageView.setImageBitmap(cached);
            return;
        }

        // Tag view to avoid race conditions with recycled views
        imageView.setTag(imageUrl);

        executor.execute(() -> {
            Bitmap bitmap = downloadBitmap(imageUrl);
            if (bitmap != null) {
                memoryCache.put(imageUrl, bitmap);
                mainHandler.post(() -> {
                    if (imageUrl.equals(imageView.getTag())) {
                        imageView.setImageBitmap(bitmap);
                    }
                });
            }
        });
    }

    public void fetchBitmap(String imageUrl, ImageCallback callback) {
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            if (callback != null) callback.onError();
            return;
        }

        Bitmap cached = memoryCache.get(imageUrl);
        if (cached != null) {
            if (callback != null) callback.onLoaded(cached);
            return;
        }

        executor.execute(() -> {
            Bitmap bitmap = downloadBitmap(imageUrl);
            mainHandler.post(() -> {
                if (bitmap != null) {
                    memoryCache.put(imageUrl, bitmap);
                    if (callback != null) callback.onLoaded(bitmap);
                } else {
                    if (callback != null) callback.onError();
                }
            });
        });
    }

    public Bitmap downloadBitmapSync(String imageUrl) {
        if (imageUrl == null || imageUrl.trim().isEmpty()) return null;
        Bitmap cached = memoryCache.get(imageUrl);
        if (cached != null) return cached;
        Bitmap downloaded = downloadBitmap(imageUrl);
        if (downloaded != null) {
            memoryCache.put(imageUrl, downloaded);
        }
        return downloaded;
    }

    private Bitmap downloadBitmap(String urlStr) {
        HttpURLConnection conn = null;
        InputStream in = null;
        try {
            URL url = new URL(urlStr);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CycleCareApp/1.0");
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(15000);
            conn.setInstanceFollowRedirects(true);
            conn.connect();

            if (conn.getResponseCode() == HttpURLConnection.HTTP_OK) {
                in = conn.getInputStream();
                return BitmapFactory.decodeStream(in);
            }
        } catch (Exception ignored) {
        } finally {
            try {
                if (in != null) in.close();
                if (conn != null) conn.disconnect();
            } catch (Exception ignored) {}
        }
        return null;
    }
}

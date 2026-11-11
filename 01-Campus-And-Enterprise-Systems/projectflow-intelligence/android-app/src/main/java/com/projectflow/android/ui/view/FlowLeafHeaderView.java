package com.projectflow.android.ui.view;

import android.content.Context;
import android.graphics.*;
import android.util.AttributeSet;
import android.view.View;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;
import java.util.Random;

/**
 * Organic Flow & Floating Leaf Canvas Animation
 * Renders ambient drifting leaves and a gentle flowing wave across the header.
 * Optimized for 60fps with zero allocations in onDraw.
 */
public class FlowLeafHeaderView extends View {

    private static class LeafParticle {
        float x, y;
        float speedX, speedY;
        float rotation, rotSpeed;
        float size;
        int color;
        int alpha;
        float oscillationPhase;
        float oscillationSpeed;
    }

    private static final int LEAF_COUNT = 7;
    private final LeafParticle[] leaves = new LeafParticle[LEAF_COUNT];
    private final Random random = new Random();

    private final Paint leafPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint wavePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path leafPath = new Path();
    private final Path wavePath = new Path();
    private final Matrix transformMatrix = new Matrix();

    private int viewWidth = 0;
    private int viewHeight = 0;
    private boolean isRunning = false;
    private long lastTime = 0;
    private float wavePhase = 0f;

    public FlowLeafHeaderView(Context context) {
        super(context);
        init();
    }

    public FlowLeafHeaderView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public FlowLeafHeaderView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        leafPaint.setStyle(Paint.Style.FILL);
        wavePaint.setStyle(Paint.Style.STROKE);
        wavePaint.setStrokeWidth(getResources().getDisplayMetrics().density * 1.5f);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        viewWidth = w;
        viewHeight = h;
        if (w > 0 && h > 0) {
            initParticles();
        }
    }

    private void initParticles() {
        int[] palette = new int[] {
            ContextCompat.getColor(getContext(), R.color.chart_done),        // Emerald Jade
            ContextCompat.getColor(getContext(), R.color.secondary_sand),    // Sand / Clay Amber
            ContextCompat.getColor(getContext(), R.color.chart_accent_cyan), // Riverstone Turquoise
            ContextCompat.getColor(getContext(), R.color.primary_earth)      // Mineral Sage
        };

        float density = getResources().getDisplayMetrics().density;

        for (int i = 0; i < LEAF_COUNT; i++) {
            LeafParticle p = new LeafParticle();
            resetParticle(p, true, density, palette);
            leaves[i] = p;
        }
    }

    private void resetParticle(LeafParticle p, boolean randomX, float density, int[] palette) {
        p.x = randomX ? random.nextFloat() * (viewWidth > 0 ? viewWidth : 800) : -40f * density;
        p.y = 8f * density + random.nextFloat() * (viewHeight > 0 ? (viewHeight - 16f * density) : 40f * density);
        p.speedX = density * (14f + random.nextFloat() * 18f); // horizontal drift
        p.speedY = density * (2f + random.nextFloat() * 4f);
        p.size = density * (5f + random.nextFloat() * 6f);
        p.rotation = random.nextFloat() * 360f;
        p.rotSpeed = (random.nextBoolean() ? 1 : -1) * (18f + random.nextFloat() * 30f);
        p.color = palette[random.nextInt(palette.length)];
        p.alpha = 45 + random.nextInt(65); // subtle 18% - 42% opacity
        p.oscillationPhase = random.nextFloat() * 6.28f;
        p.oscillationSpeed = 1.2f + random.nextFloat() * 1.8f;
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        isRunning = true;
        lastTime = System.currentTimeMillis();
        postInvalidateOnAnimation();
    }

    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        isRunning = false;
    }

    @Override
    protected void onVisibilityChanged(View changedView, int visibility) {
        super.onVisibilityChanged(changedView, visibility);
        isRunning = (visibility == VISIBLE);
        if (isRunning) {
            lastTime = System.currentTimeMillis();
            postInvalidateOnAnimation();
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (viewWidth <= 0 || viewHeight <= 0) return;

        long now = System.currentTimeMillis();
        float dt = (lastTime > 0) ? (now - lastTime) / 1000f : 0.016f;
        lastTime = now;
        if (dt > 0.1f) dt = 0.016f; // Clamp large spikes

        float density = getResources().getDisplayMetrics().density;
        int[] palette = new int[] {
            ContextCompat.getColor(getContext(), R.color.chart_done),
            ContextCompat.getColor(getContext(), R.color.secondary_sand),
            ContextCompat.getColor(getContext(), R.color.chart_accent_cyan),
            ContextCompat.getColor(getContext(), R.color.primary_earth)
        };

        // 1. Draw subtle ambient stream wave along bottom of toolbar
        wavePhase += dt * 1.2f;
        wavePath.reset();
        float waveY = viewHeight - (density * 3f);
        wavePath.moveTo(0, waveY);
        for (float x = 0; x <= viewWidth; x += 30f * density) {
            float yOffset = (float) Math.sin((x / (float) viewWidth) * 5f + wavePhase) * (density * 2.2f);
            wavePath.lineTo(x, waveY + yOffset);
        }
        wavePaint.setColor(ContextCompat.getColor(getContext(), R.color.chart_accent_cyan));
        wavePaint.setAlpha(28); // very subtle 11% stream line
        canvas.drawPath(wavePath, wavePaint);

        // 2. Draw animated floating leaves
        for (LeafParticle p : leaves) {
            if (p == null) continue;

            p.x += p.speedX * dt;
            p.oscillationPhase += p.oscillationSpeed * dt;
            p.y += (float) Math.sin(p.oscillationPhase) * (p.speedY * dt * 2.5f);
            p.rotation += p.rotSpeed * dt;

            // Loop back when drifting past the right edge
            if (p.x > viewWidth + (p.size * 2)) {
                resetParticle(p, false, density, palette);
            }

            // Build leaf path centered at (0, 0)
            leafPath.reset();
            float halfLen = p.size;
            float halfWidth = p.size * 0.48f;
            leafPath.moveTo(0, -halfLen);
            leafPath.quadTo(halfWidth, 0, 0, halfLen);
            leafPath.quadTo(-halfWidth, 0, 0, -halfLen);
            leafPath.close();

            // Transform matrix
            transformMatrix.reset();
            transformMatrix.postRotate(p.rotation);
            transformMatrix.postTranslate(p.x, p.y);
            leafPath.transform(transformMatrix);

            leafPaint.setColor(p.color);
            leafPaint.setAlpha(p.alpha);
            canvas.drawPath(leafPath, leafPaint);
        }

        if (isRunning) {
            postInvalidateOnAnimation();
        }
    }
}

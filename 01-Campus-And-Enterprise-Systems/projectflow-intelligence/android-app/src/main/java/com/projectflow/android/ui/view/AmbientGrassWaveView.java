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
 * Ambient Grass & Stream Wave Canvas View for Drawer Navigation.
 * Renders gently swaying natural grass blades at the bottom and flowing waves/leaves throughout.
 * Optimized for 60fps with zero allocations in onDraw.
 */
public class AmbientGrassWaveView extends View {

    private static class GrassBlade {
        float x;
        float height;
        float baseWidth;
        float swayAngleMax;
        float phase;
        float swaySpeed;
        int color;
    }

    private static class FloatingLeaf {
        float x, y;
        float speedX, speedY;
        float rotation, rotSpeed;
        float size;
        int color;
        int alpha;
        float phase;
        float phaseSpeed;
    }

    private static final int GRASS_COUNT = 16;
    private static final int LEAF_COUNT = 6;

    private final GrassBlade[] blades = new GrassBlade[GRASS_COUNT];
    private final FloatingLeaf[] leaves = new FloatingLeaf[LEAF_COUNT];
    private final Random random = new Random();

    private final Paint grassPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint leafPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint wavePaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final Path bladePath = new Path();
    private final Path leafPath = new Path();
    private final Path wavePath1 = new Path();
    private final Path wavePath2 = new Path();
    private final Matrix leafMatrix = new Matrix();

    private int viewWidth = 0;
    private int viewHeight = 0;
    private boolean isRunning = false;
    private long lastTime = 0;
    private float waveTime = 0f;

    public AmbientGrassWaveView(Context context) {
        super(context);
        init();
    }

    public AmbientGrassWaveView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public AmbientGrassWaveView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        grassPaint.setStyle(Paint.Style.FILL);
        leafPaint.setStyle(Paint.Style.FILL);

        wavePaint.setStyle(Paint.Style.STROKE);
        wavePaint.setStrokeCap(Paint.Cap.ROUND);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        viewWidth = w;
        viewHeight = h;
        if (w > 0 && h > 0) {
            initElements();
        }
    }

    private void initElements() {
        float density = getResources().getDisplayMetrics().density;

        int[] grassColors = new int[] {
            ContextCompat.getColor(getContext(), R.color.chart_done),        // Emerald Jade
            ContextCompat.getColor(getContext(), R.color.primary_earth),      // Mineral Sage
            ContextCompat.getColor(getContext(), R.color.secondary_sand),    // Sand Amber
            ContextCompat.getColor(getContext(), R.color.chart_accent_cyan)  // Riverstone Turquoise
        };

        // 1. Initialize swaying grass blades at the bottom of the drawer
        float stepX = (viewWidth > 0 ? viewWidth : 600f) / (GRASS_COUNT + 1);
        for (int i = 0; i < GRASS_COUNT; i++) {
            GrassBlade b = new GrassBlade();
            b.x = stepX * (i + 0.5f) + (random.nextFloat() - 0.5f) * (stepX * 0.7f);
            b.height = density * (40f + random.nextFloat() * 45f);
            b.baseWidth = density * (3.5f + random.nextFloat() * 3f);
            b.swayAngleMax = density * (10f + random.nextFloat() * 15f);
            b.phase = random.nextFloat() * 6.28f;
            b.swaySpeed = 1.2f + random.nextFloat() * 1.5f;
            b.color = grassColors[random.nextInt(grassColors.length)];
            blades[i] = b;
        }

        // 2. Initialize drifting leaves
        for (int i = 0; i < LEAF_COUNT; i++) {
            FloatingLeaf l = new FloatingLeaf();
            resetLeaf(l, true, density, grassColors);
            leaves[i] = l;
        }
    }

    private void resetLeaf(FloatingLeaf l, boolean randomY, float density, int[] palette) {
        l.x = -20f * density + random.nextFloat() * ((viewWidth > 0 ? viewWidth : 600f) + 40f * density);
        l.y = randomY ? random.nextFloat() * (viewHeight > 0 ? viewHeight : 1000f) : -20f * density;
        l.speedX = density * (8f + random.nextFloat() * 14f);
        l.speedY = density * (12f + random.nextFloat() * 18f); // slow falling/drifting down
        l.size = density * (5f + random.nextFloat() * 5f);
        l.rotation = random.nextFloat() * 360f;
        l.rotSpeed = (random.nextBoolean() ? 1 : -1) * (20f + random.nextFloat() * 35f);
        l.color = palette[random.nextInt(palette.length)];
        l.alpha = 25 + random.nextInt(40); // 10% - 25% subtle ambient opacity
        l.phase = random.nextFloat() * 6.28f;
        l.phaseSpeed = 1.0f + random.nextFloat() * 1.8f;
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
        if (dt > 0.1f) dt = 0.016f;

        float density = getResources().getDisplayMetrics().density;
        waveTime += dt;

        int[] palette = new int[] {
            ContextCompat.getColor(getContext(), R.color.chart_done),
            ContextCompat.getColor(getContext(), R.color.primary_earth),
            ContextCompat.getColor(getContext(), R.color.secondary_sand),
            ContextCompat.getColor(getContext(), R.color.chart_accent_cyan)
        };

        // 1. Draw Organic Ambient Wave Streams in the background
        wavePaint.setStrokeWidth(density * 1.8f);

        // Wave 1: Gentle flowing curve across upper-mid body
        wavePath1.reset();
        float wave1Y = viewHeight * 0.45f;
        wavePath1.moveTo(0, wave1Y);
        for (float x = 0; x <= viewWidth; x += 30f * density) {
            float offset = (float) Math.sin((x / (float) viewWidth) * 4f + waveTime * 0.9f) * (density * 9f);
            wavePath1.lineTo(x, wave1Y + offset);
        }
        wavePaint.setColor(ContextCompat.getColor(getContext(), R.color.chart_accent_cyan));
        wavePaint.setAlpha(22); // 8% opacity
        canvas.drawPath(wavePath1, wavePaint);

        // Wave 2: Gentle flowing curve across lower body
        wavePath2.reset();
        float wave2Y = viewHeight * 0.72f;
        wavePath2.moveTo(0, wave2Y);
        for (float x = 0; x <= viewWidth; x += 30f * density) {
            float offset = (float) Math.cos((x / (float) viewWidth) * 5f + waveTime * 1.1f) * (density * 11f);
            wavePath2.lineTo(x, wave2Y + offset);
        }
        wavePaint.setColor(ContextCompat.getColor(getContext(), R.color.chart_done));
        wavePaint.setAlpha(20); // 8% opacity
        canvas.drawPath(wavePath2, wavePaint);

        // 2. Draw Gentle Swaying Grass Blades at the bottom
        float groundY = viewHeight;
        for (GrassBlade b : blades) {
            if (b == null) continue;

            b.phase += b.swaySpeed * dt;
            float currentTipOffset = (float) Math.sin(b.phase) * b.swayAngleMax;

            bladePath.reset();
            bladePath.moveTo(b.x - b.baseWidth, groundY);
            // Tip bends with the wind
            bladePath.quadTo(b.x - (b.baseWidth * 0.4f), groundY - (b.height * 0.55f), b.x + currentTipOffset, groundY - b.height);
            bladePath.quadTo(b.x + (b.baseWidth * 0.4f), groundY - (b.height * 0.55f), b.x + b.baseWidth, groundY);
            bladePath.close();

            grassPaint.setColor(b.color);
            grassPaint.setAlpha(38); // 15% subtle organic silhouette
            canvas.drawPath(bladePath, grassPaint);
        }

        // 3. Draw Ambient Drifting Leaves
        for (FloatingLeaf l : leaves) {
            if (l == null) continue;

            l.phase += l.phaseSpeed * dt;
            l.x += l.speedX * dt + (float) Math.cos(l.phase) * (density * 3.5f * dt);
            l.y += l.speedY * dt;
            l.rotation += l.rotSpeed * dt;

            if (l.y > viewHeight + (l.size * 2) || l.x > viewWidth + (l.size * 2)) {
                resetLeaf(l, false, density, palette);
            }

            leafPath.reset();
            float halfLen = l.size;
            float halfW = l.size * 0.48f;
            leafPath.moveTo(0, -halfLen);
            leafPath.quadTo(halfW, 0, 0, halfLen);
            leafPath.quadTo(-halfW, 0, 0, -halfLen);
            leafPath.close();

            leafMatrix.reset();
            leafMatrix.postRotate(l.rotation);
            leafMatrix.postTranslate(l.x, l.y);
            leafPath.transform(leafMatrix);

            leafPaint.setColor(l.color);
            leafPaint.setAlpha(l.alpha);
            canvas.drawPath(leafPath, leafPaint);
        }

        if (isRunning) {
            postInvalidateOnAnimation();
        }
    }
}

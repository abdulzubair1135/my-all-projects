package com.projectflow.android.ui.view;

import android.content.Context;
import android.graphics.*;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import androidx.annotation.Nullable;
import java.util.Random;

/**
 * Living Botanical Plant with Swaying Leaves & Flowers reacting to Wind.
 * Positioned on the right screen edge in the background behind the form & text,
 * scaling from the footer all the way up to "Welcome Back".
 * Features organic curving stems, multi-petal blooming flowers, flutter physics,
 * periodic wind gusts, and drifting pollen particles.
 */
public class LivingPlantWindView extends View {

    private final Paint stemPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint leafPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint leafVeinPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint flowerPetalPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint flowerCenterPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint potPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint potRimPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint windPollenPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final Path stemPath = new Path();
    private final Path branchPath = new Path();
    private final Path leafPath = new Path();
    private final Path potPath = new Path();
    private final Matrix transformMatrix = new Matrix();

    // Wind & Sway Physics
    private float baseSwayAngle = 0f;
    private float swayVelocity = 0f;
    private float windGustStrength = 0f;
    private float nextGustTimer = 2.0f;
    private float timeElapsed = 0f;
    private long lastFrameTime = 0;
    private boolean isRunning = false;

    // Drifting Pollen Particles
    private static class Pollen {
        float x, y;
        float vx, vy;
        float radius;
        int alpha;
    }
    private static final int POLLEN_COUNT = 16;
    private final Pollen[] pollens = new Pollen[POLLEN_COUNT];
    private final Random random = new Random();

    public LivingPlantWindView(Context context) {
        super(context);
        init();
    }

    public LivingPlantWindView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public LivingPlantWindView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        stemPaint.setStyle(Paint.Style.STROKE);
        stemPaint.setStrokeCap(Paint.Cap.ROUND);
        stemPaint.setColor(Color.parseColor("#38523A")); // Deep organic stalk green

        leafPaint.setStyle(Paint.Style.FILL);
        leafPaint.setColor(Color.parseColor("#448A59")); // Lush emerald jade

        leafVeinPaint.setStyle(Paint.Style.STROKE);
        leafVeinPaint.setStrokeWidth(2f);
        leafVeinPaint.setColor(Color.parseColor("#76C993"));

        flowerPetalPaint.setStyle(Paint.Style.FILL);
        flowerPetalPaint.setColor(Color.parseColor("#DE6750")); // Terracotta Coral

        flowerCenterPaint.setStyle(Paint.Style.FILL);
        flowerCenterPaint.setColor(Color.parseColor("#FFC857")); // Pollen gold

        potPaint.setStyle(Paint.Style.FILL);
        potPaint.setColor(Color.parseColor("#503E33")); // Terracotta clay ceramic

        potRimPaint.setStyle(Paint.Style.FILL);
        potRimPaint.setColor(Color.parseColor("#634E41"));

        windPollenPaint.setStyle(Paint.Style.FILL);
        windPollenPaint.setColor(Color.parseColor("#FFEAA7"));

        for (int i = 0; i < POLLEN_COUNT; i++) {
            Pollen p = new Pollen();
            resetPollen(p, true);
            pollens[i] = p;
        }
    }

    private void resetPollen(Pollen p, boolean randomX) {
        p.x = randomX ? random.nextFloat() * (getWidth() > 0 ? getWidth() : 800) : -15f;
        p.y = random.nextFloat() * (getHeight() > 0 ? getHeight() : 1200);
        p.vx = 18f + random.nextFloat() * 30f;
        p.vy = -8f + random.nextFloat() * 18f;
        p.radius = 1.4f + random.nextFloat() * 2.2f;
        p.alpha = 35 + random.nextInt(85);
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        isRunning = true;
        lastFrameTime = System.currentTimeMillis();
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
            lastFrameTime = System.currentTimeMillis();
            postInvalidateOnAnimation();
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // Return false so touch passes seamlessly to foreground interactive inputs & buttons
        return false;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        int w = getWidth();
        int h = getHeight();
        if (w <= 0 || h <= 0) return;

        long now = System.currentTimeMillis();
        float dt = (lastFrameTime > 0) ? (now - lastFrameTime) / 1000f : 0.016f;
        lastFrameTime = now;
        if (dt > 0.1f) dt = 0.016f;
        timeElapsed += dt;

        float density = getResources().getDisplayMetrics().density;

        // 1. Wind & Gust Simulation
        nextGustTimer -= dt;
        if (nextGustTimer <= 0) {
            windGustStrength = 18f + random.nextFloat() * 26f; // Periodic wind breeze
            nextGustTimer = 2.8f + random.nextFloat() * 4.0f;
        }
        windGustStrength = Math.max(0, windGustStrength - (dt * 15f));

        // Natural continuous gentle breeze oscillation
        float ambientBreeze = (float) Math.sin(timeElapsed * 1.6f) * 6f + (float) Math.cos(timeElapsed * 3.1f) * 3f;
        float totalWind = ambientBreeze + windGustStrength;

        // Damped harmonic spring physics for plant stem sway
        float springForce = (totalWind - baseSwayAngle) * 7.0f;
        swayVelocity += springForce * dt;
        swayVelocity *= (1.0f - (dt * 2.6f));
        baseSwayAngle += swayVelocity * dt;
        baseSwayAngle = Math.max(-38f, Math.min(38f, baseSwayAngle));

        // 2. Geometry: Positioned on the RIGHT edge of the screen, extending from footer up to Welcome Back
        // The pot is half-clipped by the right edge ("ada body dalo left side ka part he dikna chahiye right screen mai dalo esko")
        float rootX = w * 0.96f;
        float rootY = h * 0.94f; // Sits down at footer level
        float stemHeight = h * 0.77f; // Reaches all the way up to "Welcome Back"!

        // 3. Draw Pot at base (right half clipped off-screen)
        drawPot(canvas, rootX, rootY, density);

        // 4. Main Stem Organic Arching Curve (Cubic Spline)
        float tipX = rootX - (w * 0.28f) + (baseSwayAngle * density * 2.4f);
        float tipY = rootY - stemHeight; // Apex right at Welcome Back level
        float ctrl1X = rootX - (w * 0.14f) + (baseSwayAngle * density * 0.9f);
        float ctrl1Y = rootY - (stemHeight * 0.35f);
        float ctrl2X = rootX - (w * 0.32f) + (baseSwayAngle * density * 1.8f);
        float ctrl2Y = rootY - (stemHeight * 0.70f);

        stemPath.reset();
        stemPath.moveTo(rootX, rootY);
        stemPath.cubicTo(ctrl1X, ctrl1Y, ctrl2X, ctrl2Y, tipX, tipY);
        stemPaint.setStrokeWidth(density * 5.2f);
        canvas.drawPath(stemPath, stemPaint);

        // 5. Draw 5 Lateral Branches with Leaves & Blooming Flowers extending leftwards
        // Branch 1 (Lower Left, near 0.82h)
        float b1RootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.18f);
        float b1RootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.18f);
        float b1Angle = -76f + (baseSwayAngle * 0.35f) + (float) Math.sin(timeElapsed * 3.6f) * 6f;
        drawBranch(canvas, b1RootX, b1RootY, density * 75f, b1Angle, density, false);

        // Branch 2 (Mid-Lower Left, near 0.68h - with Blooming Flower)
        float b2RootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.36f);
        float b2RootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.36f);
        float b2Angle = -62f + (baseSwayAngle * 0.5f) + (float) Math.cos(timeElapsed * 3.4f) * 6f;
        drawBranch(canvas, b2RootX, b2RootY, density * 92f, b2Angle, density, true);

        // Branch 3 (Mid Left, near 0.54h - lush leaves)
        float b3RootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.54f);
        float b3RootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.54f);
        float b3Angle = -50f + (baseSwayAngle * 0.7f) + (float) Math.sin(timeElapsed * 4.0f) * 7f;
        drawBranch(canvas, b3RootX, b3RootY, density * 110f, b3Angle, density, false);

        // Branch 4 (Upper Mid Left, near 0.38h - with Blooming Flower)
        float b4RootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.72f);
        float b4RootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.72f);
        float b4Angle = -42f + (baseSwayAngle * 0.85f) + (float) Math.cos(timeElapsed * 3.8f) * 7f;
        drawBranch(canvas, b4RootX, b4RootY, density * 95f, b4Angle, density, true);

        // Branch 5 (Upper Left, near 0.26h - beside Welcome Back)
        float b5RootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.88f);
        float b5RootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.88f);
        float b5Angle = -34f + (baseSwayAngle * 0.95f) + (float) Math.sin(timeElapsed * 4.4f) * 8f;
        drawBranch(canvas, b5RootX, b5RootY, density * 72f, b5Angle, density, false);

        // Minor Right Asymmetrical Branch (peeking off edge)
        float bRRootX = getCubicPoint(rootX, ctrl1X, ctrl2X, tipX, 0.45f);
        float bRRootY = getCubicPoint(rootY, ctrl1Y, ctrl2Y, tipY, 0.45f);
        float bRAngle = 26f + (baseSwayAngle * 0.4f);
        drawBranch(canvas, bRRootX, bRRootY, density * 42f, bRAngle, density, false);

        // Top Main Flower (Apex of the Plant, right alongside Welcome Back)
        float flowerFlutter = (float) Math.sin(timeElapsed * 4.8f) * 8f;
        drawBloomingFlower(canvas, tipX, tipY, baseSwayAngle + flowerFlutter, density * 18f, density);

        // 6. Draw Drifting Pollen Particles across the screen
        for (Pollen p : pollens) {
            p.x += (p.vx + windGustStrength * 1.4f) * dt;
            p.y += p.vy * dt;
            if (p.x > w + 25f || p.y < -25f || p.y > h + 25f) {
                resetPollen(p, false);
            }
            windPollenPaint.setAlpha(p.alpha);
            canvas.drawCircle(p.x, p.y, p.radius * density, windPollenPaint);
        }

        if (isRunning) {
            postInvalidateOnAnimation();
        }
    }

    private void drawBranch(Canvas canvas, float startX, float startY, float length, float angleDeg, float density, boolean hasFlower) {
        float rad = (float) Math.toRadians(angleDeg);
        float endX = startX + (float) Math.sin(rad) * length;
        float endY = startY - (float) Math.cos(rad) * length;

        float ctrlX = (startX + endX) / 2f + (density * 6f);
        float ctrlY = (startY + endY) / 2f - (density * 3f);

        branchPath.reset();
        branchPath.moveTo(startX, startY);
        branchPath.quadTo(ctrlX, ctrlY, endX, endY);
        stemPaint.setStrokeWidth(density * 3.4f);
        canvas.drawPath(branchPath, stemPaint);

        // Mid-branch leaf
        float midX = (startX + endX) / 2f;
        float midY = (startY + endY) / 2f;
        drawLeaf(canvas, midX, midY, angleDeg + 36f, density * 24f, density);

        // Secondary mid-branch leaf opposite side
        drawLeaf(canvas, midX - (density * 4f), midY + (density * 2f), angleDeg - 32f, density * 18f, density);

        // End of branch: Flower or large Terminal Leaf
        if (hasFlower) {
            drawBloomingFlower(canvas, endX, endY, angleDeg, density * 15f, density);
        } else {
            drawLeaf(canvas, endX, endY, angleDeg - 24f, density * 28f, density);
        }
    }

    private void drawLeaf(Canvas canvas, float x, float y, float angleDeg, float size, float density) {
        float leafFlutter = (float) Math.sin(timeElapsed * 5.8f + x) * 6f;
        float totalAngle = angleDeg + leafFlutter;

        leafPath.reset();
        float halfW = size * 0.40f;
        leafPath.moveTo(0, 0);
        leafPath.cubicTo(halfW, -size * 0.35f, halfW * 0.85f, -size * 0.85f, 0, -size);
        leafPath.cubicTo(-halfW * 0.85f, -size * 0.85f, -halfW, -size * 0.35f, 0, 0);
        leafPath.close();

        transformMatrix.reset();
        transformMatrix.postRotate(totalAngle);
        transformMatrix.postTranslate(x, y);
        leafPath.transform(transformMatrix);

        leafPaint.setColor(Color.parseColor("#448A59"));
        canvas.drawPath(leafPath, leafPaint);

        // Central vein
        float rad = (float) Math.toRadians(totalAngle);
        float veinEndX = x - (float) Math.sin(rad) * (size * 0.78f);
        float veinEndY = y - (float) Math.cos(rad) * (size * 0.78f);
        canvas.drawLine(x, y, veinEndX, veinEndY, leafVeinPaint);
    }

    private void drawBloomingFlower(Canvas canvas, float centerX, float centerY, float angleDeg, float size, float density) {
        // Draw 5 overlapping petals
        int petalCount = 5;
        float petalRadius = size * 0.58f;
        float petalDistance = size * 0.44f;

        for (int i = 0; i < petalCount; i++) {
            float petalAngle = angleDeg + (i * (360f / petalCount)) + (timeElapsed * 8f);
            float rad = (float) Math.toRadians(petalAngle);
            float px = centerX + (float) Math.sin(rad) * petalDistance;
            float py = centerY - (float) Math.cos(rad) * petalDistance;

            canvas.drawCircle(px, py, petalRadius, flowerPetalPaint);
        }

        // Center Pistil with bright warm gold
        canvas.drawCircle(centerX, centerY, size * 0.40f, flowerCenterPaint);
        // Inner highlight dot
        flowerCenterPaint.setColor(Color.parseColor("#FFF3B0"));
        canvas.drawCircle(centerX - (density * 1.5f), centerY - (density * 1.5f), size * 0.16f, flowerCenterPaint);
        flowerCenterPaint.setColor(Color.parseColor("#FFC857")); // restore
    }

    private void drawPot(Canvas canvas, float centerX, float topY, float density) {
        float potTopW = density * 72f;
        float potBottomW = density * 50f;
        float potH = density * 56f;
        float rimH = density * 11f;

        // Pot Body
        potPath.reset();
        potPath.moveTo(centerX - potTopW / 2f, topY);
        potPath.lineTo(centerX + potTopW / 2f, topY);
        potPath.lineTo(centerX + potBottomW / 2f, topY + potH);
        potPath.lineTo(centerX - potBottomW / 2f, topY + potH);
        potPath.close();
        canvas.drawPath(potPath, potPaint);

        // Pot Rim
        RectF rimRect = new RectF(centerX - (potTopW / 2f) - (density * 4f),
                topY - (density * 3f),
                centerX + (potTopW / 2f) + (density * 4f),
                topY + rimH);
        canvas.drawRoundRect(rimRect, density * 5f, density * 5f, potRimPaint);

        // Soft base shadow
        Paint shadowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        shadowPaint.setColor(Color.parseColor("#15110E"));
        shadowPaint.setStyle(Paint.Style.FILL);
        RectF shadowRect = new RectF(centerX - potBottomW * 0.7f,
                topY + potH - (density * 2f),
                centerX + potBottomW * 0.7f,
                topY + potH + (density * 5f));
        canvas.drawOval(shadowRect, shadowPaint);
    }

    private float getCubicPoint(float p0, float p1, float p2, float p3, float t) {
        float oneMinusT = 1.0f - t;
        return (oneMinusT * oneMinusT * oneMinusT * p0)
                + (3f * oneMinusT * oneMinusT * t * p1)
                + (3f * oneMinusT * t * t * p2)
                + (t * t * t * p3);
    }
}

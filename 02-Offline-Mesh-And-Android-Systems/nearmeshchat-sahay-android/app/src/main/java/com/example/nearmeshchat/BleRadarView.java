package com.example.nearmeshchat;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.SweepGradient;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.LinearInterpolator;
import java.util.ArrayList;
import java.util.List;

public class BleRadarView extends View {

    private Paint ringPaint;
    private Paint sweepPaint;
    private Paint centerNodePaint;
    private Paint peerNodePaint;
    private Paint textPaint;
    private Paint crosshairPaint;

    private float sweepAngle = 0f;
    private ValueAnimator sweepAnimator;
    private final List<PeerNode> nodes = new ArrayList<>();

    public static class PeerNode {
        public String name;
        public float distanceRatio; // 0.2 to 0.8
        public float angleDegrees;

        public PeerNode(String name, float distanceRatio, float angleDegrees) {
            this.name = name;
            this.distanceRatio = distanceRatio;
            this.angleDegrees = angleDegrees;
        }
    }

    public BleRadarView(Context context) {
        super(context);
        init();
    }

    public BleRadarView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public BleRadarView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        ringPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        ringPaint.setColor(Color.parseColor("#407C3AED"));
        ringPaint.setStyle(Paint.Style.STROKE);
        ringPaint.setStrokeWidth(dpToPx(1.5f));

        crosshairPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        crosshairPaint.setColor(Color.parseColor("#257C3AED"));
        crosshairPaint.setStyle(Paint.Style.STROKE);
        crosshairPaint.setStrokeWidth(dpToPx(1f));

        sweepPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        sweepPaint.setStyle(Paint.Style.FILL);

        centerNodePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        centerNodePaint.setColor(Color.parseColor("#3B82F6"));
        centerNodePaint.setStyle(Paint.Style.FILL);

        peerNodePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        peerNodePaint.setColor(Color.parseColor("#10B981"));
        peerNodePaint.setStyle(Paint.Style.FILL);

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.parseColor("#475569"));
        textPaint.setTextSize(spToPx(10));
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        startSweepAnimation();
    }

    public void setPeers(List<String> peerNames) {
        nodes.clear();
        if (peerNames != null && !peerNames.isEmpty()) {
            float angleStep = 360f / peerNames.size();
            for (int i = 0; i < peerNames.size(); i++) {
                float dist = 0.35f + (float) ((i % 3) * 0.18f);
                float angle = i * angleStep + 25f;
                nodes.add(new PeerNode(peerNames.get(i), dist, angle));
            }
        }
        invalidate();
    }

    private void startSweepAnimation() {
        if (sweepAnimator != null && sweepAnimator.isRunning()) return;

        sweepAnimator = ValueAnimator.ofFloat(0f, 360f);
        sweepAnimator.setDuration(2400);
        sweepAnimator.setRepeatCount(ValueAnimator.INFINITE);
        sweepAnimator.setInterpolator(new LinearInterpolator());
        sweepAnimator.addUpdateListener(animation -> {
            sweepAngle = (float) animation.getAnimatedValue();
            invalidate();
        });
        sweepAnimator.start();
    }

    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        if (sweepAnimator != null) {
            sweepAnimator.cancel();
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        float cx = getWidth() / 2f;
        float cy = getHeight() / 2f;
        float maxRadius = Math.min(cx, cy) - dpToPx(16);

        // 1. Concentric Range Rings
        canvas.drawCircle(cx, cy, maxRadius * 0.33f, ringPaint);
        canvas.drawCircle(cx, cy, maxRadius * 0.66f, ringPaint);
        canvas.drawCircle(cx, cy, maxRadius, ringPaint);

        // 2. Crosshairs
        canvas.drawLine(cx - maxRadius, cy, cx + maxRadius, cy, crosshairPaint);
        canvas.drawLine(cx, cy - maxRadius, cx, cy + maxRadius, crosshairPaint);

        // 3. Radar Sweep Beam
        int[] colors = new int[]{Color.TRANSPARENT, Color.parseColor("#057C3AED"), Color.parseColor("#4D7C3AED")};
        float[] positions = new float[]{0.0f, 0.75f, 1.0f};
        SweepGradient gradient = new SweepGradient(cx, cy, colors, positions);
        sweepPaint.setShader(gradient);

        canvas.save();
        canvas.rotate(sweepAngle, cx, cy);
        canvas.drawCircle(cx, cy, maxRadius, sweepPaint);
        canvas.restore();

        // 4. Center Node (YOUR DEVICE)
        centerNodePaint.setColor(Color.parseColor("#2563EB"));
        canvas.drawCircle(cx, cy, dpToPx(8), centerNodePaint);
        centerNodePaint.setColor(Color.parseColor("#93C5FD"));
        canvas.drawCircle(cx, cy, dpToPx(4), centerNodePaint);
        canvas.drawText("YOU", cx, cy + dpToPx(18), textPaint);

        // 5. Surrounding Active Mesh Nodes
        if (nodes.isEmpty()) {
            Paint emptyTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
            emptyTextPaint.setColor(Color.parseColor("#94A3B8"));
            emptyTextPaint.setTextSize(spToPx(11));
            emptyTextPaint.setTextAlign(Paint.Align.CENTER);
            canvas.drawText("Scanning BLE mesh for nearby Sahay nodes...", cx, cy + maxRadius * 0.85f, emptyTextPaint);
        } else {
            for (PeerNode node : nodes) {
                float rad = (float) Math.toRadians(node.angleDegrees);
                float dist = maxRadius * node.distanceRatio;
                float nx = cx + (float) Math.cos(rad) * dist;
                float ny = cy + (float) Math.sin(rad) * dist;

                // Node blip
                peerNodePaint.setColor(Color.parseColor("#34D399"));
                canvas.drawCircle(nx, ny, dpToPx(9), peerNodePaint);
                peerNodePaint.setColor(Color.parseColor("#059669"));
                canvas.drawCircle(nx, ny, dpToPx(5), peerNodePaint);

                String label = node.name;
                if (label.length() > 8) {
                    label = label.substring(0, 8) + "..";
                }
                canvas.drawText(label, nx, ny + dpToPx(16), textPaint);
            }
        }
    }

    private float dpToPx(float dp) {
        return dp * getResources().getDisplayMetrics().density;
    }

    private float spToPx(float sp) {
        return sp * getResources().getDisplayMetrics().scaledDensity;
    }
}

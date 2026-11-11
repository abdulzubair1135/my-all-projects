package com.example.nearmeshchat;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import android.view.animation.LinearInterpolator;

public class SosHoldProgressView extends View {

    public interface OnSosHoldListener {
        void onSosHoldStart();
        void onSosHoldProgress(float progress);
        void onSosHoldCancelled();
        void onSosTriggered();
    }

    private static final long HOLD_DURATION_MS = 2000;

    private Paint outerGlowPaint;
    private Paint trackPaint;
    private Paint progressPaint;
    private Paint innerCirclePaint;
    private Paint textPaint;
    private Paint subTextPaint;
    private Paint iconPaint;

    private RectF arcBounds = new RectF();
    private float currentProgress = 0f;
    private ValueAnimator holdAnimator;
    private boolean isHolding = false;
    private boolean isTriggered = false;

    private OnSosHoldListener listener;
    private Vibrator vibrator;

    public SosHoldProgressView(Context context) {
        super(context);
        init();
    }

    public SosHoldProgressView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public SosHoldProgressView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        vibrator = (Vibrator) getContext().getSystemService(Context.VIBRATOR_SERVICE);

        outerGlowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        outerGlowPaint.setColor(Color.parseColor("#33EF4444"));
        outerGlowPaint.setStyle(Paint.Style.FILL);

        trackPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        trackPaint.setColor(Color.parseColor("#FEE2E2"));
        trackPaint.setStyle(Paint.Style.STROKE);
        trackPaint.setStrokeWidth(dpToPx(6));

        progressPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        progressPaint.setColor(Color.parseColor("#DC2626"));
        progressPaint.setStyle(Paint.Style.STROKE);
        progressPaint.setStrokeWidth(dpToPx(6));
        progressPaint.setStrokeCap(Paint.Cap.ROUND);

        innerCirclePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        innerCirclePaint.setColor(Color.parseColor("#DC2626"));
        innerCirclePaint.setStyle(Paint.Style.FILL);

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.WHITE);
        textPaint.setTextSize(spToPx(16));
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        subTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        subTextPaint.setColor(Color.parseColor("#FEE2E2"));
        subTextPaint.setTextSize(spToPx(10));
        subTextPaint.setTextAlign(Paint.Align.CENTER);

        iconPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        iconPaint.setColor(Color.WHITE);
        iconPaint.setTextSize(spToPx(20));
        iconPaint.setTextAlign(Paint.Align.CENTER);
        iconPaint.setFakeBoldText(true);
    }

    public void setOnSosHoldListener(OnSosHoldListener listener) {
        this.listener = listener;
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int desiredSize = (int) dpToPx(180);
        int width = resolveSize(desiredSize, widthMeasureSpec);
        int height = resolveSize(desiredSize, heightMeasureSpec);
        int size = Math.min(width, height);
        setMeasuredDimension(size, size);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        float cx = getWidth() / 2f;
        float cy = getHeight() / 2f;
        float maxRadius = Math.min(cx, cy) - dpToPx(4);

        // 1. Soft Outer Emergency Glow
        float glowRadius = maxRadius - dpToPx(2);
        if (isHolding) {
            outerGlowPaint.setColor(Color.parseColor("#4DEE2222"));
        } else {
            outerGlowPaint.setColor(Color.parseColor("#26EF4444"));
        }
        canvas.drawCircle(cx, cy, glowRadius, outerGlowPaint);

        // 2. Circular Progress Track
        float strokeRadius = maxRadius - dpToPx(10);
        arcBounds.set(cx - strokeRadius, cy - strokeRadius, cx + strokeRadius, cy + strokeRadius);
        canvas.drawArc(arcBounds, 0, 360, false, trackPaint);

        // 3. Circular Progress Arc
        if (currentProgress > 0) {
            float sweepAngle = currentProgress * 360f;
            canvas.drawArc(arcBounds, -90, sweepAngle, false, progressPaint);
        }

        // 4. Central 3D SOS Button
        float innerRadius = strokeRadius - dpToPx(10);
        if (isHolding) {
            innerCirclePaint.setColor(Color.parseColor("#B91C1C"));
        } else {
            innerCirclePaint.setColor(Color.parseColor("#DC2626"));
        }
        canvas.drawCircle(cx, cy, innerRadius, innerCirclePaint);

        // 5. Text & Icons
        canvas.drawText("(( • ))", cx, cy - dpToPx(14), iconPaint);
        canvas.drawText("EMERGENCY", cx, cy + dpToPx(4), textPaint);
        canvas.drawText("SOS", cx, cy + dpToPx(18), textPaint);

        if (isHolding) {
            int pct = (int) (currentProgress * 100);
            canvas.drawText("HOLD " + pct + "%", cx, cy + dpToPx(32), subTextPaint);
        } else {
            canvas.drawText("HOLD 2s", cx, cy + dpToPx(32), subTextPaint);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                startHold();
                return true;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                cancelHold();
                return true;
        }
        return super.onTouchEvent(event);
    }

    private void startHold() {
        if (isTriggered) return;
        isHolding = true;
        currentProgress = 0f;
        vibrateFeedback(40);

        if (listener != null) {
            listener.onSosHoldStart();
        }

        if (holdAnimator != null && holdAnimator.isRunning()) {
            holdAnimator.cancel();
        }

        holdAnimator = ValueAnimator.ofFloat(0f, 1f);
        holdAnimator.setDuration(HOLD_DURATION_MS);
        holdAnimator.setInterpolator(new LinearInterpolator());
        holdAnimator.addUpdateListener(animation -> {
            currentProgress = (float) animation.getAnimatedValue();
            invalidate();

            if (listener != null) {
                listener.onSosHoldProgress(currentProgress);
            }

            if (currentProgress >= 0.5f && currentProgress < 0.53f) {
                vibrateFeedback(30);
            }

            if (currentProgress >= 1f) {
                triggerSos();
            }
        });
        holdAnimator.start();
        invalidate();
    }

    private void cancelHold() {
        if (isTriggered) return;
        isHolding = false;

        if (holdAnimator != null && holdAnimator.isRunning()) {
            holdAnimator.cancel();
        }

        currentProgress = 0f;
        invalidate();

        if (listener != null) {
            listener.onSosHoldCancelled();
        }
    }

    private void triggerSos() {
        isTriggered = true;
        isHolding = false;
        vibrateFeedback(600);

        if (listener != null) {
            listener.onSosTriggered();
        }

        postDelayed(() -> {
            isTriggered = false;
            currentProgress = 0f;
            invalidate();
        }, 3000);
    }

    private void vibrateFeedback(long durationMs) {
        if (vibrator != null) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(durationMs, VibrationEffect.DEFAULT_AMPLITUDE));
            } else {
                vibrator.vibrate(durationMs);
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

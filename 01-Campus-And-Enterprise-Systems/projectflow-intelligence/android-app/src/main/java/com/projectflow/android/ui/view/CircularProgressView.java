package com.projectflow.android.ui.view;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;

public class CircularProgressView extends View {

    private Paint trackPaint;
    private Paint progressPaint;
    private Paint textPaint;
    private Paint subtextPaint;
    private RectF rectF;
    private float strokeWidth = 24f;
    private float progress = 0f;
    private float animatedProgress = 0f;
    private ValueAnimator animator;

    public CircularProgressView(Context context) {
        super(context);
        init();
    }

    public CircularProgressView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public CircularProgressView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        strokeWidth = getResources().getDisplayMetrics().density * 10f;

        trackPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        trackPaint.setStyle(Paint.Style.STROKE);
        trackPaint.setStrokeWidth(strokeWidth);
        trackPaint.setStrokeCap(Paint.Cap.ROUND);
        trackPaint.setColor(ContextCompat.getColor(getContext(), R.color.earth_border));

        progressPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        progressPaint.setStyle(Paint.Style.STROKE);
        progressPaint.setStrokeWidth(strokeWidth);
        progressPaint.setStrokeCap(Paint.Cap.ROUND);
        progressPaint.setColor(ContextCompat.getColor(getContext(), R.color.primary_earth));

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setTextSize(getResources().getDisplayMetrics().density * 22f);
        textPaint.setFakeBoldText(true);
        textPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_main));

        subtextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        subtextPaint.setTextAlign(Paint.Align.CENTER);
        subtextPaint.setTextSize(getResources().getDisplayMetrics().density * 11f);
        subtextPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_secondary));

        rectF = new RectF();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        float pad = strokeWidth / 2f + getResources().getDisplayMetrics().density * 4f;
        rectF.set(pad, pad, w - pad, h - pad);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Draw track circle
        canvas.drawArc(rectF, 0f, 360f, false, trackPaint);

        // Draw progress arc (-90 degrees is top center)
        float sweepAngle = (animatedProgress / 100f) * 360f;
        canvas.drawArc(rectF, -90f, sweepAngle, false, progressPaint);

        // Draw center text
        float centerX = getWidth() / 2f;
        float centerY = getHeight() / 2f;
        String percentStr = Math.round(animatedProgress) + "%";
        canvas.drawText(percentStr, centerX, centerY + (textPaint.getTextSize() / 3f) - 6f, textPaint);
        canvas.drawText("Complete", centerX, centerY + (textPaint.getTextSize() / 3f) + 18f, subtextPaint);
    }

    public void setProgress(int targetProgress) {
        targetProgress = Math.max(0, Math.min(100, targetProgress));
        this.progress = targetProgress;

        if (animator != null && animator.isRunning()) {
            animator.cancel();
        }

        animator = ValueAnimator.ofFloat(animatedProgress, progress);
        animator.setDuration(700);
        animator.setInterpolator(new DecelerateInterpolator());
        animator.addUpdateListener(animation -> {
            animatedProgress = (float) animation.getAnimatedValue();
            invalidate();
        });
        animator.start();
    }

    public void setProgressColor(int color) {
        progressPaint.setColor(color);
        invalidate();
    }
}

package com.projectflow.android.ui.view;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;
import java.util.ArrayList;
import java.util.List;

public class NeumorphicPieChartView extends View {

    public static class Slice {
        public String label;
        public float value;
        public int color;

        public Slice(String label, float value, int color) {
            this.label = label;
            this.value = value;
            this.color = color;
        }
    }

    private final List<Slice> slices = new ArrayList<>();
    private Paint slicePaint;
    private Paint innerCirclePaint;
    private Paint innerShadowPaint;
    private Paint outerShadowPaint;
    private Paint textPrimaryPaint;
    private Paint textSecondaryPaint;
    private RectF chartBounds;
    private RectF outerShadowBounds;
    private float animationProgress = 0f;
    private ValueAnimator animator;
    private int totalCount = 0;
    private int completedPercent = 0;

    public NeumorphicPieChartView(Context context) {
        super(context);
        init();
    }

    public NeumorphicPieChartView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public NeumorphicPieChartView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        chartBounds = new RectF();
        outerShadowBounds = new RectF();

        slicePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        slicePaint.setStyle(Paint.Style.FILL);

        innerCirclePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        innerCirclePaint.setStyle(Paint.Style.FILL);
        innerCirclePaint.setColor(ContextCompat.getColor(getContext(), R.color.neu_surface));

        innerShadowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        innerShadowPaint.setStyle(Paint.Style.STROKE);
        innerShadowPaint.setStrokeWidth(getResources().getDisplayMetrics().density * 2f);
        innerShadowPaint.setColor(Color.parseColor("#15000000"));

        outerShadowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        outerShadowPaint.setStyle(Paint.Style.STROKE);
        outerShadowPaint.setStrokeWidth(getResources().getDisplayMetrics().density * 4f);
        outerShadowPaint.setColor(Color.parseColor("#18BFAFA0"));

        textPrimaryPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPrimaryPaint.setTextAlign(Paint.Align.CENTER);
        textPrimaryPaint.setTextSize(getResources().getDisplayMetrics().density * 24f);
        textPrimaryPaint.setFakeBoldText(true);
        textPrimaryPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_main));

        textSecondaryPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textSecondaryPaint.setTextAlign(Paint.Align.CENTER);
        textSecondaryPaint.setTextSize(getResources().getDisplayMetrics().density * 11f);
        textSecondaryPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_secondary));

        // Default initial distribution
        setTaskData(4, 2, 1, 1);
    }

    public void setTaskData(int done, int inProgress, int review, int todo) {
        slices.clear();
        int sum = done + inProgress + review + todo;
        if (sum == 0) sum = 1;
        this.totalCount = sum;
        this.completedPercent = Math.round((done * 100f) / sum);

        if (done > 0) {
            slices.add(new Slice("Done", done, ContextCompat.getColor(getContext(), R.color.chart_done)));
        }
        if (inProgress > 0) {
            slices.add(new Slice("In Progress", inProgress, ContextCompat.getColor(getContext(), R.color.chart_progress)));
        }
        if (review > 0) {
            slices.add(new Slice("Review", review, ContextCompat.getColor(getContext(), R.color.chart_review)));
        }
        if (todo > 0) {
            slices.add(new Slice("To Do", todo, ContextCompat.getColor(getContext(), R.color.chart_todo)));
        }

        if (slices.isEmpty()) {
            slices.add(new Slice("Planned", 1, ContextCompat.getColor(getContext(), R.color.chart_todo)));
        }

        animateChart();
    }

    private void animateChart() {
        if (animator != null && animator.isRunning()) {
            animator.cancel();
        }
        animator = ValueAnimator.ofFloat(0f, 1f);
        animator.setDuration(900);
        animator.setInterpolator(new DecelerateInterpolator());
        animator.addUpdateListener(animation -> {
            animationProgress = (float) animation.getAnimatedValue();
            invalidate();
        });
        animator.start();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        float pad = getResources().getDisplayMetrics().density * 12f;
        chartBounds.set(pad, pad, w - pad, h - pad);
        outerShadowBounds.set(pad - 2f, pad - 2f, w - pad + 2f, h - pad + 2f);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float width = getWidth();
        float height = getHeight();
        float centerX = width / 2f;
        float centerY = height / 2f;
        float radius = (Math.min(width, height) / 2f) - (getResources().getDisplayMetrics().density * 12f);

        if (radius <= 0) return;

        innerCirclePaint.setColor(ContextCompat.getColor(getContext(), R.color.neu_surface));
        textPrimaryPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_main));
        textSecondaryPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_secondary));

        // Draw soft 3D outer ambient ring
        canvas.drawCircle(centerX, centerY, radius + 2f, outerShadowPaint);

        // Draw debossed 3D background track
        slicePaint.setColor(ContextCompat.getColor(getContext(), R.color.neu_surface_pressed));
        canvas.drawCircle(centerX, centerY, radius, slicePaint);

        float totalVal = 0f;
        for (Slice s : slices) totalVal += s.value;

        float currentAngle = -90f;
        float totalSweep = 360f * animationProgress;

        for (Slice s : slices) {
            float sliceAngle = (s.value / totalVal) * totalSweep;
            if (sliceAngle <= 0.1f) continue;

            slicePaint.setColor(s.color);

            // Draw slice arc with slight gap (1.5 degrees) for 3D separation if multiple slices
            float gap = slices.size() > 1 ? 2f : 0f;
            canvas.drawArc(chartBounds, currentAngle + (gap / 2f), sliceAngle - gap, true, slicePaint);
            currentAngle += sliceAngle;
        }

        // Draw inner cutout circle (Donut hole: 62% radius)
        float innerRadius = radius * 0.62f;
        canvas.drawCircle(centerX, centerY, innerRadius, innerCirclePaint);
        canvas.drawCircle(centerX, centerY, innerRadius, innerShadowPaint);

        // Center Text: Completion % and Total Task Label
        String mainText = completedPercent + "%";
        canvas.drawText(mainText, centerX, centerY + (textPrimaryPaint.getTextSize() / 3f) - 6f, textPrimaryPaint);
        canvas.drawText(totalCount + " Total Tasks", centerX, centerY + (textPrimaryPaint.getTextSize() / 3f) + 16f, textSecondaryPaint);
    }
}

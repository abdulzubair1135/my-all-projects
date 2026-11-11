package com.projectflow.android.ui.view;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.*;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import com.projectflow.android.R;
import java.util.ArrayList;
import java.util.List;

public class NeumorphicBarChartView extends View {

    public static class BarItem {
        public String label;
        public int count;
        public int max;
        public int color;

        public BarItem(String label, int count, int max, int color) {
            this.label = label;
            this.count = count;
            this.max = max > 0 ? max : 1;
            this.color = color;
        }
    }

    private final List<BarItem> items = new ArrayList<>();
    private final Paint barTrackPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint barFillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textBadgePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint badgeBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint badgeStrokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final RectF badgeRect = new RectF();
    private final RectF trackRect = new RectF();
    private final RectF fillRect = new RectF();

    private float animationProgress = 0f;
    private ValueAnimator animator;

    public NeumorphicBarChartView(Context context) {
        super(context);
        init();
    }

    public NeumorphicBarChartView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public NeumorphicBarChartView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        barTrackPaint.setStyle(Paint.Style.FILL);
        barFillPaint.setStyle(Paint.Style.FILL);

        textLabelPaint.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD));
        textBadgePaint.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD));
        textBadgePaint.setTextAlign(Paint.Align.CENTER);

        badgeBgPaint.setStyle(Paint.Style.FILL);
        badgeStrokePaint.setStyle(Paint.Style.STROKE);

        setSampleData();
    }

    public void setSampleData() {
        items.clear();
        int max = 10;
        items.add(new BarItem("Core Architecture", 8, max, ContextCompat.getColor(getContext(), R.color.chart_done)));
        items.add(new BarItem("Admin Integration", 6, max, ContextCompat.getColor(getContext(), R.color.chart_progress)));
        items.add(new BarItem("Risk Radar Engine", 4, max, ContextCompat.getColor(getContext(), R.color.chart_review)));
        items.add(new BarItem("Team Collaboration", 7, max, ContextCompat.getColor(getContext(), R.color.chart_accent_cyan)));
        animateBars();
    }

    public void setData(List<BarItem> newItems) {
        items.clear();
        if (newItems != null) items.addAll(newItems);
        animateBars();
    }

    private void animateBars() {
        if (animator != null && animator.isRunning()) {
            animator.cancel();
        }
        animator = ValueAnimator.ofFloat(0f, 1f);
        animator.setDuration(850);
        animator.setInterpolator(new DecelerateInterpolator(1.5f));
        animator.addUpdateListener(a -> {
            animationProgress = (float) a.getAnimatedValue();
            invalidate();
        });
        animator.start();
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        float density = getResources().getDisplayMetrics().density;
        int rowHeight = (int) (density * 44f);
        int totalHeight = Math.max(120, items.size() * rowHeight + (int) (density * 12f));
        setMeasuredDimension(getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec), totalHeight);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (items.isEmpty()) return;

        float density = getResources().getDisplayMetrics().density;

        // Dynamic theme resolution
        barTrackPaint.setColor(ContextCompat.getColor(getContext(), R.color.neu_surface_pressed));
        textLabelPaint.setColor(ContextCompat.getColor(getContext(), R.color.text_main));
        textLabelPaint.setTextSize(density * 13f);
        textBadgePaint.setTextSize(density * 10.5f);
        badgeStrokePaint.setStrokeWidth(density * 1f);

        float startX = density * 4f;
        float endX = getWidth() - (density * 4f);
        float currentY = density * 18f;
        float barHeight = density * 10f;
        float radius = barHeight / 2f;

        for (BarItem item : items) {
            // 1. Draw Section Title Label
            canvas.drawText(item.label, startX, currentY - (density * 5f), textLabelPaint);

            // 2. Draw 3D Capsule Badge on Right (e.g. "8 TASKS")
            String badgeText = item.count + " TASKS";
            float textWidth = textBadgePaint.measureText(badgeText);
            float badgePaddingH = density * 8f;
            float badgePaddingV = density * 3f;
            float badgeW = textWidth + (badgePaddingH * 2f);
            float badgeH = density * 18f;
            float badgeLeft = endX - badgeW;
            float badgeTop = currentY - (density * 16f);
            badgeRect.set(badgeLeft, badgeTop, endX, badgeTop + badgeH);

            // Semi-transparent badge background
            badgeBgPaint.setColor(item.color);
            badgeBgPaint.setAlpha(36);
            canvas.drawRoundRect(badgeRect, density * 9f, density * 9f, badgeBgPaint);

            // Badge border
            badgeStrokePaint.setColor(item.color);
            badgeStrokePaint.setAlpha(120);
            canvas.drawRoundRect(badgeRect, density * 9f, density * 9f, badgeStrokePaint);

            // Badge Text
            textBadgePaint.setColor(item.color);
            Paint.FontMetrics fm = textBadgePaint.getFontMetrics();
            float textY = badgeRect.centerY() - (fm.ascent + fm.descent) / 2f;
            canvas.drawText(badgeText, badgeRect.centerX(), textY, textBadgePaint);

            // 3. Draw Track Groove
            trackRect.set(startX, currentY, endX, currentY + barHeight);
            canvas.drawRoundRect(trackRect, radius, radius, barTrackPaint);

            // 4. Draw Animated Bar Fill
            float fillWidth = (endX - startX) * ((float) item.count / item.max) * animationProgress;
            if (fillWidth > 0) {
                fillRect.set(startX, currentY, startX + Math.max(radius * 2f, fillWidth), currentY + barHeight);
                barFillPaint.setColor(item.color);
                canvas.drawRoundRect(fillRect, radius, radius, barFillPaint);
            }

            currentY += density * 42f;
        }
    }
}

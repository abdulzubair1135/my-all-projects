package com.example.myhelper;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.DecelerateInterpolator;

public class StorageDonutChartView extends View {

    private Paint paintArc;
    private Paint paintTextLarge;
    private Paint paintTextSmall;
    private RectF rectF;

    private float animationProgress = 0f;

    // Percentages (Sum <= 100)
    private float appsPct = 40f;
    private float mediaPct = 25f;
    private float systemPct = 15f;
    private float freePct = 20f;

    private String centerTextLarge = "80%";
    private String centerTextSmall = "Used";

    public StorageDonutChartView(Context context) {
        super(context);
        init();
    }

    public StorageDonutChartView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public StorageDonutChartView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        paintArc = new Paint(Paint.ANTI_ALIAS_FLAG);
        paintArc.setStyle(Paint.Style.STROKE);
        paintArc.setStrokeCap(Paint.Cap.ROUND);

        paintTextLarge = new Paint(Paint.ANTI_ALIAS_FLAG);
        paintTextLarge.setColor(Color.parseColor("#0F172A"));
        paintTextLarge.setTextAlign(Paint.Align.CENTER);
        paintTextLarge.setFakeBoldText(true);

        paintTextSmall = new Paint(Paint.ANTI_ALIAS_FLAG);
        paintTextSmall.setColor(Color.parseColor("#64748B"));
        paintTextSmall.setTextAlign(Paint.Align.CENTER);

        rectF = new RectF();
    }

    public void setStorageData(float apps, float media, float system, float free, String centerLarge, String centerSmall) {
        this.appsPct = apps;
        this.mediaPct = media;
        this.systemPct = system;
        this.freePct = free;
        this.centerTextLarge = centerLarge;
        this.centerTextSmall = centerSmall;

        startAnimation();
    }

    public void startAnimation() {
        ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);
        animator.setDuration(1000);
        animator.setInterpolator(new DecelerateInterpolator());
        animator.addUpdateListener(animation -> {
            animationProgress = (float) animation.getAnimatedValue();
            invalidate();
        });
        animator.start();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        int width = getWidth();
        int height = getHeight();
        if (width == 0 || height == 0) return;

        float size = Math.min(width, height);
        float strokeWidth = size * 0.13f;
        float padding = strokeWidth / 2f + 8f;

        rectF.set((width - size) / 2f + padding,
                  (height - size) / 2f + padding,
                  (width + size) / 2f - padding,
                  (height + size) / 2f - padding);

        paintArc.setStrokeWidth(strokeWidth);

        // 1. Draw Base/Free Arc (Background Circle)
        paintArc.setColor(Color.parseColor("#E2E8F0"));
        canvas.drawArc(rectF, 0f, 360f, false, paintArc);

        float startAngle = -90f;
        float totalDrawAngle = 360f * animationProgress;

        // 2. Apps Arc (Blue)
        float appsSweep = (appsPct / 100f) * 360f;
        if (appsSweep > 0) {
            paintArc.setColor(Color.parseColor("#0284C7"));
            float drawSweep = Math.min(appsSweep, Math.max(0, totalDrawAngle));
            canvas.drawArc(rectF, startAngle, drawSweep, false, paintArc);
            startAngle += appsSweep;
        }

        // 3. Media Arc (Emerald Green)
        float mediaSweep = (mediaPct / 100f) * 360f;
        float drawStartMedia = startAngle;
        if (mediaSweep > 0 && totalDrawAngle > (drawStartMedia + 90f)) {
            paintArc.setColor(Color.parseColor("#10B981"));
            float maxAllowed = totalDrawAngle - (drawStartMedia + 90f);
            float drawSweep = Math.min(mediaSweep, Math.max(0, maxAllowed));
            canvas.drawArc(rectF, drawStartMedia, drawSweep, false, paintArc);
            startAngle += mediaSweep;
        }

        // 4. System Arc (Amber)
        float systemSweep = (systemPct / 100f) * 360f;
        float drawStartSys = startAngle;
        if (systemSweep > 0 && totalDrawAngle > (drawStartSys + 90f)) {
            paintArc.setColor(Color.parseColor("#F59E0B"));
            float maxAllowed = totalDrawAngle - (drawStartSys + 90f);
            float drawSweep = Math.min(systemSweep, Math.max(0, maxAllowed));
            canvas.drawArc(rectF, drawStartSys, drawSweep, false, paintArc);
        }

        // Draw Center Text
        float cx = width / 2f;
        float cy = height / 2f;

        paintTextLarge.setTextSize(size * 0.20f);
        paintTextSmall.setTextSize(size * 0.09f);

        canvas.drawText(centerTextLarge, cx, cy, paintTextLarge);
        canvas.drawText(centerTextSmall, cx, cy + (size * 0.12f), paintTextSmall);
    }
}

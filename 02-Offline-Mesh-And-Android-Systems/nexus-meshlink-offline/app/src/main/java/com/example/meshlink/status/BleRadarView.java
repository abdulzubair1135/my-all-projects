package com.example.meshlink.status;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.SweepGradient;
import android.util.AttributeSet;
import android.view.View;
import android.view.animation.LinearInterpolator;

import android.graphics.PointF;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class BleRadarView extends View {

    private Paint ringPaint;
    private Paint sweepPaint;
    private Paint centerNodePaint;
    private Paint peerNodePaint;
    private Paint waveArcPaint;
    private Paint textPaint;
    private Paint distanceTextPaint;
    private Paint crosshairPaint;
    private Paint meshLinkPaint;
    private Paint pulseDotPaint;
    private Paint hopBadgePaint;
    private Paint hopBadgeTextPaint;

    private float sweepAngle = 0f;
    private float wavePulse = 0f;
    private ValueAnimator sweepAnimator;
    private ValueAnimator waveAnimator;
    private final List<PeerNode> nodes = new ArrayList<>();
    private final Map<String, Set<String>> topologyLinks = new HashMap<>();
    private String hostName = "YOU";

    public static class PeerNode {
        public String name;
        public float distanceRatio; // 0.2 to 0.8
        public float angleDegrees;
        public String transport; // BLE, WIFI_DIRECT, HOTSPOT
        public float estimatedMeters;
        public int signalPercent;
        public int hopCount = 1;
        public String viaNode = "";

        public PeerNode(String name, float distanceRatio, float angleDegrees, String transport) {
            this(name, distanceRatio, angleDegrees, transport, 1, "");
        }

        public PeerNode(String name, float distanceRatio, float angleDegrees, String transport, int hopCount, String viaNode) {
            this.name = name;
            this.distanceRatio = distanceRatio;
            this.angleDegrees = angleDegrees;
            this.transport = transport;
            this.hopCount = hopCount;
            this.viaNode = viaNode != null ? viaNode : "";
            this.estimatedMeters = Math.max(0.8f, hopCount * 4.5f + (distanceRatio * 5.0f));
            this.signalPercent = Math.max(15, 100 - (hopCount * 20) - (int) (distanceRatio * 20));
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
        ringPaint.setColor(Color.parseColor("#2516A34A"));
        ringPaint.setStyle(Paint.Style.STROKE);
        ringPaint.setStrokeWidth(dpToPx(1.5f));

        crosshairPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        crosshairPaint.setColor(Color.parseColor("#1516A34A"));
        crosshairPaint.setStyle(Paint.Style.STROKE);
        crosshairPaint.setStrokeWidth(dpToPx(1f));

        sweepPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        sweepPaint.setStyle(Paint.Style.FILL);

        centerNodePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        centerNodePaint.setColor(Color.parseColor("#16A34A"));
        centerNodePaint.setStyle(Paint.Style.FILL);

        peerNodePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        peerNodePaint.setColor(Color.parseColor("#22C55E"));
        peerNodePaint.setStyle(Paint.Style.FILL);

        waveArcPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        waveArcPaint.setStyle(Paint.Style.STROKE);
        waveArcPaint.setStrokeWidth(dpToPx(1.8f));

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.parseColor("#374151"));
        textPaint.setTextSize(spToPx(10));
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        distanceTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        distanceTextPaint.setColor(Color.parseColor("#16A34A"));
        distanceTextPaint.setTextSize(spToPx(9));
        distanceTextPaint.setTextAlign(Paint.Align.LEFT);

        meshLinkPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        meshLinkPaint.setColor(Color.parseColor("#4D10B981"));
        meshLinkPaint.setStyle(Paint.Style.STROKE);
        meshLinkPaint.setStrokeWidth(dpToPx(2.0f));

        pulseDotPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        pulseDotPaint.setColor(Color.parseColor("#34D399"));
        pulseDotPaint.setStyle(Paint.Style.FILL);

        hopBadgePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        hopBadgePaint.setStyle(Paint.Style.FILL);

        hopBadgeTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        hopBadgeTextPaint.setColor(Color.WHITE);
        hopBadgeTextPaint.setTextSize(spToPx(7.5f));
        hopBadgeTextPaint.setTextAlign(Paint.Align.CENTER);
        hopBadgeTextPaint.setFakeBoldText(true);

        startAnimations();
    }

    public void setMeshTopology(String myDisplayName, Map<String, com.example.meshlink.mesh.MeshCoordinator.RouteInfo> routes, Map<String, Set<String>> topology) {
        this.hostName = (myDisplayName != null && !myDisplayName.isEmpty()) ? myDisplayName : "YOU";
        this.topologyLinks.clear();
        if (topology != null) {
            this.topologyLinks.putAll(topology);
        }

        nodes.clear();
        if (routes != null && !routes.isEmpty()) {
            List<String> peerNames = new ArrayList<>(routes.keySet());
            float angleStep = 360f / Math.max(1, peerNames.size());
            for (int i = 0; i < peerNames.size(); i++) {
                String peer = peerNames.get(i);
                com.example.meshlink.mesh.MeshCoordinator.RouteInfo route = routes.get(peer);
                int hops = (route != null) ? route.hopCount : 1;
                String via = (route != null && route.path.size() > 2) ? route.path.get(1) : "";

                // Ring distance based on hops
                float distRatio;
                if (hops <= 1) {
                    distRatio = 0.48f + (float) ((i % 2) * 0.10f);
                } else if (hops == 2) {
                    distRatio = 0.70f + (float) ((i % 2) * 0.08f);
                } else {
                    distRatio = 0.88f;
                }

                float angle = i * angleStep + 30f;
                String transport = (hops <= 1) ? "WIFI_DIRECT" : "MESH_RELAY";
                nodes.add(new PeerNode(peer, distRatio, angle, transport, hops, via));
            }
        }
        invalidate();
    }

    public void setPeers(List<String> peerNames) {
        nodes.clear();
        if (peerNames != null && !peerNames.isEmpty()) {
            float angleStep = 360f / peerNames.size();
            for (int i = 0; i < peerNames.size(); i++) {
                float dist = 0.30f + (float) ((i % 3) * 0.22f);
                float angle = i * angleStep + 30f;
                nodes.add(new PeerNode(peerNames.get(i), dist, angle, i % 2 == 0 ? "WIFI_DIRECT" : "BLE"));
            }
        }
        invalidate();
    }

    public void addPeer(String name, float distRatio, float angleDeg, String transport) {
        nodes.add(new PeerNode(name, distRatio, angleDeg, transport));
        invalidate();
    }

    private void startAnimations() {
        if (sweepAnimator == null) {
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

        if (waveAnimator == null) {
            waveAnimator = ValueAnimator.ofFloat(0f, 1f);
            waveAnimator.setDuration(1600);
            waveAnimator.setRepeatCount(ValueAnimator.INFINITE);
            waveAnimator.setInterpolator(new LinearInterpolator());
            waveAnimator.addUpdateListener(animation -> wavePulse = (float) animation.getAnimatedValue());
            waveAnimator.start();
        }
    }

    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        if (sweepAnimator != null) sweepAnimator.cancel();
        if (waveAnimator != null) waveAnimator.cancel();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        float cx = getWidth() / 2f;
        float cy = getHeight() / 2f;
        float maxRadius = Math.min(cx, cy) - dpToPx(24);

        // 1. Concentric Range Rings with distance labels (RuVNet style distance estimation)
        canvas.drawCircle(cx, cy, maxRadius * 0.30f, ringPaint);
        canvas.drawText("2m", cx + maxRadius * 0.30f + 6, cy - 4, distanceTextPaint);

        canvas.drawCircle(cx, cy, maxRadius * 0.60f, ringPaint);
        canvas.drawText("5m", cx + maxRadius * 0.60f + 6, cy - 4, distanceTextPaint);

        canvas.drawCircle(cx, cy, maxRadius * 0.90f, ringPaint);
        canvas.drawText("10m", cx + maxRadius * 0.90f + 6, cy - 4, distanceTextPaint);

        // 2. Crosshairs
        canvas.drawLine(cx - maxRadius, cy, cx + maxRadius, cy, crosshairPaint);
        canvas.drawLine(cx, cy - maxRadius, cx, cy + maxRadius, crosshairPaint);

        // 3. Radar Sweep Beam (360 Sweep)
        int[] colors = new int[]{Color.TRANSPARENT, Color.parseColor("#0516A34A"), Color.parseColor("#4D16A34A")};
        float[] positions = new float[]{0.0f, 0.75f, 1.0f};
        SweepGradient gradient = new SweepGradient(cx, cy, colors, positions);
        sweepPaint.setShader(gradient);

        canvas.save();
        canvas.rotate(sweepAngle, cx, cy);
        canvas.drawCircle(cx, cy, maxRadius, sweepPaint);
        canvas.restore();

        // 4. Precalculate Node Positions for Interconnection Lines
        Map<String, PointF> nodeCoords = new HashMap<>();
        String myClean = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(hostName).toLowerCase();
        nodeCoords.put("you", new PointF(cx, cy));
        nodeCoords.put("host", new PointF(cx, cy));
        nodeCoords.put(myClean, new PointF(cx, cy));

        Map<PeerNode, PointF> peerPositions = new HashMap<>();
        for (PeerNode node : nodes) {
            float rad = (float) Math.toRadians(node.angleDegrees);
            float dist = maxRadius * node.distanceRatio;
            float nx = cx + (float) Math.cos(rad) * dist;
            float ny = cy + (float) Math.sin(rad) * dist;
            PointF pt = new PointF(nx, ny);
            peerPositions.put(node, pt);
            nodeCoords.put(com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(node.name).toLowerCase(), pt);
            nodeCoords.put(node.name.toLowerCase(), pt);
        }

        // Draw Interconnecting Mesh Lines (Multi-Hop Topology Connections)
        java.util.HashSet<String> drawnLinks = new java.util.HashSet<>();
        for (PeerNode node : nodes) {
            PointF p = peerPositions.get(node);
            if (p == null) continue;

            if (node.hopCount <= 1 || node.viaNode == null || node.viaNode.isEmpty()) {
                drawMeshConnection(canvas, cx, cy, p.x, p.y, true);
                drawnLinks.add(myClean + "->" + com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(node.name).toLowerCase());
            } else {
                String viaClean = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(node.viaNode).toLowerCase();
                PointF viaPt = nodeCoords.get(viaClean);
                if (viaPt != null) {
                    drawMeshConnection(canvas, viaPt.x, viaPt.y, p.x, p.y, false);
                    drawnLinks.add(viaClean + "->" + com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(node.name).toLowerCase());
                } else {
                    drawMeshConnection(canvas, cx, cy, p.x, p.y, false);
                }
            }
        }

        for (Map.Entry<String, Set<String>> entry : topologyLinks.entrySet()) {
            String fromKey = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(entry.getKey()).toLowerCase();
            PointF fromPt = nodeCoords.get(fromKey);
            if (fromPt == null) continue;

            for (String neighbor : entry.getValue()) {
                String toKey = com.example.meshlink.mesh.MeshCoordinator.cleanPeerName(neighbor).toLowerCase();
                PointF toPt = nodeCoords.get(toKey);
                if (toPt == null) continue;

                String key1 = fromKey + "->" + toKey;
                String key2 = toKey + "->" + fromKey;
                if (!drawnLinks.contains(key1) && !drawnLinks.contains(key2)) {
                    drawnLinks.add(key1);
                    drawMeshConnection(canvas, fromPt.x, fromPt.y, toPt.x, toPt.y, false);
                }
            }
        }

        // 5. Center Node (THIS PHONE)
        centerNodePaint.setColor(Color.parseColor("#16A34A"));
        canvas.drawCircle(cx, cy, dpToPx(8), centerNodePaint);
        centerNodePaint.setColor(Color.parseColor("#BBF7D0"));
        canvas.drawCircle(cx, cy, dpToPx(4), centerNodePaint);
        String centerLabel = (hostName != null && !hostName.equals("YOU")) ? hostName + " (Host)" : "YOU (Host)";
        canvas.drawText(centerLabel, cx, cy - dpToPx(13), textPaint);

        // 6. Active Peer Nodes with RuVNet Wi-Fi Wave Sensing Arcs & Hop Badges
        if (nodes.isEmpty()) {
            Paint emptyTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
            emptyTextPaint.setColor(Color.parseColor("#64748B"));
            emptyTextPaint.setTextSize(spToPx(11));
            emptyTextPaint.setTextAlign(Paint.Align.CENTER);
            canvas.drawText("📡 RuVNet Mesh Sensing: Scanning & routing...", cx, cy + maxRadius * 0.85f, emptyTextPaint);
        } else {
            for (PeerNode node : nodes) {
                PointF p = peerPositions.get(node);
                if (p == null) continue;
                float nx = p.x;
                float ny = p.y;

                // Wi-Fi Radio Wave Propagation arcs (RuVNet concept)
                float baseArcR = dpToPx(12) + (wavePulse * dpToPx(16));
                int alpha = (int) ((1f - wavePulse) * 180);
                waveArcPaint.setColor(Color.argb(alpha, 22, 163, 74));
                RectF arcBox = new RectF(nx - baseArcR, ny - baseArcR, nx + baseArcR, ny + baseArcR);
                canvas.drawArc(arcBox, node.angleDegrees - 45, 90, false, waveArcPaint);

                // Node avatar or color dot
                android.graphics.Bitmap peerBmp = com.example.meshlink.mesh.MeshCoordinator.getInstance(getContext()).getPeerAvatarBitmap(node.name);
                if (peerBmp != null) {
                    android.graphics.Bitmap circBmp = com.example.meshlink.data.ImageUtils.getCircularBitmap(peerBmp);
                    float r = dpToPx(12);
                    RectF dst = new RectF(nx - r, ny - r, nx + r, ny + r);
                    canvas.drawBitmap(circBmp, null, dst, null);
                } else {
                    int color = (node.hopCount <= 1) ? Color.parseColor("#00C896") : Color.parseColor("#0A84FF");
                    peerNodePaint.setColor(color);
                    canvas.drawCircle(nx, ny, dpToPx(8), peerNodePaint);
                    peerNodePaint.setColor(Color.WHITE);
                    canvas.drawCircle(nx, ny, dpToPx(3), peerNodePaint);
                }

                String label = node.name;
                if (label.length() > 8) label = label.substring(0, 8) + "..";
                canvas.drawText(label, nx, ny + dpToPx(16), textPaint);

                // Hop Badge Pill
                String badgeText;
                int badgeBg;
                if (node.hopCount <= 1) {
                    badgeText = "DIRECT (1 HOP)";
                    badgeBg = Color.parseColor("#16A34A");
                } else if (node.hopCount == 2) {
                    badgeText = "MESH (2 HOPS)";
                    badgeBg = Color.parseColor("#0284C7");
                } else {
                    badgeText = node.hopCount + " HOPS • RELAY";
                    badgeBg = Color.parseColor("#7C3AED");
                }

                float badgeW = hopBadgeTextPaint.measureText(badgeText) + dpToPx(8);
                float badgeH = dpToPx(13);
                float badgeTop = ny + dpToPx(20);
                RectF badgeRect = new RectF(nx - badgeW / 2f, badgeTop, nx + badgeW / 2f, badgeTop + badgeH);
                hopBadgePaint.setColor(badgeBg);
                canvas.drawRoundRect(badgeRect, dpToPx(4), dpToPx(4), hopBadgePaint);
                canvas.drawText(badgeText, nx, badgeTop + dpToPx(9.5f), hopBadgeTextPaint);

                // Distance & Signal tag below badge
                Paint subText = new Paint(Paint.ANTI_ALIAS_FLAG);
                subText.setColor(Color.parseColor("#15803D"));
                subText.setTextSize(spToPx(8.5f));
                subText.setTextAlign(Paint.Align.CENTER);
                canvas.drawText(String.format("%.1fm • %d%%", node.estimatedMeters, node.signalPercent), nx, badgeTop + badgeH + dpToPx(11), subText);
            }
        }
    }

    private void drawMeshConnection(Canvas canvas, float x1, float y1, float x2, float y2, boolean isDirect) {
        if (meshLinkPaint == null || pulseDotPaint == null) return;
        meshLinkPaint.setColor(isDirect ? Color.parseColor("#4D10B981") : Color.parseColor("#590284C7"));
        canvas.drawLine(x1, y1, x2, y2, meshLinkPaint);

        // Traveling pulse dot
        float pulseX = x1 + (x2 - x1) * wavePulse;
        float pulseY = y1 + (y2 - y1) * wavePulse;
        pulseDotPaint.setColor(isDirect ? Color.parseColor("#10B981") : Color.parseColor("#38BDF8"));
        canvas.drawCircle(pulseX, pulseY, dpToPx(2.5f), pulseDotPaint);
    }

    private float dpToPx(float dp) {
        return dp * getResources().getDisplayMetrics().density;
    }

    private float spToPx(float sp) {
        return sp * getResources().getDisplayMetrics().scaledDensity;
    }
}

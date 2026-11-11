package com.projectflow.android.ui.fragment;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import com.projectflow.android.R;
import com.projectflow.android.data.remote.model.DtoModels.NotificationDto;
import com.projectflow.android.data.repository.ProjectFlowRepository;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class NotificationsFragment extends Fragment {

    private TextView chipAllNotifs, chipUnreadNotifs, btnMarkAllRead;
    private RecyclerView rvNotifications;
    private LinearLayout llEmptyNotifs;
    private SwipeRefreshLayout swipeRefreshNotifs;
    private ProjectFlowRepository repository;

    private NotificationsAdapter adapter;
    private final List<NotificationDto> allList = new ArrayList<>();
    private boolean showOnlyUnread = false;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_notifications, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        repository = new ProjectFlowRepository(requireContext());

        chipAllNotifs = view.findViewById(R.id.chipAllNotifs);
        chipUnreadNotifs = view.findViewById(R.id.chipUnreadNotifs);
        btnMarkAllRead = view.findViewById(R.id.btnMarkAllRead);
        rvNotifications = view.findViewById(R.id.rvNotifications);
        llEmptyNotifs = view.findViewById(R.id.llEmptyNotifs);
        swipeRefreshNotifs = view.findViewById(R.id.swipeRefreshNotifs);

        adapter = new NotificationsAdapter(notif -> {
            if (!notif.read) {
                notif.read = true;
                adapter.notifyDataSetChanged();
                repository.markNotificationRead(notif.id, null);
            }
            if (notif.message != null && notif.message.contains("<!--PF:")) {
                java.util.regex.Matcher m = java.util.regex.Pattern.compile("<!--PF:(.*?)-->").matcher(notif.message);
                if (m.find()) {
                    String inside = m.group(1);
                    String[] parts = inside.split(":");
                    for (String part : parts) {
                        int eq = part.indexOf('=');
                        if (eq > 0) {
                            String k = part.substring(0, eq).trim();
                            String v = part.substring(eq + 1).trim();
                            if ("ch".equalsIgnoreCase(k) && (notif.channel == null || notif.channel.isEmpty())) notif.channel = v;
                            if ("task".equalsIgnoreCase(k) && (notif.taskId == null || notif.taskId.isEmpty())) notif.taskId = v;
                            if ("sender".equalsIgnoreCase(k) && (notif.senderName == null || notif.senderName.isEmpty())) notif.senderName = v;
                            if ("senderEmail".equalsIgnoreCase(k) && (notif.senderEmail == null || notif.senderEmail.isEmpty())) notif.senderEmail = v;
                            if ("targetEmail".equalsIgnoreCase(k)) notif.targetEmail = v;
                            if ("proj".equalsIgnoreCase(k)) notif.projectId = v;
                        }
                    }
                }
            }
            boolean isChat = (notif.channel != null && !notif.channel.isEmpty())
                    || "CHAT_MESSAGE".equalsIgnoreCase(notif.type)
                    || (notif.title != null && notif.title.contains("💬"));
            if (isChat) {
                String ch = (notif.channel != null && !notif.channel.isEmpty()) ? notif.channel : "";
                if (ch.isEmpty()) {
                    String userEmail = requireContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE)
                            .getString("user_email", "admin@projectflow.io");
                    String c1 = userEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase();
                    String c2 = "admin_projectflow_io";
                    ch = (c1.compareTo(c2) < 0) ? "dm_" + c1 + "_" + c2 : "dm_" + c2 + "_" + c1;
                }
                String sender = (notif.senderName != null && !notif.senderName.isEmpty()) ? notif.senderName : "System Administrator";
                String type = ch.startsWith("dm_") ? "DIRECT" : "GROUP";
                if (getActivity() instanceof com.projectflow.android.ui.MainActivity) {
                    ((com.projectflow.android.ui.MainActivity) getActivity()).navigateToFragment(
                            ChatFragment.newInstance(ch, sender, type),
                            "Chat: " + sender
                    );
                }
            } else if ((notif.taskId != null && !notif.taskId.isEmpty()) || (notif.type != null && notif.type.toUpperCase().contains("TASK"))) {
                if (notif.taskId != null && !notif.taskId.isEmpty()) {
                    android.content.Intent intent = new android.content.Intent(requireContext(), com.projectflow.android.ui.TaskDetailsActivity.class);
                    intent.putExtra("task_id", notif.taskId);
                    intent.putExtra("task_title", notif.title);
                    intent.putExtra("task_desc", notif.message != null ? notif.message.replaceAll("<!--PF:[^>]*-->", "").trim() : "");
                    startActivity(intent);
                } else if (getActivity() instanceof com.projectflow.android.ui.MainActivity) {
                    ((com.projectflow.android.ui.MainActivity) getActivity()).navigateToFragment(
                            new TasksFragment(),
                            "Tasks"
                    );
                }
            } else if (notif.type != null && notif.type.toUpperCase().contains("PROJECT")) {
                if (getActivity() instanceof com.projectflow.android.ui.MainActivity) {
                    ((com.projectflow.android.ui.MainActivity) getActivity()).navigateToFragment(
                            new ProjectsFragment(),
                            "Projects"
                    );
                }
            }
        });

        rvNotifications.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvNotifications.setAdapter(adapter);

        chipAllNotifs.setOnClickListener(v -> {
            showOnlyUnread = false;
            chipAllNotifs.setBackgroundResource(R.drawable.bg_chip_selected);
            chipAllNotifs.setTextColor(ContextCompat.getColor(requireContext(), R.color.white));
            chipUnreadNotifs.setBackgroundResource(R.drawable.bg_chip_unselected);
            chipUnreadNotifs.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_main));
            filterList();
        });

        chipUnreadNotifs.setOnClickListener(v -> {
            showOnlyUnread = true;
            chipUnreadNotifs.setBackgroundResource(R.drawable.bg_chip_selected);
            chipUnreadNotifs.setTextColor(ContextCompat.getColor(requireContext(), R.color.white));
            chipAllNotifs.setBackgroundResource(R.drawable.bg_chip_unselected);
            chipAllNotifs.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_main));
            filterList();
        });

        btnMarkAllRead.setOnClickListener(v -> {
            for (NotificationDto n : allList) n.read = true;
            adapter.notifyDataSetChanged();
            repository.markAllNotificationsRead(null);
        });

        swipeRefreshNotifs.setColorSchemeResources(R.color.primary_earth, R.color.muted_clay);
        swipeRefreshNotifs.setOnRefreshListener(this::loadNotifications);

        loadNotifications();
    }

    private void loadNotifications() {
        repository.fetchNotifications(new ProjectFlowRepository.DataCallback<List<NotificationDto>>() {
            @Override
            public void onData(List<NotificationDto> data) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        swipeRefreshNotifs.setRefreshing(false);
                        allList.clear();
                        if (data != null && isAdded()) {
                            String myEmail = requireContext().getSharedPreferences("projectflow_prefs", android.content.Context.MODE_PRIVATE)
                                    .getString("user_email", "").trim().toLowerCase();
                            String mySlug = !myEmail.isEmpty() ? myEmail.replaceAll("[^a-zA-Z0-9]", "_").toLowerCase() : "";

                            for (NotificationDto n : data) {
                                if (n.message != null && n.message.contains("<!--PF:")) {
                                    java.util.regex.Matcher m = java.util.regex.Pattern.compile("<!--PF:(.*?)-->").matcher(n.message);
                                    if (m.find()) {
                                        String[] tokens = m.group(1).split(":");
                                        for (String tok : tokens) {
                                            int eq = tok.indexOf('=');
                                            if (eq > 0) {
                                                String k = tok.substring(0, eq);
                                                String v = tok.substring(eq + 1);
                                                if ("ch".equals(k) && (n.channel == null || n.channel.isEmpty())) n.channel = v;
                                                if ("task".equals(k) && (n.taskId == null || n.taskId.isEmpty())) n.taskId = v;
                                                if ("sender".equals(k) && (n.senderName == null || n.senderName.isEmpty())) n.senderName = v;
                                                if ("senderEmail".equals(k) && (n.senderEmail == null || n.senderEmail.isEmpty())) n.senderEmail = v;
                                                if ("targetEmail".equals(k)) n.targetEmail = v;
                                            }
                                        }
                                    }
                                    n.message = n.message.replaceAll("<!--PF:[^>]*-->", "").trim();
                                }

                                // Skip DMs between two other people
                                if (n.channel != null && n.channel.startsWith("dm_") && !mySlug.isEmpty()) {
                                    if (!n.channel.contains(mySlug)) continue;
                                }

                                // Skip notifications triggered by this user
                                if (n.senderEmail != null && !n.senderEmail.isEmpty() && n.senderEmail.equalsIgnoreCase(myEmail)) {
                                    continue;
                                }

                                // Skip tasks targeted to someone else
                                if (n.targetEmail != null && !n.targetEmail.isEmpty() && !n.targetEmail.equalsIgnoreCase(myEmail)) {
                                    continue;
                                }

                                allList.add(n);
                            }
                        }
                        filterList();
                    });
                }
            }

            @Override
            public void onError(String message) {
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> swipeRefreshNotifs.setRefreshing(false));
                }
            }
        });
    }

    private void filterList() {
        List<NotificationDto> filtered = new ArrayList<>();
        for (NotificationDto n : allList) {
            if (!showOnlyUnread || !n.read) {
                filtered.add(n);
            }
        }
        adapter.setList(filtered);

        if (filtered.isEmpty()) {
            rvNotifications.setVisibility(View.GONE);
            llEmptyNotifs.setVisibility(View.VISIBLE);
        } else {
            llEmptyNotifs.setVisibility(View.GONE);
            rvNotifications.setVisibility(View.VISIBLE);
        }
    }

    private static class NotificationsAdapter extends RecyclerView.Adapter<NotificationsAdapter.ViewHolder> {
        private final List<NotificationDto> list = new ArrayList<>();
        private final OnNotifClickListener listener;

        interface OnNotifClickListener { void onClick(NotificationDto notif); }

        NotificationsAdapter(OnNotifClickListener listener) { this.listener = listener; }

        void setList(List<NotificationDto> items) {
            list.clear();
            if (items != null) list.addAll(items);
            notifyDataSetChanged();
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_notification, parent, false);
            return new ViewHolder(v);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            NotificationDto item = list.get(position);
            holder.tvTitle.setText(item.title);
            String cleanMsg = item.message != null ? item.message.replaceAll("<!--PF:[^>]*-->", "").trim() : "";
            holder.tvSubtitle.setText(cleanMsg);
            holder.tvTime.setText(formatRelativeTime(item.createdAt));
            holder.unreadDot.setVisibility(item.read ? View.GONE : View.VISIBLE);

            holder.itemView.setOnClickListener(v -> listener.onClick(item));
        }

        @Override
        public int getItemCount() { return list.size(); }

        private String formatRelativeTime(String isoTime) {
            if (isoTime == null) return "Recently";
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                Date d = sdf.parse(isoTime.split("\\.")[0]);
                if (d == null) return "Recently";
                long diffMs = System.currentTimeMillis() - d.getTime();
                long mins = diffMs / 60000;
                if (mins < 1) return "Just now";
                if (mins < 60) return mins + "m ago";
                long hours = mins / 60;
                if (hours < 24) return hours + "h ago";
                long days = hours / 24;
                return days + "d ago";
            } catch (Exception e) {
                return "Today";
            }
        }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvTitle, tvSubtitle, tvTime;
            View unreadDot;
            ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvTitle = itemView.findViewById(R.id.tvNotifTitle);
                tvSubtitle = itemView.findViewById(R.id.tvNotifSubtitle);
                tvTime = itemView.findViewById(R.id.tvNotifTime);
                unreadDot = itemView.findViewById(R.id.unreadDot);
            }
        }
    }
}

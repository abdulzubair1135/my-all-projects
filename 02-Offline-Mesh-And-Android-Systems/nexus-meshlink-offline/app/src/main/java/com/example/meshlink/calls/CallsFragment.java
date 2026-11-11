package com.example.meshlink.calls;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.meshlink.R;
import com.example.meshlink.data.CallModel;
import com.example.meshlink.data.MeshDatabase;

import java.util.ArrayList;
import java.util.List;

public class CallsFragment extends Fragment {

    private RecyclerView rvCallsList;
    private View llCallsEmptyState;
    private CallsAdapter adapter;
    private final List<CallModel> callList = new ArrayList<>();
    private MeshDatabase db;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_calls, container, false);

        rvCallsList = v.findViewById(R.id.rvCallsList);
        llCallsEmptyState = v.findViewById(R.id.llCallsEmptyState);
        rvCallsList.setLayoutManager(new LinearLayoutManager(getContext()));

        db = new MeshDatabase(requireContext());
        adapter = new CallsAdapter(requireContext(), callList);
        rvCallsList.setAdapter(adapter);

        View btnVoice = v.findViewById(R.id.btnQuickVoiceCall);
        if (btnVoice != null) {
            btnVoice.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VoiceCallActivity.class);
                intent.putExtra("PEER_NAME", "Broadcast Mesh");
                intent.putExtra("PEER_ID", "ALL");
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });
        }

        View btnVideo = v.findViewById(R.id.btnQuickVideoCall);
        if (btnVideo != null) {
            btnVideo.setOnClickListener(view -> {
                android.content.Intent intent = new android.content.Intent(getContext(), VideoCallActivity.class);
                intent.putExtra("PEER_NAME", "Broadcast Mesh");
                intent.putExtra("PEER_ID", "ALL");
                intent.putExtra("IS_INCOMING", false);
                intent.putExtra("CALL_STATE", "CALLING");
                startActivity(intent);
            });
        }

        loadCalls();
        return v;
    }

    @Override
    public void onResume() {
        super.onResume();
        loadCalls();
    }

    private void loadCalls() {
        if (db == null) return;
        callList.clear();
        callList.addAll(db.getAllCalls());
        adapter.notifyDataSetChanged();

        if (llCallsEmptyState != null) {
            llCallsEmptyState.setVisibility(callList.isEmpty() ? View.VISIBLE : View.GONE);
        }
    }
}

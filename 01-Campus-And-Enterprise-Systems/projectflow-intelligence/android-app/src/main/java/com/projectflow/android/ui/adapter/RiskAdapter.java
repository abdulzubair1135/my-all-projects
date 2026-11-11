package com.projectflow.android.ui.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.projectflow.android.R;
import com.projectflow.android.data.local.RiskEntity;

import java.util.ArrayList;
import java.util.List;

public class RiskAdapter extends RecyclerView.Adapter<RiskAdapter.RiskViewHolder> {

    private List<RiskEntity> risks = new ArrayList<>();

    public void setRisks(List<RiskEntity> list) {
        this.risks = list != null ? list : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public RiskViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_risk, parent, false);
        return new RiskViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull RiskViewHolder holder, int position) {
        RiskEntity r = risks.get(position);
        holder.tvSeverity.setText(r.severity != null ? r.severity : "CRITICAL");
        holder.tvRuleId.setText(r.ruleId != null ? r.ruleId : "OVERDUE_TASK");
        holder.tvTitle.setText(r.title);
        holder.tvDesc.setText(r.description);
        holder.tvAction.setText("Action: " + (r.recommendedAction != null ? r.recommendedAction : "Review schedule"));
    }

    @Override
    public int getItemCount() {
        return risks.size();
    }

    static class RiskViewHolder extends RecyclerView.ViewHolder {
        TextView tvSeverity, tvRuleId, tvTitle, tvDesc, tvAction;

        RiskViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSeverity = itemView.findViewById(R.id.tvRiskSeverity);
            tvRuleId = itemView.findViewById(R.id.tvRiskRuleId);
            tvTitle = itemView.findViewById(R.id.tvRiskTitle);
            tvDesc = itemView.findViewById(R.id.tvRiskDesc);
            tvAction = itemView.findViewById(R.id.tvRiskAction);
        }
    }
}

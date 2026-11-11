package com.cyclecare.store;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.RadioButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.models.UserAddress;
import com.google.android.material.card.MaterialCardView;

import java.util.ArrayList;
import java.util.List;

public class AddressAdapter extends RecyclerView.Adapter<AddressAdapter.AddressViewHolder> {

    public interface OnAddressSelectedListener {
        void onAddressSelected(UserAddress address);
    }

    private final Context context;
    private final List<UserAddress> addresses = new ArrayList<>();
    private final OnAddressSelectedListener listener;
    private int selectedPosition = 0;

    public AddressAdapter(Context context, OnAddressSelectedListener listener) {
        this.context = context;
        this.listener = listener;
    }

    public void setAddresses(List<UserAddress> newAddresses) {
        this.addresses.clear();
        if (newAddresses != null) {
            this.addresses.addAll(newAddresses);
            for (int i = 0; i < addresses.size(); i++) {
                if (addresses.get(i).isDefault()) {
                    selectedPosition = i;
                    break;
                }
            }
        }
        notifyDataSetChanged();
    }

    public UserAddress getSelectedAddress() {
        if (selectedPosition >= 0 && selectedPosition < addresses.size()) {
            return addresses.get(selectedPosition);
        }
        return null;
    }

    @NonNull
    @Override
    public AddressViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_address, parent, false);
        return new AddressViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull AddressViewHolder holder, int position) {
        UserAddress address = addresses.get(position);

        holder.tvTypeTag.setText(address.getType());
        holder.tvDefaultBadge.setVisibility(address.isDefault() ? View.VISIBLE : View.GONE);
        holder.tvRecipient.setText(address.getName());
        holder.tvFullAddress.setText(address.getFormattedAddress());
        holder.tvPhone.setText("Phone: " + (address.getPhone() != null ? address.getPhone() : ""));

        boolean isSelected = (position == selectedPosition);
        holder.rbSelect.setChecked(isSelected);
        holder.cardContainer.setStrokeColor(isSelected ? 0xFFD81B60 : 0x15000000);
        holder.cardContainer.setStrokeWidth(isSelected ? 4 : 1);

        View.OnClickListener clickListener = v -> {
            int previousPos = selectedPosition;
            selectedPosition = holder.getAdapterPosition();
            notifyItemChanged(previousPos);
            notifyItemChanged(selectedPosition);
            if (listener != null) {
                listener.onAddressSelected(address);
            }
        };

        holder.cardContainer.setOnClickListener(clickListener);
        holder.rbSelect.setOnClickListener(clickListener);
    }

    @Override
    public int getItemCount() {
        return addresses.size();
    }

    static class AddressViewHolder extends RecyclerView.ViewHolder {
        MaterialCardView cardContainer;
        TextView tvTypeTag, tvDefaultBadge, tvRecipient, tvFullAddress, tvPhone;
        RadioButton rbSelect;

        public AddressViewHolder(@NonNull View itemView) {
            super(itemView);
            cardContainer = itemView.findViewById(R.id.card_address_container);
            tvTypeTag = itemView.findViewById(R.id.tv_address_type_tag);
            tvDefaultBadge = itemView.findViewById(R.id.tv_default_badge);
            tvRecipient = itemView.findViewById(R.id.tv_address_recipient);
            tvFullAddress = itemView.findViewById(R.id.tv_address_full);
            tvPhone = itemView.findViewById(R.id.tv_address_phone);
            rbSelect = itemView.findViewById(R.id.rb_select_address);
        }
    }
}

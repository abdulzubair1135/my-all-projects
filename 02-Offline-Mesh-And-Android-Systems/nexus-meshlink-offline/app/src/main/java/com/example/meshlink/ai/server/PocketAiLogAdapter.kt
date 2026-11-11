package com.example.meshlink.ai.server

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.meshlink.R
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class PocketAiLogAdapter(
    private val logs: MutableList<PocketAiServerController.RequestLogEntry>
) : RecyclerView.Adapter<PocketAiLogAdapter.LogViewHolder>() {

    private val timeFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    class LogViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvLogTime: TextView = itemView.findViewById(R.id.tvLogTime)
        val tvLogStatus: TextView = itemView.findViewById(R.id.tvLogStatus)
        val tvLogClient: TextView = itemView.findViewById(R.id.tvLogClient)
        val tvLogEndpoint: TextView = itemView.findViewById(R.id.tvLogEndpoint)
        val tvLogPrompt: TextView = itemView.findViewById(R.id.tvLogPrompt)
        val tvLogDuration: TextView = itemView.findViewById(R.id.tvLogDuration)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LogViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_pocket_ai_log, parent, false)
        return LogViewHolder(view)
    }

    override fun onBindViewHolder(holder: LogViewHolder, position: Int) {
        val item = logs[position]
        holder.tvLogTime.text = timeFormat.format(Date(item.timestamp))
        holder.tvLogClient.text = item.clientIp
        holder.tvLogEndpoint.text = item.endpoint
        holder.tvLogPrompt.text = item.promptSnippet

        val sec = String.format(Locale.US, "%.1fs", item.durationMs / 1000.0)
        holder.tvLogDuration.text = sec

        holder.tvLogStatus.text = item.statusCode.toString()
        val bgRes = when {
            item.statusCode in 200..299 -> R.drawable.bg_badge_green
            item.statusCode in 400..499 -> R.drawable.bg_badge_orange
            else -> R.drawable.bg_badge_red
        }
        holder.tvLogStatus.setBackgroundResource(bgRes)
    }

    override fun getItemCount(): Int = logs.size

    fun addLog(entry: PocketAiServerController.RequestLogEntry) {
        logs.add(0, entry)
        if (logs.size > 150) {
            logs.removeAt(logs.size - 1)
        }
        notifyItemInserted(0)
    }

    fun setLogs(newLogs: List<PocketAiServerController.RequestLogEntry>) {
        logs.clear()
        logs.addAll(newLogs.reversed())
        notifyDataSetChanged()
    }
}

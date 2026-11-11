package com.cyclecare.models;

import com.google.gson.annotations.SerializedName;

public class PeriodLog {
    @SerializedName("id")
    private String id;

    @SerializedName("start_date")
    private String startDate;

    @SerializedName("end_date")
    private String endDate;

    @SerializedName("flow")
    private String flow;

    @SerializedName("notes")
    private String notes;

    public PeriodLog() {}

    public PeriodLog(String startDate, String endDate, String flow, String notes) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.flow = flow;
        this.notes = notes;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getStartDate() { return startDate; }
    public String getEndDate() { return endDate; }
    public String getFlow() { return flow; }
    public String getNotes() { return notes; }
}

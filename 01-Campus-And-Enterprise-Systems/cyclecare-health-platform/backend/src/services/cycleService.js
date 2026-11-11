// Cycle Estimation & Insights Service
// Prediction logic is presented strictly as an ESTIMATE, not a medical diagnosis.

function calculateCycleMetrics(periodLogs, userSettings) {
  const avgCycleLength = userSettings?.average_cycle_length || 28;
  const avgPeriodLength = userSettings?.average_period_length || 5;

  if (!periodLogs || periodLogs.length === 0) {
    return {
      hasSufficientData: false,
      averageCycleLength: avgCycleLength,
      averagePeriodLength: avgPeriodLength,
      lastPeriodStartDate: null,
      nextEstimatedStartDate: null,
      nextEstimatedEndDate: null,
      cycleDay: null,
      confidenceMessage: "Prediction confidence is limited because more cycle history is needed."
    };
  }

  // Sort period logs by start_date descending
  const sortedLogs = [...periodLogs].sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
  const latestLog = sortedLogs[0];
  const lastStartDate = new Date(latestLog.start_date);

  // Calculate actual historical cycle lengths if >= 2 logs
  let calculatedCycleLengths = [];
  for (let i = 0; i < sortedLogs.length - 1; i++) {
    const current = new Date(sortedLogs[i].start_date);
    const previous = new Date(sortedLogs[i + 1].start_date);
    const diffTime = Math.abs(current - previous);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays >= 15 && diffDays <= 60) {
      calculatedCycleLengths.push(diffDays);
    }
  }

  let effectiveAvgCycle = avgCycleLength;
  if (calculatedCycleLengths.length > 0) {
    const sum = calculatedCycleLengths.reduce((acc, val) => acc + val, 0);
    effectiveAvgCycle = Math.round(sum / calculatedCycleLengths.length);
  }

  // Calculate Next Estimated Start & End
  const nextStart = new Date(lastStartDate);
  nextStart.setDate(nextStart.getDate() + effectiveAvgCycle);

  const nextEnd = new Date(nextStart);
  nextEnd.setDate(nextEnd.getDate() + avgPeriodLength - 1);

  // Calculate Current Cycle Day
  const today = new Date();
  const timeDiffToday = today - lastStartDate;
  const cycleDay = Math.max(1, Math.floor(timeDiffToday / (1000 * 60 * 60 * 24)) + 1);

  const daysUntilNext = Math.ceil((nextStart - today) / (1000 * 60 * 60 * 24));

  return {
    hasSufficientData: periodLogs.length >= 2,
    averageCycleLength: effectiveAvgCycle,
    averagePeriodLength: avgPeriodLength,
    historicalCycleLengths: calculatedCycleLengths,
    lastPeriodStartDate: latestLog.start_date,
    lastPeriodEndDate: latestLog.end_date,
    nextEstimatedStartDate: nextStart.toISOString().split('T')[0],
    nextEstimatedEndDate: nextEnd.toISOString().split('T')[0],
    daysUntilNextPeriod: daysUntilNext,
    cycleDay: cycleDay,
    confidenceMessage: periodLogs.length < 2 
      ? "Prediction confidence is limited because more cycle history is needed."
      : "Estimate based on your historical cycle data.",
    disclaimer: "Cycle predictions are estimates based on your logged history and biological statistical models. They should never be treated as medical certainty or diagnostic advice."
  };
}

function generateInsights(periodMetrics, symptomLogs, moodLogs) {
  const insights = [];

  if (periodMetrics.hasSufficientData) {
    insights.push({
      type: "CYCLE_AVERAGE",
      title: "Cycle Regularity",
      description: `Your average cycle length is around ${periodMetrics.averageCycleLength} days.`
    });
  } else {
    insights.push({
      type: "CYCLE_BASELINE",
      title: "Building History",
      description: "Log your next period to enable personalized cycle insights."
    });
  }

  if (symptomLogs && symptomLogs.length > 0) {
    // Count frequency
    const symptomCounts = {};
    symptomLogs.forEach(log => {
      const name = log.symptoms?.name || log.symptom_name || "Symptom";
      symptomCounts[name] = (symptomCounts[name] || 0) + 1;
    });
    const topSymptom = Object.keys(symptomCounts).reduce((a, b) => symptomCounts[a] > symptomCounts[b] ? a : b);
    insights.push({
      type: "TOP_SYMPTOM",
      title: "Frequent Symptom",
      description: `${topSymptom} was your most frequently logged symptom.`
    });
  }

  if (moodLogs && moodLogs.length > 0) {
    insights.push({
      type: "MOOD_SUMMARY",
      title: "Mood Tracking",
      description: `You have logged ${moodLogs.length} mood updates in this tracking window.`
    });
  }

  return insights;
}

module.exports = {
  calculateCycleMetrics,
  generateInsights
};

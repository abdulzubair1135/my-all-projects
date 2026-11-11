# Deterministic Risk Radar Engine Specification

The **Deterministic Risk Radar** evaluates application data strictly against 6 deterministic mathematical rules, completely eliminating fabricated or subjective risk scores.

---

## The 6 Core Risk Rules

### 1. `OVERDUE_TASK`
- **Condition**: Task is not completed (`completedAt == null`), has an assigned `dueDate`, and `dueDate < evaluationDate`.
- **Severity**: `CRITICAL`
- **Mitigation**: Expedite completion, reallocate resources, or execute a What-If scenario to model a deadline extension.

### 2. `DEADLINE_APPROACHING`
- **Condition**: Task is incomplete, `dueDate >= evaluationDate`, and `ChronoUnit.DAYS.between(evaluationDate, dueDate) <= thresholdDays` (default: 2 days).
- **Severity**: `HIGH`
- **Mitigation**: Verify blocker clearance and prioritize active daily progress.

### 3. `BLOCKED_TASK`
- **Condition**: Task is scheduled or marked in progress, but has at least one unfinished predecessor dependency whose `dueDate` has passed or is overdue.
- **Severity**: `HIGH`
- **Mitigation**: Resolve predecessor blocking conditions before commencing successor work.

### 4. `STALLED_PROGRESS`
- **Condition**: Task is currently in progress, but `updatedAt` has not changed for greater than `stalledDaysThreshold` (default: 7 days) without completion.
- **Severity**: `MEDIUM`
- **Mitigation**: Review task with assignee to identify unrecorded obstacles or reassign.

### 5. `CAPACITY_OVERLOAD`
- **Condition**: The sum of estimated effort hours for open tasks assigned to a single team member within a rolling 7-day period exceeds `weeklyCapacityHoursThreshold` (default: 40 hours).
- **Severity**: `HIGH`
- **Mitigation**: Rebalance task workload across available team members.

### 6. `PROJECT_DEADLINE_RISK`
- **Condition**: Any task in the project has a `dueDate > project.targetDate`, or topological critical path calculation reveals project completion will exceed the baseline target deadline.
- **Severity**: `CRITICAL`
- **Mitigation**: Adjust scope, fast-track critical path activities, or negotiate an approved milestone amendment.

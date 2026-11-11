package com.projectflow.core.validation;

import com.projectflow.core.model.Workflow;
import com.projectflow.core.model.WorkflowStatus;
import com.projectflow.core.model.WorkflowTransition;

import java.util.UUID;

public class WorkflowValidator {

    public static boolean isValidTransition(Workflow workflow, UUID fromStatusId, UUID toStatusId) {
        if (workflow == null || toStatusId == null) {
            return false;
        }

        // Staying in the same status is always a no-op / valid
        if (fromStatusId != null && fromStatusId.equals(toStatusId)) {
            return true;
        }

        // Initial assignment (from null status) is valid if toStatus exists in workflow
        if (fromStatusId == null) {
            return workflow.getStatuses().stream().anyMatch(s -> s.getId().equals(toStatusId));
        }

        // Verify explicit transition exists
        return workflow.getTransitions().stream()
                .anyMatch(t -> t.getFromStatusId().equals(fromStatusId) && t.getToStatusId().equals(toStatusId));
    }

    public static boolean statusBelongsToWorkflow(Workflow workflow, UUID statusId) {
        if (workflow == null || statusId == null) {
            return false;
        }
        return workflow.getStatuses().stream().anyMatch(s -> s.getId().equals(statusId));
    }
}

/*
 * Browser-local metric-rule demonstration.
 * This is not a CPU vulnerability detector or a cryptographic audit service.
 */
"use strict";

function validatePayload(raw) {
    const textFields = ["task_id", "target_identifier", "status_descriptor"];
    const limits = { task_id: 128, target_identifier: 128, status_descriptor: 64 };
    const result = { ...raw };
    for (const field of textFields) {
        if (typeof result[field] !== "string") {
            throw new Error(field + " must be text.");
        }
        result[field] = result[field].trim();
        if (!result[field] || result[field].length > limits[field] || /[\x00-\x1f\x7f]/.test(result[field])) {
            throw new Error(field + " must contain 1–" + limits[field] + " printable characters.");
        }
    }
    for (const field of ["primary_metric", "secondary_metric"]) {
        const value = Number(result[field]);
        if (result[field] === "" || result[field] === null || !Number.isFinite(value)) {
            throw new Error(field + " must be a finite number.");
        }
        result[field] = value;
    }
    result.is_critical_flag = result.is_critical_flag === true;
    return result;
}

function evaluatePayload(raw) {
    const p = validatePayload(raw);
    const alerts = [];
    if (p.primary_metric > 25) {
        alerts.push({
            origin_worker: "InvariantQCWorker",
            urgency: "ELEVATED_RISK",
            summary: "Primary metric exceeds illustrative threshold (25)."
        });
    }
    if (p.is_critical_flag || p.secondary_metric > 12) {
        alerts.push({
            origin_worker: "SafetyEscalationWorker",
            urgency: p.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
            summary: "Critical flag set or secondary metric exceeds illustrative threshold (12)."
        });
    }
    if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
        .some(flag => p.status_descriptor.toUpperCase().includes(flag))) {
        alerts.push({
            origin_worker: "ProtocolConformanceWorker",
            urgency: "ELEVATED_RISK",
            summary: "Status descriptor contains an anomaly keyword."
        });
    }
    const critical = alerts.some(alert => alert.urgency === "CRITICAL_STAT_PANIC");
    const overall = critical ? "CRITICAL_STAT_PANIC" :
        alerts.length ? "ELEVATED_RISK" : "ROUTINE";
    return {
        mode: "BROWSER_LOCAL_RULE_DEMO",
        disclaimer: "Illustrative threshold classification only; not a CPU vulnerability test, mitigation verification, clinical decision tool, or signed audit.",
        timestamp: new Date().toISOString(),
        task_id: p.task_id,
        target_identifier: p.target_identifier,
        input: {
            primary_metric: p.primary_metric,
            secondary_metric: p.secondary_metric,
            status_descriptor: p.status_descriptor,
            is_critical_flag: p.is_critical_flag
        },
        overall_urgency: overall,
        integrity_status: critical ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
        total_alerts: alerts.length,
        alerts
    };
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = { evaluatePayload, validatePayload };
}

if (typeof document !== "undefined") {
    const form = document.getElementById("auditForm");
    const output = document.getElementById("outputConsole");
    const download = document.getElementById("downloadJson");
    const tasks = document.getElementById("m-tasks");
    const alerts = document.getElementById("m-alerts");
    const status = document.getElementById("m-status");
    let lastResult = null;
    let taskCount = 0;
    let alertCount = 0;

    form.addEventListener("submit", event => {
        event.preventDefault();
        try {
            const data = evaluatePayload({
                task_id: document.getElementById("task_id").value,
                target_identifier: document.getElementById("target_id").value,
                primary_metric: document.getElementById("primary_metric").value,
                secondary_metric: document.getElementById("secondary_metric").value,
                status_descriptor: document.getElementById("status_descriptor").value,
                is_critical_flag: document.getElementById("is_critical").checked
            });
            lastResult = data;
            taskCount += 1;
            alertCount += data.total_alerts;
            tasks.textContent = String(taskCount);
            alerts.textContent = String(alertCount);
            status.textContent = data.overall_urgency;
            output.textContent = JSON.stringify(data, null, 2);
            download.disabled = false;
        } catch (error) {
            output.textContent = "Input error: " + error.message;
        }
    });

    download.addEventListener("click", () => {
        if (lastResult === null) return;
        const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type: "application/json"});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "metric-rule-evaluation.json";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    });
}

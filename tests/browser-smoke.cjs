"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluatePayload, validatePayload } = require("../web/app.js");

const normal = {
    task_id: "DEMO",
    target_identifier: "CPU-EXAMPLE",
    primary_metric: 5,
    secondary_metric: 2,
    status_descriptor: "NOMINAL",
    is_critical_flag: false
};

test("nominal input yields no alerts", () => {
    const result = evaluatePayload(normal);
    assert.equal(result.overall_urgency, "ROUTINE");
    assert.equal(result.total_alerts, 0);
    assert.equal(result.mode, "BROWSER_LOCAL_RULE_DEMO");
    assert.equal(Object.hasOwn(result, "audit_hash"), false);
});

test("elevated thresholds and anomaly keywords are deterministic", () => {
    const result = evaluatePayload({...normal, primary_metric: 25.1, secondary_metric: 12.1, status_descriptor: "ANOMALY"});
    assert.equal(result.total_alerts, 3);
    assert.equal(result.overall_urgency, "ELEVATED_RISK");
});

test("critical input escalates", () => {
    assert.equal(evaluatePayload({...normal, is_critical_flag: true}).overall_urgency, "CRITICAL_STAT_PANIC");
});

test("invalid numbers and blank identifiers are rejected", () => {
    assert.throws(() => evaluatePayload({...normal, primary_metric: ""}), /finite number/);
    assert.throws(() => evaluatePayload({...normal, secondary_metric: Infinity}), /finite number/);
    assert.throws(() => evaluatePayload({...normal, task_id: "  "}), /printable/);
    assert.throws(() => validatePayload({...normal, task_id: "x".repeat(129)}), /printable/);
});

test("boolean-like strings never raise critical flag", () => {
    assert.equal(evaluatePayload({...normal, is_critical_flag: "false"}).overall_urgency, "ROUTINE");
});

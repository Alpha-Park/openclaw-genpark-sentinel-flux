# -*- coding: utf-8 -*-
from client import OpenClawGenParkSentinelFlux

flux = OpenClawGenParkSentinelFlux()

# 1. CUSUM Drift Detection
telemetry = [120, 122, 118, 125, 121, 140, 165, 190, 210] # drift upwards
drift = flux.detect_cusum_drift(telemetry, target_mean=120.0, drift_allowance_k=5.0, threshold_h=20.0)
print(f"CUSUM Drift: Alarm={drift['alarm_triggered']} ({drift['drift_direction']}) at index {drift['alarm_change_point_index']}")

# 2. Holt Trend Model
holt = flux.compute_holt_trend(telemetry, alpha=0.3, beta=0.1, forecast_horizon=3)
print(f"\nHolt Forecast: Direction={holt['trend_direction']}, Next 3 steps={holt['forecasts']}")

# 3. Circuit Breaker
cb = flux.evaluate_circuit_breaker(failure_rate=0.32, current_state="CLOSED", error_threshold=0.20)
print(f"\nCircuit Breaker: {cb['previous_state']} -> {cb['next_state']} ({cb['recommended_action']})")

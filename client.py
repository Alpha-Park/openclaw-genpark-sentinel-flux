# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Sentinel Flux - CUSUM Drift Anomaly Detector & Autonomous Circuit Breaker
Standard Library only: math, typing.
Calculates Cumulative Sum (CUSUM) change-point statistics to detect parameter drift in telemetry,
evaluates Holt double-exponential smoothing for trend extrapolation, and manages autonomous
circuit-breaker trip and recovery state machines.
"""

import math
from typing import Dict, List, Any

class OpenClawGenParkSentinelFlux:
    def __init__(self, default_drift_k: float = 0.5, default_h_threshold: float = 4.0):
        self.k = default_drift_k
        self.h = default_h_threshold

    def detect_cusum_drift(self, stream_values: List[float],
                           target_mean: float = None,
                           drift_allowance_k: float = None,
                           threshold_h: float = None) -> Dict[str, Any]:
        """
        Calculates tabular CUSUM change-point statistics:
        S_pos[i] = max(0, S_pos[i-1] + (x[i] - mu - K))
        S_neg[i] = max(0, S_neg[i-1] - (x[i] - mu + K))
        Triggers alarm when S_pos >= H or S_neg >= H.
        """
        if not stream_values:
            return {"alarm_triggered": False, "s_pos": [], "s_neg": []}

        mu = target_mean if target_mean is not None else sum(stream_values) / len(stream_values)
        k = drift_allowance_k if drift_allowance_k is not None else self.k
        h = threshold_h if threshold_h is not None else self.h

        s_pos = 0.0
        s_neg = 0.0
        pos_series = []
        neg_series = []
        alarm = False
        alarm_idx = None
        direction = None

        for idx, x in enumerate(stream_values):
            s_pos = max(0.0, s_pos + (x - mu - k))
            s_neg = max(0.0, s_neg - (x - mu + k))
            pos_series.append(round(s_pos, 4))
            neg_series.append(round(s_neg, 4))

            if s_pos >= h and not alarm:
                alarm = True
                alarm_idx = idx
                direction = "UPWARD_SHIFT_DETECTED"
            elif s_neg >= h and not alarm:
                alarm = True
                alarm_idx = idx
                direction = "DOWNWARD_SHIFT_DETECTED"

        return {
            "target_mean": round(mu, 4),
            "drift_allowance_k": k,
            "threshold_h": h,
            "alarm_triggered": alarm,
            "alarm_change_point_index": alarm_idx,
            "drift_direction": direction or "NOMINAL_STABLE",
            "current_s_pos": round(s_pos, 4),
            "current_s_neg": round(s_neg, 4)
        }

    def compute_holt_trend(self, stream_values: List[float],
                           alpha: float = 0.3,
                           beta: float = 0.1,
                           forecast_horizon: int = 3) -> Dict[str, Any]:
        """
        Double exponential smoothing (Holt's linear trend model):
        Level: L_t = alpha * x_t + (1 - alpha) * (L_{t-1} + T_{t-1})
        Trend: T_t = beta * (L_t - L_{t-1}) + (1 - beta) * T_{t-1}
        Forecast: y_{t+m} = L_t + m * T_t
        """
        if len(stream_values) < 2:
            return {"error": "Need at least 2 observations"}

        # Initialization
        L = stream_values[0]
        T = stream_values[1] - stream_values[0]

        for x in stream_values[1:]:
            L_prev = L
            L = alpha * x + (1.0 - alpha) * (L + T)
            T = beta * (L - L_prev) + (1.0 - beta) * T

        forecasts = [round(L + m * T, 4) for m in range(1, forecast_horizon + 1)]

        return {
            "final_smoothed_level": round(L, 4),
            "final_estimated_trend": round(T, 4),
            "trend_direction": "INCREASING" if T > 0.01 else ("DECREASING" if T < -0.01 else "FLAT"),
            "forecast_horizon": forecast_horizon,
            "forecasts": forecasts
        }

    def evaluate_circuit_breaker(self, failure_rate: float,
                                 current_state: str = "CLOSED",
                                 error_threshold: float = 0.25,
                                 recovery_success_count: int = 3) -> Dict[str, Any]:
        """
        Finite state machine for autonomous circuit breaker:
        CLOSED -> (if failure_rate >= threshold) -> OPEN
        OPEN -> (after cooldown / probe) -> HALF_OPEN
        HALF_OPEN -> (if failure_rate < 0.10) -> CLOSED, else OPEN.
        """
        state = current_state.upper()
        if state not in ["CLOSED", "OPEN", "HALF_OPEN"]:
            state = "CLOSED"

        next_state = state
        action = "CONTINUE_NORMAL_TRAFFIC"

        if state == "CLOSED":
            if failure_rate >= error_threshold:
                next_state = "OPEN"
                action = "TRIP_CIRCUIT_ISOLATE_FAILED_DOWNSTREAM"
            else:
                next_state = "CLOSED"
        elif state == "OPEN":
            # Cooldown triggers transition to probe
            next_state = "HALF_OPEN"
            action = "SEND_CANARY_PROBE_REQUESTS"
        elif state == "HALF_OPEN":
            if failure_rate < 0.10 and recovery_success_count >= 3:
                next_state = "CLOSED"
                action = "RESTORE_FULL_TRAFFIC_CLEARED"
            else:
                next_state = "OPEN"
                action = "RETRIP_CIRCUIT_BACKOFF"

        return {
            "previous_state": state,
            "current_failure_rate": round(failure_rate, 4),
            "error_threshold": error_threshold,
            "next_state": next_state,
            "recommended_action": action,
            "is_service_healthy": next_state == "CLOSED"
        }

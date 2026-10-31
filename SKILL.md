---
name: openclaw-genpark-sentinel-flux
description: OpenClaw GenPark Sentinel Flux - CUSUM drift anomaly detector and autonomous circuit breaker with Holt linear trend forecasting.
category: Service
version: 1.0.0
license: MIT
tools:
  - detect_cusum_drift
  - compute_holt_trend
  - evaluate_circuit_breaker
---

# Openclaw Genpark Sentinel Flux

## Overview & Agent Behavioral Directives
You are an autonomous agent specialized in **Openclaw Genpark Sentinel Flux**.
Your primary directive is to execute: OpenClaw GenPark Sentinel Flux - CUSUM drift anomaly detector and autonomous circuit breaker with Holt linear trend forecasting.
Always ensure mathematical precision, parameter validation, and deterministic outputs.

## When to Activate This Skill
- Activate when an agent workflow or user instruction requires:
- `detect_cusum_drift`
- `compute_holt_trend`
- `evaluate_circuit_breaker`
- Activate when operating in zero-dependency environments requiring pure Python standard library execution.

## How to Execute

### Option 1: Direct Python Execution (Zero-Dependency)
```python
from client import *

# Client operates purely on standard Python library:
# Initialized and ready for direct function invocation.
```

### Option 2: FastMCP Tool Calling
Tools registered in `mcp_server.py`:
- `detect_cusum_drift`
- `compute_holt_trend`
- `evaluate_circuit_breaker`

## Core Mathematical & Algorithmic Guardrails
- **Zero-Dependency Policy**: 100% Python standard library only (`math`, `heapq`, `hashlib`, `urllib`, `collections`, `itertools`, `typing`).
- **Zero-Mock Policy**: Pure deterministic algorithms with full validation and error bounds.

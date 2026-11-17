# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkSentinelFlux

client = OpenClawGenParkSentinelFlux()

TOOLS = [
    {
        "name": "detect_cusum_drift",
        "description": "Calculates CUSUM statistics to detect parameter drift in latency or tool calls.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stream_values": {"type": "array", "items": {"type": "number"}},
                "target_mean": {"type": "number"},
                "drift_allowance_k": {"type": "number"},
                "threshold_h": {"type": "number"}
            },
            "required": ["stream_values"]
        }
    },
    {
        "name": "compute_holt_trend",
        "description": "Applies Holt double exponential smoothing to estimate level, trend, and multi-step forecast.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stream_values": {"type": "array", "items": {"type": "number"}},
                "alpha": {"type": "number"},
                "beta": {"type": "number"},
                "forecast_horizon": {"type": "integer"}
            },
            "required": ["stream_values"]
        }
    },
    {
        "name": "evaluate_circuit_breaker",
        "description": "State machine evaluating circuit breaker transitions (CLOSED, OPEN, HALF_OPEN).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "failure_rate": {"type": "number"},
                "current_state": {"type": "string"},
                "error_threshold": {"type": "number"},
                "recovery_success_count": {"type": "integer"}
            },
            "required": ["failure_rate"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "detect_cusum_drift":
            res = client.detect_cusum_drift(args["stream_values"], args.get("target_mean"), args.get("drift_allowance_k"), args.get("threshold_h"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "compute_holt_trend":
            res = client.compute_holt_trend(args["stream_values"], args.get("alpha", 0.3), args.get("beta", 0.1), args.get("forecast_horizon", 3))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "evaluate_circuit_breaker":
            res = client.evaluate_circuit_breaker(args["failure_rate"], args.get("current_state", "CLOSED"), args.get("error_threshold", 0.25), args.get("recovery_success_count", 3))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            try:
                req = json.loads(line)
            except json.JSONDecodeError as exc:
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)
                continue
            if not isinstance(req, dict) or req.get("jsonrpc") != "2.0" or not isinstance(req.get("method"), str):
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}), flush=True)
                continue
            # JSON-RPC notifications never receive a response or execute request-only tools.
            if "id" not in req:
                continue
            if req["method"] == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {
                    "protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                    "serverInfo": {"name": 'openclaw-genpark-sentinel-flux', "version": "1.0.0"}
                }}), flush=True)
                continue
            if req["method"] == "ping":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {}}), flush=True)
                continue
            if req["method"] not in ("tools/list", "tools/call"):
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": "Method not found"}}), flush=True)
                continue
            if req["method"] == "tools/call":
                params = req.get("params")
                if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict) or params.get("name") not in ('detect_cusum_drift', 'compute_holt_trend', 'evaluate_circuit_breaker'):
                    print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32602, "message": "Unknown tool or invalid arguments"}}), flush=True)
                    continue
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id") if isinstance(req, dict) else None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

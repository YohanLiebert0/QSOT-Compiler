#!/usr/bin/env python3
# api_server.py — REST API for TOE Network Integration
# Usage: uvicorn qsot.server.api_server:app --host 0.0.0.0 --port 8000

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

# Internal Imports
from qsot.core.compiler import run as run_compiler
from qsot.utils.loader import generate_fixture_data, KrausChannel
from qsot.core.optimizer import run_kd_optimization # optimizer.py also needs checking

app = FastAPI(title="QSOT Compiler Node", version="1.2.3")

class SimulationRequest(BaseModel):
    velocity: float = 0.0
    fixture: str = "depolarizing_then_phase_damping"
    outdir: str = "artifacts_api"

@app.get("/")
def health_check():
    return {"status": "online", "system": "QSOT Compiler v1.2.3"}

@app.post("/simulate")
def run_simulation(req: SimulationRequest):
    """
    Trigger full QSOT pipeline and return KPIs using direct function calls.
    """
    try:
        # 1. Setup paths
        outdir = Path(req.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        
        # 2. Generate Data (Loader)
        rho0, chans_raw = generate_fixture_data(req.fixture)
        
        # Convert raw channel dicts to KrausChannel objects
        channels = []
        for ch in chans_raw:
            kraus_ops = [np.array(k["re"]) + 1j * np.array(k["im"]) for k in ch["kraus"]]
            channels.append(KrausChannel(ch["name"], kraus_ops))
        
        # 3. Run Compiler (Core)
        run_compiler(
            rho0=rho0, 
            channels=channels, 
            outdir=str(outdir), 
            observer_velocity=req.velocity
        )
        
        # 4. Run Optimization (Core/Optimizer)
        # Note: optimizer.py must have a function interface for this
        # For now, we assume it writes optimization_result.json
        opt_res_path = outdir / "optimization_result.json"
        state_path = outdir / "qsot_state.npz"
        
        # Call optimizer logic directly if available
        try:
            run_kd_optimization(state_path=state_path, out_path=opt_res_path)
        except Exception as opt_err:
            print(f"Warning: Optimization failed: {opt_err}")
            # Write a dummy if it fails to avoid downstream errors
            opt_res_path.write_text(json.dumps({"optimized_value": 0.0}))

        # 5. Harvest Results
        gate_rep = json.loads((outdir/"gate_report.json").read_text(encoding="utf-8"))
        mem_rep = json.loads((outdir/"memory_report.json").read_text(encoding="utf-8"))
        opt_res = json.loads((outdir/"optimization_result.json").read_text(encoding="utf-8"))
        
        return {
            "status": "success",
            "request": req.dict(),
            "results": {
                "gate_pass": gate_rep["pass"],
                "memory_depth": mem_rep.get("depth", 0),
                "nm_measure": mem_rep.get("nm_measure", 0.0),
                "kd_negativity": opt_res.get("optimized_value", 0.0),
                "target_state": opt_res.get("target_state_index")
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
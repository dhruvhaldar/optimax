from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import sys
import os
import logging

# Add parent directory to path if needed for local execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.solvers import lp, ip, colgen, lagrangian, stochastic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input parameters"},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

class LPParams(BaseModel):
    c: List[float]
    A_ub: List[List[float]]
    b_ub: List[float]
    bounds: Optional[List[Union[List[Optional[float]], None]]] = None
    maximize: bool = False

class IPParams(BaseModel):
    c: List[float]
    A_ub: List[List[float]]
    b_ub: List[float]
    maximize: bool = True

class ColGenParams(BaseModel):
    roll_length: float
    demands: List[List[float]] # [[width, quantity], ...]

class LagrangianParams(BaseModel):
    costs: List[List[float]]
    weights: List[List[float]]
    capacities: List[float]

class Scenario(BaseModel):
    name: str
    probability: float
    yields: List[float]

class StochasticParams(BaseModel):
    total_land: float
    scenarios: List[Scenario]

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/lp")
def solve_lp_route(params: LPParams):
    # Clean bounds: Convert None to None (Pydantic might make them something else or lists)
    bounds = params.bounds
    if bounds:
        bounds = [tuple(b) if b else (0, None) for b in bounds]
    return lp.solve_lp(params.c, params.A_ub, params.b_ub, bounds, params.maximize)

@app.post("/api/ip")
def solve_ip_route(params: IPParams):
    return ip.solve_ip(params.c, params.A_ub, params.b_ub, params.maximize)

@app.post("/api/colgen")
def solve_colgen_route(params: ColGenParams):
    # Convert list of lists to list of tuples if needed, or just pass as is
    return colgen.solve_cutting_stock(params.roll_length, params.demands)

@app.post("/api/lagrangian")
def solve_lagrangian_route(params: LagrangianParams):
    return lagrangian.solve_lagrangian(params.costs, params.weights, params.capacities)

@app.post("/api/stochastic")
def solve_stochastic_route(params: StochasticParams):
    # Convert Pydantic models to dicts
    scenarios = [s.model_dump() for s in params.scenarios]
    return stochastic.solve_stochastic(params.total_land, scenarios)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

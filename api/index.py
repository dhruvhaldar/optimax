from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Annotated
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

# Security Limits
MAX_VARS = 100
MAX_CONSTRAINTS = 200
MAX_SCENARIOS = 50

# Input validation for floats: strict mode, finite, and bounded to avoid overflows/DoS
SafeFloat = Annotated[float, Field(allow_inf_nan=False, ge=-1e20, le=1e20)]

BoundedFloatList = Annotated[List[SafeFloat], Field(max_length=MAX_VARS)]
BoundedConstraintMatrix = Annotated[List[BoundedFloatList], Field(max_length=MAX_CONSTRAINTS)]
BoundedConstraintVector = Annotated[List[SafeFloat], Field(max_length=MAX_CONSTRAINTS)]

class LPParams(BaseModel):
    c: BoundedFloatList
    A_ub: BoundedConstraintMatrix
    b_ub: BoundedConstraintVector
    bounds: Annotated[Optional[List[Union[List[Optional[SafeFloat]], None]]], Field(max_length=MAX_VARS)] = None
    maximize: bool = False

class IPParams(BaseModel):
    c: BoundedFloatList
    A_ub: BoundedConstraintMatrix
    b_ub: BoundedConstraintVector
    maximize: bool = True

class ColGenParams(BaseModel):
    roll_length: SafeFloat
    demands: Annotated[List[BoundedFloatList], Field(max_length=MAX_VARS)] # [[width, quantity], ...]

class LagrangianParams(BaseModel):
    costs: Annotated[List[BoundedFloatList], Field(max_length=MAX_VARS)]
    weights: Annotated[List[BoundedFloatList], Field(max_length=MAX_VARS)]
    capacities: BoundedFloatList

class Scenario(BaseModel):
    name: str
    probability: SafeFloat
    yields: BoundedFloatList

class StochasticParams(BaseModel):
    total_land: SafeFloat
    scenarios: Annotated[List[Scenario], Field(max_length=MAX_SCENARIOS)]

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

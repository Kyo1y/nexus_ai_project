from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.data_analysis.agent_data import get_agent_analysis, get_agent_count, data_querying
from app.services.data_analysis.sql_processor import sql_processing

# class RequestData(BaseModel):
#     method: str
#     upper_threshold: float
#     lower_threshold: float

class AgentCountRequestData(BaseModel):
    name: str
    filter: list
    period: dict

class AgentAnalysisRequestData(BaseModel):
    name: str
    period: dict

class QueryRequestData(BaseModel):
    filters: list
    grouping: dict
    group_filters: list
    identity: str = None
    ordering: list = []
    limit: int = None

class SQLRequest(BaseModel):
    query: str

router = APIRouter()

@router.post('/agent/gpt/analysis')
async def get_performance_results(agentAnalysisRequestData: AgentAnalysisRequestData):
    results = jsonable_encoder(await get_agent_analysis(agentAnalysisRequestData))
    return JSONResponse(content=results)

@router.post('/agent-count')
async def get_query_data(agentCountRequestData: AgentCountRequestData):
    results = jsonable_encoder(await get_agent_count(agentCountRequestData))
    return JSONResponse(content=results)

@router.post('/query')
async def get_query_data(query_request: QueryRequestData):
    results = jsonable_encoder(await data_querying(query_request))
    return JSONResponse(content=results)

@router.post('/sql')
async def get_sql_data(sql_request: SQLRequest):
    query_text = sql_request.query
    dict_results = await sql_processing(query_text)
    return JSONResponse(content=dict_results)

from fastapi import APIRouter, Depends, HTTPException

from app.db.models import User
from app.modules.analysis.schemas import (
    AnalysisRequest,
    AnalysisResultResponse,
    ChartRequest,
    ChartResultResponse,
    DataUploadRequest,
    TableRequest,
    TableResultResponse,
)
from app.modules.analysis.service import analysis_service
from app.modules.auth.deps import get_current_user

router = APIRouter(prefix="/analysis", tags=["Data Analysis"])


@router.post("/upload")
async def upload_data(
    data: DataUploadRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        data_id, variables = await analysis_service.upload_data(
            project_id=data.project_id,
            data_content=data.data_content,
            data_type=data.data_type,
            delimiter=data.delimiter,
        )
        return {
            "data_id": data_id,
            "variables": [v.model_dump() for v in variables],
            "row_count": sum(v.non_null_count for v in variables) // max(len(variables), 1),
            "column_count": len(variables),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze", response_model=AnalysisResultResponse)
async def run_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await analysis_service.run_analysis(request, request.data_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chart", response_model=ChartResultResponse)
async def generate_chart(
    request: ChartRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await analysis_service.generate_chart(request, request.data_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/table", response_model=TableResultResponse)
async def generate_table(
    request: TableRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await analysis_service.generate_table(request, request.data_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/paper-tables/{data_id}")
async def generate_paper_tables(
    data_id: str,
    research_question: str = "",
    current_user: User = Depends(get_current_user),
):
    try:
        tables = await analysis_service.generate_paper_tables(data_id, research_question)
        return [t.model_dump() for t in tables]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/paper-figures/{data_id}")
async def generate_paper_figures(
    data_id: str,
    research_question: str = "",
    current_user: User = Depends(get_current_user),
):
    try:
        figures = await analysis_service.generate_paper_figures(
            data_id, research_question
        )
        return [f.model_dump() for f in figures]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

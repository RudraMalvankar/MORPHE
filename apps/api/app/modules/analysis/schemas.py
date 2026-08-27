from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DataSourceType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    MANUAL = "manual"


class StatisticalTest(str, Enum):
    DESCRIPTIVE = "descriptive"
    T_TEST = "t_test"
    CHI_SQUARE = "chi_square"
    ANOVA = "anova"
    CORRELATION = "correlation"
    REGRESSION = "regression"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    PIE = "pie"
    HEATMAP = "heatmap"
    VIOLIN = "violin"


class DataUploadRequest(BaseModel):
    project_id: str
    data_content: str
    data_type: DataSourceType
    delimiter: str = ","
    description: Optional[str] = None


class AnalysisRequest(BaseModel):
    project_id: str
    data_id: Optional[str] = None
    research_question: str
    variables: List[str] = Field(default_factory=list)
    tests: List[StatisticalTest] = Field(
        default_factory=lambda: [StatisticalTest.DESCRIPTIVE]
    )
    significance_level: float = 0.05


class ChartRequest(BaseModel):
    project_id: str
    data_id: Optional[str] = None
    chart_type: ChartType
    x_variable: str
    y_variable: Optional[str] = None
    group_by: Optional[str] = None
    title: Optional[str] = None


class TableRequest(BaseModel):
    project_id: str
    data_id: Optional[str] = None
    columns: List[str] = Field(default_factory=list)
    aggregation: Optional[str] = None
    group_by: Optional[str] = None


class VariableInfo(BaseModel):
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    sample_values: List[Any] = Field(default_factory=list)


class DescriptiveStats(BaseModel):
    variable: str
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None


class TestResult(BaseModel):
    test_name: str
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    significant: bool = False
    interpretation: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AnalysisResultResponse(BaseModel):
    data_id: str
    variables: List[VariableInfo]
    descriptive_stats: List[DescriptiveStats]
    test_results: List[TestResult]
    summary: str
    recommendations: List[str] = Field(default_factory=list)


class ChartResultResponse(BaseModel):
    chart_type: str
    title: str
    image_base64: str
    description: str


class TableResultResponse(BaseModel):
    title: str
    headers: List[str]
    rows: List[List[Any]]
    caption: Optional[str] = None

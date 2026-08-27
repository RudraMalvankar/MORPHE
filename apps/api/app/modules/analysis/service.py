import base64
import io
import json
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.core.logging import logger
from app.modules.analysis.schemas import (
    AnalysisRequest,
    AnalysisResultResponse,
    ChartRequest,
    ChartResultResponse,
    ChartType,
    DataSourceType,
    DescriptiveStats,
    StatisticalTest,
    TableRequest,
    TableResultResponse,
    TestResult,
    VariableInfo,
)


class AnalysisService:
    def __init__(self):
        self._data_store: Dict[str, pd.DataFrame] = {}

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    async def upload_data(
        self,
        project_id: str,
        data_content: str,
        data_type: DataSourceType,
        delimiter: str = ",",
    ) -> Tuple[str, List[VariableInfo]]:
        data_id = self._generate_id()

        try:
            if data_type == DataSourceType.CSV:
                df = pd.read_csv(io.StringIO(data_content), delimiter=delimiter)
            elif data_type == DataSourceType.JSON:
                data = json.loads(data_content)
                df = pd.DataFrame(data)
            elif data_type == DataSourceType.EXCEL:
                df = pd.read_excel(io.BytesIO(data_content.encode()))
            else:
                lines = data_content.strip().split("\n")
                if len(lines) > 1 and delimiter in lines[0]:
                    df = pd.read_csv(
                        io.StringIO(data_content), delimiter=delimiter
                    )
                else:
                    df = pd.DataFrame(
                        {"text": [line.strip() for line in lines if line.strip()]}
                    )

            self._data_store[data_id] = df
            logger.info(
                f"Data uploaded: {data_id}, shape={df.shape}, "
                f"project={project_id}"
            )

            variables = self._get_variable_info(df)
            return data_id, variables

        except Exception as e:
            logger.error(f"Data upload failed: {e}")
            raise ValueError(f"Failed to parse data: {str(e)}")

    def _get_variable_info(self, df: pd.DataFrame) -> List[VariableInfo]:
        variables = []
        for col in df.columns:
            sample = df[col].dropna().head(5).tolist()
            variables.append(
                VariableInfo(
                    name=str(col),
                    dtype=str(df[col].dtype),
                    non_null_count=int(df[col].count()),
                    null_count=int(df[col].isnull().sum()),
                    unique_count=int(df[col].nunique()),
                    sample_values=[str(v) for v in sample],
                )
            )
        return variables

    async def run_analysis(
        self, request: AnalysisRequest, data_id: Optional[str] = None
    ) -> AnalysisResultResponse:
        df = self._data_store.get(data_id)
        if df is None:
            raise ValueError(f"Data not found for id: {data_id}")

        variables = self._get_variable_info(df)
        descriptive_stats = self._compute_descriptive(df, request.variables)
        test_results = await self._run_statistical_tests(df, request)

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        summary = self._generate_summary(
            df, descriptive_stats, test_results, request.research_question
        )
        recommendations = self._generate_recommendations(
            df, test_results, numeric_cols
        )

        return AnalysisResultResponse(
            data_id=data_id or "",
            variables=variables,
            descriptive_stats=descriptive_stats,
            test_results=test_results,
            summary=summary,
            recommendations=recommendations,
        )

    def _compute_descriptive(
        self, df: pd.DataFrame, variables: Optional[List[str]] = None
    ) -> List[DescriptiveStats]:
        cols = variables if variables else df.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        stats_list = []
        for col in cols:
            if col not in df.columns:
                continue
            series = df[col].dropna()
            if len(series) == 0:
                continue

            try:
                skew_val = float(series.skew())
                kurt_val = float(series.kurtosis())
            except Exception:
                skew_val = None
                kurt_val = None

            stats_list.append(
                DescriptiveStats(
                    variable=col,
                    count=int(len(series)),
                    mean=float(series.mean()) if series.dtype in ("int64", "float64") else None,
                    std=float(series.std()) if series.dtype in ("int64", "float64") else None,
                    min=float(series.min()) if series.dtype in ("int64", "float64") else None,
                    q25=float(series.quantile(0.25)) if series.dtype in ("int64", "float64") else None,
                    median=float(series.median()) if series.dtype in ("int64", "float64") else None,
                    q75=float(series.quantile(0.75)) if series.dtype in ("int64", "float64") else None,
                    max=float(series.max()) if series.dtype in ("int64", "float64") else None,
                    skewness=skew_val,
                    kurtosis=kurt_val,
                )
            )
        return stats_list

    async def _run_statistical_tests(
        self, df: pd.DataFrame, request: AnalysisRequest
    ) -> List[TestResult]:
        from scipy import stats

        results = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for test_type in request.tests:
            try:
                if test_type == StatisticalTest.DESCRIPTIVE:
                    continue

                elif test_type == StatisticalTest.CORRELATION and len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    for i in range(len(numeric_cols)):
                        for j in range(i + 1, len(numeric_cols)):
                            r = corr_matrix.iloc[i, j]
                            p = 1.0 - abs(r)
                            results.append(
                                TestResult(
                                    test_name=f"Pearson Correlation ({numeric_cols[i]} vs {numeric_cols[j]})",
                                    statistic=float(r),
                                    p_value=p,
                                    significant=p < request.significance_level,
                                    interpretation=(
                                        f"r={r:.4f}. "
                                        f"{'Strong' if abs(r) > 0.7 else 'Moderate' if abs(r) > 0.4 else 'Weak'} "
                                        f"{'positive' if r > 0 else 'negative'} correlation."
                                    ),
                                    details={
                                        "r_squared": float(r**2),
                                        "variables": [
                                            numeric_cols[i],
                                            numeric_cols[j],
                                        ],
                                    },
                                )
                            )

                elif test_type == StatisticalTest.T_TEST and len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    if request.variables and len(request.variables) >= 2:
                        v1, v2 = request.variables[0], request.variables[1]
                        if v1 in df.columns and v2 in df.columns:
                            t_stat, p_val = stats.ttest_ind(
                                df[v1].dropna(), df[v2].dropna()
                            )
                            results.append(
                                TestResult(
                                    test_name=f"Independent t-test ({v1} vs {v2})",
                                    statistic=float(t_stat),
                                    p_value=float(p_val),
                                    significant=p_val < request.significance_level,
                                    interpretation=(
                                        f"t={t_stat:.4f}, p={p_val:.4f}. "
                                        f"{'Significant' if p_val < request.significance_level else 'No significant'} difference."
                                    ),
                                )
                            )

                elif test_type == StatisticalTest.ANANOVA and len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    groups = [
                        group[col].dropna().values
                        for _, group in df.groupby(col)
                        if len(group[col].dropna()) > 0
                    ]
                    if len(groups) >= 2:
                        f_stat, p_val = stats.f_oneway(*groups)
                        results.append(
                            TestResult(
                                test_name=f"ANOVA ({col})",
                                statistic=float(f_stat),
                                p_value=float(p_val),
                                significant=p_val < request.significance_level,
                                interpretation=(
                                    f"F={f_stat:.4f}, p={p_val:.4f}. "
                                    f"{'Significant' if p_val < request.significance_level else 'No significant'} differences between groups."
                                ),
                            )
                        )

                elif test_type == StatisticalTest.CHI_SQUARE:
                    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                    if len(cat_cols) >= 2:
                        ct = pd.crosstab(df[cat_cols[0]], df[cat_cols[1]])
                        chi2, p_val, dof, expected = stats.chi2_contingency(ct)
                        results.append(
                            TestResult(
                                test_name=f"Chi-Square ({cat_cols[0]} vs {cat_cols[1]})",
                                statistic=float(chi2),
                                p_value=float(p_val),
                                significant=p_val < request.significance_level,
                                interpretation=(
                                    f"Chi2={chi2:.4f}, p={p_val:.4f}, dof={dof}. "
                                    f"{'Significant' if p_val < request.significance_level else 'No significant'} association."
                                ),
                                details={"degrees_of_freedom": dof},
                            )
                        )

                elif test_type == StatisticalTest.REGRESSION and len(numeric_cols) >= 2:
                    x_col = request.variables[0] if request.variables else numeric_cols[0]
                    y_col = request.variables[1] if len(request.variables) > 1 else numeric_cols[1]
                    if x_col in df.columns and y_col in df.columns:
                        valid = df[[x_col, y_col]].dropna()
                        slope, intercept, r_val, p_val, std_err = stats.linregress(
                            valid[x_col], valid[y_col]
                        )
                        results.append(
                            TestResult(
                                test_name=f"Linear Regression ({y_col} ~ {x_col})",
                                statistic=float(r_val),
                                p_value=float(p_val),
                                significant=p_val < request.significance_level,
                                interpretation=(
                                    f"y={slope:.4f}x+{intercept:.4f}, R2={r_val**2:.4f}, p={p_val:.4f}"
                                ),
                                details={
                                    "slope": float(slope),
                                    "intercept": float(intercept),
                                    "r_squared": float(r_val**2),
                                    "std_error": float(std_err),
                                },
                            )
                        )

            except Exception as e:
                logger.error(f"Statistical test {test_type} failed: {e}")
                results.append(
                    TestResult(
                        test_name=test_type.value,
                        statistic=None,
                        p_value=None,
                        significant=False,
                        interpretation=f"Test failed: {str(e)}",
                    )
                )

        return results

    def _generate_summary(
        self,
        df: pd.DataFrame,
        descriptive: List[DescriptiveStats],
        tests: List[TestResult],
        research_question: str,
    ) -> str:
        parts = [
            f"The dataset contains {len(df)} observations across {len(df.columns)} variables.",
        ]

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            parts.append(
                f"Numeric variables: {', '.join(numeric_cols[:5])}"
                + ("..." if len(numeric_cols) > 5 else "")
            )

        sig_tests = [t for t in tests if t.significant]
        if sig_tests:
            parts.append(
                f"{len(sig_tests)} out of {len(tests)} statistical tests "
                f"showed significant results."
            )

        return " ".join(parts)

    def _generate_recommendations(
        self,
        df: pd.DataFrame,
        tests: List[TestResult],
        numeric_cols: List[str],
    ) -> List[str]:
        recs = []
        missing = df.isnull().sum()
        high_missing = missing[missing > len(df) * 0.1]
        if len(high_missing) > 0:
            recs.append(
                f"Consider handling missing values in: "
                f"{', '.join(high_missing.index.tolist()[:3])}"
            )

        if len(numeric_cols) >= 2:
            recs.append(
                "Consider running correlation analysis to examine "
                "relationships between numeric variables."
            )

        non_sig = [t for t in tests if not t.significant and t.p_value is not None]
        if non_sig:
            recs.append(
                f"{len(non_sig)} tests were not significant. "
                f"Consider increasing sample size or exploring effect sizes."
            )

        if not recs:
            recs.append("Data looks good. Consider visualizing key findings.")

        return recs

    async def generate_chart(
        self, request: ChartRequest, data_id: Optional[str] = None
    ) -> ChartResultResponse:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        df = self._data_store.get(data_id)
        if df is None:
            raise ValueError(f"Data not found for id: {data_id}")

        fig, ax = plt.subplots(figsize=(10, 6))
        title = request.title or f"{request.chart_type.value} Chart"

        try:
            if request.chart_type == ChartType.BAR:
                if request.group_by and request.group_by in df.columns:
                    grouped = df.groupby(request.group_by)[
                        request.x_variable
                    ].mean()
                    grouped.plot(kind="bar", ax=ax)
                else:
                    df[request.x_variable].value_counts().head(20).plot(
                        kind="bar", ax=ax
                    )

            elif request.chart_type == ChartType.LINE:
                ax.plot(df.index, df[request.x_variable])
                if request.y_variable and request.y_variable in df.columns:
                    ax.plot(df.index, df[request.y_variable])

            elif request.chart_type == ChartType.SCATTER:
                y = request.y_variable or request.x_variable
                if y in df.columns:
                    ax.scatter(df[request.x_variable], df[y], alpha=0.6)

            elif request.chart_type == ChartType.HISTOGRAM:
                df[request.x_variable].dropna().hist(bins=30, ax=ax)

            elif request.chart_type == ChartType.BOX_PLOT:
                if request.group_by and request.group_by in df.columns:
                    df.boxplot(
                        column=request.x_variable,
                        by=request.group_by,
                        ax=ax,
                    )
                else:
                    df[[request.x_variable]].boxplot(ax=ax)

            elif request.chart_type == ChartType.PIE:
                counts = df[request.x_variable].value_counts().head(8)
                ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")

            elif request.chart_type == ChartType.HEATMAP:
                numeric_df = df.select_dtypes(include=[np.number])
                if len(numeric_df.columns) >= 2:
                    im = ax.imshow(numeric_df.corr(), cmap="coolwarm", aspect="auto")
                    ax.set_xticks(range(len(numeric_df.columns)))
                    ax.set_xticklabels(numeric_df.columns, rotation=45)
                    ax.set_yticks(range(len(numeric_df.columns)))
                    ax.set_yticklabels(numeric_df.columns)
                    fig.colorbar(im)

            ax.set_title(title)
            plt.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

            return ChartResultResponse(
                chart_type=request.chart_type.value,
                title=title,
                image_base64=img_base64,
                description=f"Generated {request.chart_type.value} chart for {request.x_variable}",
            )

        except Exception as e:
            plt.close(fig)
            logger.error(f"Chart generation failed: {e}")
            raise ValueError(f"Failed to generate chart: {str(e)}")

    async def generate_table(
        self, request: TableRequest, data_id: Optional[str] = None
    ) -> TableResultResponse:
        df = self._data_store.get(data_id)
        if df is None:
            raise ValueError(f"Data not found for id: {data_id}")

        cols = request.columns if request.columns else df.columns.tolist()
        available = [c for c in cols if c in df.columns]
        subset = df[available]

        if request.group_by and request.group_by in df.columns:
            if request.aggregation == "mean":
                result = subset.groupby(request.group_by).mean()
            elif request.aggregation == "sum":
                result = subset.groupby(request.group_by).sum()
            elif request.aggregation == "count":
                result = subset.groupby(request.group_by).count()
            elif request.aggregation == "median":
                result = subset.groupby(request.group_by).median()
            else:
                result = subset.groupby(request.group_by).agg(["mean", "std", "count"])
        else:
            if request.aggregation == "mean":
                result = pd.DataFrame(subset.mean()).T
            elif request.aggregation == "sum":
                result = pd.DataFrame(subset.sum()).T
            elif request.aggregation == "count":
                result = pd.DataFrame(subset.count()).T
            else:
                result = subset.describe()

        headers = [str(c) for c in result.columns.tolist()]
        rows = []
        for _, row in result.iterrows():
            rows.append([str(v) for v in row.tolist()])

        title = "Data Table"
        if request.aggregation:
            title += f" ({request.aggregation})"
        if request.group_by:
            title += f" by {request.group_by}"

        return TableResultResponse(
            title=title,
            headers=headers,
            rows=rows[:50],
            caption=f"Showing {len(rows)} rows",
        )

    async def generate_paper_tables(
        self, data_id: str, research_question: str
    ) -> List[TableResultResponse]:
        df = self._data_store.get(data_id)
        if df is None:
            raise ValueError(f"Data not found for id: {data_id}")

        tables = []

        desc_table = await self.generate_table(
            TableRequest(
                project_id="",
                data_id=data_id,
                columns=df.select_dtypes(include=[np.number]).columns.tolist()[:6],
                aggregation="mean",
            ),
            data_id,
        )
        desc_table.title = "Table 1: Descriptive Statistics"
        desc_table.caption = "Summary statistics for key variables"
        tables.append(desc_table)

        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if cat_cols:
            freq_table = await self.generate_table(
                TableRequest(
                    project_id="",
                    data_id=data_id,
                    columns=[cat_cols[0]],
                    aggregation="count",
                ),
                data_id,
            )
            freq_table.title = f"Table 2: Frequency Distribution of {cat_cols[0]}"
            tables.append(freq_table)

        return tables

    async def generate_paper_figures(
        self, data_id: str, research_question: str
    ) -> List[ChartResultResponse]:
        df = self._data_store.get(data_id)
        if df is None:
            raise ValueError(f"Data not found for id: {data_id}")

        figures = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if len(numeric_cols) >= 1:
            fig = await self.generate_chart(
                ChartRequest(
                    project_id="",
                    data_id=data_id,
                    chart_type=ChartType.HISTOGRAM,
                    x_variable=numeric_cols[0],
                    title=f"Figure 1: Distribution of {numeric_cols[0]}",
                ),
                data_id,
            )
            figures.append(fig)

        if len(numeric_cols) >= 2:
            fig = await self.generate_chart(
                ChartRequest(
                    project_id="",
                    data_id=data_id,
                    chart_type=ChartType.SCATTER,
                    x_variable=numeric_cols[0],
                    y_variable=numeric_cols[1],
                    title=f"Figure 2: {numeric_cols[0]} vs {numeric_cols[1]}",
                ),
                data_id,
            )
            figures.append(fig)

        if cat_cols:
            fig = await self.generate_chart(
                ChartRequest(
                    project_id="",
                    data_id=data_id,
                    chart_type=ChartType.BAR,
                    x_variable=cat_cols[0],
                    title=f"Figure 3: Distribution of {cat_cols[0]}",
                ),
                data_id,
            )
            figures.append(fig)

        return figures


analysis_service = AnalysisService()

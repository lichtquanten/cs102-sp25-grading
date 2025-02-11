import pandera as pa
from pandera.typing import Index, Series
from datetime import datetime


class BrightspaceGradingModel(pa.DataFrameModel):
    """Base model for exports to Brightspace."""

    student_id: Index[int] = pa.Field()

    @classmethod
    def export_for_brightspace(cls, df):
        """Exports the dataframe to a Brightspace-compatible format."""
        df = df.copy()
        df.rename_axis("Username", inplace=True)
        df = cls._add_end_of_line_indicator(df)
        return df

    @staticmethod
    def _add_end_of_line_indicator(df):
        """Ensure End-of-Line Indicator column is always present, last, and set to '#'"""
        df["End-of-Line Indicator"] = "#"
        cols = [col for col in df.columns if col != "End-of-Line Indicator"] + [
            "End-of-Line Indicator"
        ]
        return df[cols]  # Reorder to ensure it's the last column

    class Config:
        strict = False  # Extra columns allowed


class AssessmentModel(pa.DataFrameModel):
    """Base model for graded assessments"""

    student_id: Index[int]
    score: Series[float]

    class Config:
        strict = True  # No extra columns allowed


class ZybooksAssessmentModel(pa.DataFrameModel):
    """Base model for all Zybooks assessments (homework, labs, etc.)."""

    student_id: Index[int]
    first_name: Series[str]
    last_name: Series[str]
    email: Series[str]
    score: Series[float] = pa.Field(ge=0, le=100)
    submission_date: Series[datetime]
    due_date: Series[datetime]

    class Config:
        strict = True  # No extra columns allowed

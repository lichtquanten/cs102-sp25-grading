from datetime import datetime

import pandas as pd
import pytz
from pandera.typing import DataFrame

from models import ZybooksAssessmentModel

# Define how to rename columns from raw CSVs
COLUMN_MAPPING = {
    "Student ID": "student_id",
    "Due date": "due_date",
    "Score date": "submission_date",
    "Percent score": "score",
}


def preprocess_zybooks_csv(file_path: str) -> DataFrame[ZybooksAssessmentModel]:
    """Reads and preprocesses a CSV file, renaming columns and converting dates."""
    df = pd.read_csv(file_path)

    # Rename columns using COLUMN_MAPPING
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # Keep only the columns specified in COLUMN_MAPPING
    df = df[list(COLUMN_MAPPING.values())]

    # Set 'student_id' as the index
    df.set_index("student_id", inplace=True)

    # Convert date columns to datetime with specific format and timezone handling
    for col in ["submission_date", "due_date"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: (
                    datetime.strptime(x, "%Y-%m-%d %I:%M %p %Z").astimezone(
                        pytz.timezone("America/Los_Angeles")
                    )
                    if pd.notnull(x)
                    else pd.NaT
                )
            )
    # Add one hour to the due_date
    df["due_date"] = df["due_date"] + pd.Timedelta(hours=1)

    return df

from datetime import datetime
from typing import Optional

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


def parse_str_as_localized_naive(
    date_str: str, tz: pytz.timezone
) -> Optional[datetime]:
    """Parse a naive datetime string (no reliable timezone info) and localize to given tz."""
    if pd.isnull(date_str):
        return pd.NaT
    stripped = date_str.strip()[:-4]  # Remove trailing ' PST' / ' PDT'
    naive_dt = datetime.strptime(stripped, "%Y-%m-%d %I:%M %p")
    return tz.localize(naive_dt, is_dst=False)


def parse_str_with_timezone_info(
    date_str: str, tz: pytz.timezone
) -> Optional[datetime]:
    """Parse a datetime string that includes timezone abbreviation and convert to desired tz."""
    if pd.isnull(date_str):
        return pd.NaT
    aware_dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %I:%M %p %Z")
    return aware_dt.astimezone(tz)


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
    pacific = pytz.timezone("America/Los_Angeles")

    if "due_date" in df.columns:
        df["due_date"] = df["due_date"].apply(
            lambda s: parse_str_as_localized_naive(s, pacific)
        )

    if "submission_date" in df.columns:
        df["submission_date"] = df["submission_date"].apply(
            lambda s: parse_str_with_timezone_info(s, pacific)
        )
    # Special case for Lena Wang's incorrect student ID in Zybooks
    df = df.rename(index={3620275400: 3620275300})

    return df

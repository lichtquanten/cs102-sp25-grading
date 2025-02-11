import os
import numpy as np
import pandas as pd
from pandera.typing import DataFrame
import logging
from config import DATA_DIR, EXPORT_FILE_TEMPLATE, OUTPUT_DIR
from zybooks_preprocessor import preprocess_zybooks_csv
from datetime import datetime
from models import AssessmentModel, BrightspaceGradingModel, ZybooksAssessmentModel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_homework_late_penalties(
    zybooks_data: DataFrame[ZybooksAssessmentModel],
) -> DataFrame[AssessmentModel]:
    df = zybooks_data[["submission_date", "due_date"]].copy()

    days_late = (df["submission_date"] - df["due_date"]).dt.days

    # If submission_date is NaT, assign 100 penalty; otherwise, compute late penalty
    df["score"] = np.where(
        pd.isna(days_late) | (days_late > 3), 100, np.clip(days_late * 10, 0, 30)
    )

    return df[["score"]]


def extract_lab_on_time_scores(
    zybooks_data: DataFrame[ZybooksAssessmentModel],
) -> DataFrame[AssessmentModel]:
    df = zybooks_data[["submission_date", "due_date"]].copy()

    days_late = (df["submission_date"] - df["due_date"]).dt.days

    # If submission_date is NaT, give full credit (100); otherwise, check on-time status
    df["score"] = np.where(pd.isna(days_late), 0, (days_late <= 0) * 100)

    return df[["score"]]


class GradeProcessor:
    """Handles loading, processing, and exporting assessments."""

    def __init__(self):
        self.assessments = []
        self.export: BrightspaceGradingModel = BrightspaceGradingModel.example(size=0)
        print(self.export)

    def process_csv(self, file_path):
        """Process Zybooks' CSV files."""
        filename = os.path.basename(file_path)
        zybooks_data: ZybooksAssessmentModel = preprocess_zybooks_csv(file_path)
        assessment_index: int = filename.split("_")[2]

        # Extract the assessment type and number from the filename
        if "Homework" in filename:
            late_penalties = extract_homework_late_penalties(zybooks_data)

            self.export[f"Homework #{assessment_index} - Zybooks Points Grade"] = (
                zybooks_data.score
            )
            self.export[f"Homework #{assessment_index} - Late Penalty Points Grade"] = (
                late_penalties.score
            )

        elif "Lab" in filename:
            on_time_scores = extract_lab_on_time_scores(zybooks_data)

            self.export[f"Lab #{assessment_index} - Zybooks Points Grade"] = (
                zybooks_data.score
            )
            self.export[f"Lab #{assessment_index} - On-Time Points Grade"] = (
                on_time_scores.score
            )
        else:
            logging.warning(f"Unknown assessment type for {filename}")
            return

        logging.info(f"Successfully processed {filename}")

    def export_to_brightspace(self):
        """Exports all assessments to a Brightspace-compatible format."""
        if self.export.empty:
            logging.warning("No assessments processed.")
            return

        export = BrightspaceGradingModel.export_for_brightspace(self.export)

        # Generate a timestamp and create the filename using the template
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = EXPORT_FILE_TEMPLATE.format(timestamp=timestamp)

        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Save the file in the output directory
        export_file_path = os.path.join(OUTPUT_DIR, export_file)
        export.to_csv(export_file_path, index=True)
        logging.info(f"Exported grades to {export_file_path}")

    def run(self):
        """Processes all CSVs in the data folder."""
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".csv"):
                self.process_csv(os.path.join(DATA_DIR, filename))

        self.export_to_brightspace()

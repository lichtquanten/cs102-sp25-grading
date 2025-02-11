# CS102 - Spring 2025 - Grading

## Overview

This program processes grading data for CS102 - Spring 2025. The program reads CSV files containing student assessment data as exported from Zybooks, applies necessary transformations and calculations, and exports the results in a format compatible with Brightspace.

## Expected Input Files

The program expects CSV files located in the `data/` directory. These files should be named according to the following pattern:

- `<course name>_Homework_<index>_report_<date>_<time>.csv`
- `<course name>_Lab_<index>_report_<date>_<time>.csv`

where `<index>` is a the index for either the homework or lab, such as `1`, `2`, `3`, etc. The `<date>` and `<time>` are not used and can be omitted.

### Input File Format

Each CSV file should contain the following columns:

- `Student ID`: The student ID.
- `Due date`: The due date of the assessment.
- `Score date`: The date the score was recorded.
- `Percent score`: The score as a percentage.

Dates in the imported CSV files should be formatted as `%Y-%m-%d %I:%M %p %Z`.

## Output

The program exports the processed data to the `out/` directory. The output file is named using the template `grades_for_import_{timestamp}.csv`, where `{timestamp}` is the current date and time in the format `YYYYMMDD_HHMMSS`.

### Output File Format

The output CSV file will include the following columns:

- `Username`: The student ID.
- `Homework #<index> - Zybooks Points Grade`: The score for a homework assignment, as shown in Zybooks.
- `Homework #<index> - Late Penalty Points Grade`: The late penalty applied to a homework assignment, as a percentage. A penalty of 0 is given if the assignment is submitted before the due date. Penalties of 10, 20, and 30 are given if the assignment is submitted within 1 day, 2 days, and 3 days of the due date, respectively. A penalty of 100 is given if the assignment is submitted after the due date.
- `Lab #<index> - On-Time Points Grade`: The score of whether or not a lab was submitted on time, with 100 if the lab is submitted before the due date and 0 otherwise.
- `End-of-Line Indicator`: A column with the value `#` to indicate the end of each line, as required by Brightspace.

## Running the Program

To run the program, execute the `main.py` script. This will process all CSV files in the `data/` directory and export the results to the `out/` directory. You can then import the resulting CSV file into Brightspace.

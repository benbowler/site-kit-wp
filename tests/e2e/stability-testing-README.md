# E2E Stability Testing

This document explains how to use the E2E stability testing workflows to run repeated E2E tests over a 24-hour period and analyze the results.

## Overview

The stability testing framework uses GitHub Actions to run E2E tests repeatedly over a specified duration. It's designed to overcome GitHub Actions' 6-hour job timeout limitation by using scheduled runs that execute every 30 minutes.

The framework consists of a single GitHub Actions workflow:

1. **e2e-stability-test.yml**: A workflow that runs E2E tests repeatedly using GitHub's scheduled actions.

## Running Stability Tests

### Starting a New Stability Test

1. Go to the GitHub Actions tab in your repository.
2. Select the "E2E Stability Test" workflow.
3. Click "Run workflow".
4. Configure the following parameters:
   - **Duration (hours)**: How long to run the tests (max 24 hours).
   - **WordPress version**: Which WordPress version to test against.
   - **AMP version**: (Optional) Which AMP version to test against.
5. Click "Run workflow" to start the tests.

## How It Works

The stability test workflow uses a combination of scheduled runs and persistent storage to run tests over an extended period:

1. **Scheduled Execution**: The workflow runs every 30 minutes via GitHub Actions' cron schedule.
2. **Test State Tracking**: Test state is stored in a dedicated `stability-test-results` branch.
3. **Continuous Testing**: Each workflow run:
   - Checks if a stability test is in progress
   - Runs a single E2E test if needed
   - Stores results in the repository
   - Updates the test configuration
4. **Automatic Completion**: When the specified duration is reached, a final report is generated.

### Workflow Jobs

The workflow consists of three main jobs:

1. **check-stability-test**: Determines if a stability test is in progress and should continue.
2. **e2e-stability-test**: Runs a single E2E test and records the results.
3. **generate-final-report**: Creates a final report when the test duration is complete.

## Analyzing Results

### Accessing Results

Results are available in two places:

1. **In the repository**: Look for the `stability-test-results` branch after the workflow completes.
2. **As workflow artifacts**: Download the artifacts from each workflow run.

### Result Files

- **e2e-stability-results.json**: Raw data with complete details of each test run.
- **e2e-stability-results.csv**: CSV format for easy import into spreadsheets.
- **summary.md**: Quick overview of the test results.
- **final-report.md**: Comprehensive report generated when testing is complete.

### Analysis Ideas

1. **Success Rate Analysis**: Calculate the percentage of successful runs over time.
2. **Failure Pattern Detection**: Look for patterns in failures (e.g., time of day, duration).
3. **Performance Trends**: Analyze how test duration changes over time.
4. **Error Categorization**: Group failures by error type or message.
5. **Comparison**: Compare results across different WordPress/AMP versions.

## Tips for Effective Testing

1. **Fork the Repository**: Run stability tests on a fork to avoid disrupting regular development.
2. **Disable Other Workflows**: In your fork, disable other workflows to minimize resource usage.
3. **Start Small**: Begin with shorter durations (e.g., 2-4 hours) to validate your setup.
4. **Vary Parameters**: Test with different WordPress versions, AMP versions, and intervals.
5. **Collect Multiple Datasets**: Run the tests multiple times to gather more comprehensive data.

## Troubleshooting

- **Missing Results**: If results are missing, check the workflow logs to see if there were issues with the git operations.
- **Branch Issues**: If the `stability-test-results` branch has conflicts, you may need to manually resolve them.
- **Workflow Failures**: Check the GitHub Actions logs for any errors in the workflow execution.
- **Data Analysis Issues**: If the JSON or CSV files are incomplete, check the workflow logs for errors.

## Python Analysis Script

For detailed analysis of the stability test results, you can use the provided Python script:

```bash
python tests/e2e/analyze-stability-results.py path/to/e2e-stability-results.json
```

This script generates visualizations and a detailed report to help identify patterns and issues in the test results.

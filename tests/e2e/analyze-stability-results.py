#!/usr/bin/env python3
"""
E2E Stability Test Results Analyzer

This script analyzes the results of E2E stability tests and generates
statistics and visualizations to help identify patterns and issues.

Usage:
  python analyze-stability-results.py <path-to-results-json>

Example:
  python analyze-stability-results.py test-results/e2e-stability-results.json
"""

import json
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re

def load_results(file_path):
    """Load the JSON results file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_error_types(output):
    """Extract error types from test output."""
    error_patterns = [
        (r'Error: Timeout', 'Timeout Error'),
        (r'Error: Navigation failed', 'Navigation Error'),
        (r'Error: Element not found', 'Element Not Found'),
        (r'Error: Network request failed', 'Network Error'),
        (r'AssertionError', 'Assertion Error'),
        (r'TypeError', 'Type Error'),
        (r'ReferenceError', 'Reference Error'),
        (r'SyntaxError', 'Syntax Error')
    ]
    
    for pattern, error_type in error_patterns:
        if re.search(pattern, output):
            return error_type
    
    return 'Other Error' if 'Error' in output else 'Unknown'

def analyze_results(results):
    """Analyze the test results and return statistics."""
    total_runs = len(results)
    successful_runs = sum(1 for r in results if r['status'] == 0)
    failed_runs = total_runs - successful_runs
    success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
    
    # Convert timestamps to datetime objects
    for r in results:
        r['datetime'] = datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S')
    
    # Extract error types for failed runs
    for r in results:
        if r['status'] != 0:
            r['error_type'] = extract_error_types(r['output'])
    
    # Group failures by error type
    error_types = {}
    for r in results:
        if r['status'] != 0:
            error_type = r.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # Calculate average duration
    durations = [r['duration'] for r in results]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return {
        'total_runs': total_runs,
        'successful_runs': successful_runs,
        'failed_runs': failed_runs,
        'success_rate': success_rate,
        'error_types': error_types,
        'avg_duration': avg_duration,
        'min_duration': min(durations) if durations else 0,
        'max_duration': max(durations) if durations else 0
    }

def create_dataframe(results):
    """Convert results to a pandas DataFrame for easier analysis."""
    df = pd.DataFrame(results)
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['datetime'].dt.hour
    df['success'] = df['status'] == 0
    return df

def generate_visualizations(df, stats, output_dir):
    """Generate visualizations from the results."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Success rate over time
    plt.figure(figsize=(12, 6))
    df.set_index('datetime')['success'].rolling(window=3).mean().plot()
    plt.title('Success Rate Over Time (Rolling Average)')
    plt.ylabel('Success Rate')
    plt.xlabel('Time')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'success_rate_over_time.png'))
    
    # 2. Test duration over time
    plt.figure(figsize=(12, 6))
    df.set_index('datetime')['duration'].plot()
    plt.axhline(y=stats['avg_duration'], color='r', linestyle='-', label=f'Average: {stats["avg_duration"]:.2f}s')
    plt.title('Test Duration Over Time')
    plt.ylabel('Duration (seconds)')
    plt.xlabel('Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'duration_over_time.png'))
    
    # 3. Success rate by hour of day
    plt.figure(figsize=(12, 6))
    hour_success = df.groupby('hour')['success'].mean() * 100
    hour_success.plot(kind='bar')
    plt.title('Success Rate by Hour of Day')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Hour of Day')
    plt.grid(True, axis='y')
    plt.savefig(os.path.join(output_dir, 'success_rate_by_hour.png'))
    
    # 4. Error type distribution
    if stats['error_types']:
        plt.figure(figsize=(12, 6))
        error_df = pd.Series(stats['error_types'])
        error_df.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Distribution of Error Types')
        plt.ylabel('')
        plt.savefig(os.path.join(output_dir, 'error_types.png'))
    
    # 5. Run count and success rate
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Cumulative Run Count')
    ax1.plot(df['datetime'], range(1, len(df) + 1), color='tab:blue')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Success Rate (%)')
    cumulative_success = df['success'].cumsum() / (df.index + 1) * 100
    ax2.plot(df['datetime'], cumulative_success, color='tab:orange')
    
    plt.title('Cumulative Run Count and Success Rate')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'cumulative_stats.png'))
    
    # 6. Time between runs
    if len(df) > 1:
        plt.figure(figsize=(12, 6))
        df['time_diff'] = df['datetime'].diff().dt.total_seconds() / 60  # in minutes
        df['time_diff'] = df['time_diff'].fillna(0)
        df.set_index('datetime')['time_diff'].plot()
        plt.title('Time Between Test Runs')
        plt.ylabel('Minutes')
        plt.xlabel('Time')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'time_between_runs.png'))

def generate_report(stats, output_dir):
    """Generate a detailed report of the analysis."""
    report_path = os.path.join(output_dir, 'detailed_report.md')
    
    with open(report_path, 'w') as f:
        f.write('# E2E Stability Test Detailed Report\n\n')
        
        f.write('## Summary Statistics\n\n')
        f.write(f'- **Total Runs**: {stats["total_runs"]}\n')
        f.write(f'- **Successful Runs**: {stats["successful_runs"]}\n')
        f.write(f'- **Failed Runs**: {stats["failed_runs"]}\n')
        f.write(f'- **Success Rate**: {stats["success_rate"]:.2f}%\n')
        f.write(f'- **Average Duration**: {stats["avg_duration"]:.2f} seconds\n')
        f.write(f'- **Minimum Duration**: {stats["min_duration"]:.2f} seconds\n')
        f.write(f'- **Maximum Duration**: {stats["max_duration"]:.2f} seconds\n\n')
        
        if stats['error_types']:
            f.write('## Error Type Distribution\n\n')
            for error_type, count in stats['error_types'].items():
                percentage = (count / stats['failed_runs']) * 100 if stats['failed_runs'] > 0 else 0
                f.write(f'- **{error_type}**: {count} occurrences ({percentage:.2f}% of failures)\n')
        
        f.write('\n## Visualizations\n\n')
        f.write('The following visualizations have been generated:\n\n')
        f.write('1. **Success Rate Over Time**: Shows how the success rate changes over the test period\n')
        f.write('2. **Test Duration Over Time**: Shows how test execution time varies\n')
        f.write('3. **Success Rate by Hour of Day**: Identifies if certain times of day have more failures\n')
        if stats['error_types']:
            f.write('4. **Error Type Distribution**: Breakdown of different types of errors encountered\n')
        f.write('5. **Cumulative Run Count and Success Rate**: Shows overall progress and success trend\n')
        f.write('6. **Time Between Test Runs**: Shows the interval between test runs\n\n')
        
        f.write('## Recommendations\n\n')
        
        # Add recommendations based on the analysis
        if stats['success_rate'] < 90:
            f.write('- **Investigate Failures**: The success rate is below 90%, suggesting significant stability issues\n')
        
        if stats['max_duration'] > 2 * stats['avg_duration']:
            f.write('- **Optimize Performance**: Some test runs are taking significantly longer than average\n')
        
        # Add error-specific recommendations
        if stats['error_types'].get('Timeout Error', 0) > 0:
            f.write('- **Address Timeout Issues**: Consider increasing timeout thresholds or optimizing slow operations\n')
        
        if stats['error_types'].get('Element Not Found', 0) > 0:
            f.write('- **Improve Selectors**: Update element selectors that are failing to find elements\n')
        
        if stats['error_types'].get('Network Error', 0) > 0:
            f.write('- **Check Network Stability**: Network-related errors suggest connectivity issues\n')

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-results-json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    if not os.path.exists(results_file):
        print(f"Error: File '{results_file}' not found.")
        sys.exit(1)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(results_file), 'analysis')
    
    # Load and analyze results
    results = load_results(results_file)
    stats = analyze_results(results)
    df = create_dataframe(results)
    
    # Generate visualizations and report
    generate_visualizations(df, stats, output_dir)
    generate_report(stats, output_dir)
    
    print(f"Analysis complete. Results saved to {output_dir}")
    print(f"Summary: {stats['successful_runs']}/{stats['total_runs']} successful ({stats['success_rate']:.2f}% success rate)")

if __name__ == "__main__":
    main()

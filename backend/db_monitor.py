#!/usr/bin/env python3
"""
Database Query Performance Monitor
Utility script for analyzing database query performance and generating reports.
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import argparse

class DatabaseQueryAnalyzer:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.query_log_file = os.path.join(log_dir, "database_queries.log")
        self.slow_query_log_file = os.path.join(log_dir, "slow_queries.log")
        self.error_query_log_file = os.path.join(log_dir, "error_queries.log")
        self.performance_log_file = os.path.join(log_dir, "performance_metrics.log")
    
    def parse_query_logs(self, hours_back: int = 24) -> List[Dict]:
        """Parse query logs and extract performance data"""
        if not os.path.exists(self.query_log_file):
            print(f"Query log file not found: {self.query_log_file}")
            return []
        
        queries = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        with open(self.query_log_file, 'r') as f:
            for line in f:
                try:
                    # Parse log line format: timestamp - name - level - message
                    parts = line.strip().split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        level = parts[2]
                        message = parts[3]
                        
                        # Parse timestamp
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        
                        if timestamp < cutoff_time:
                            continue
                        
                        # Extract query duration and SQL
                        duration_match = re.search(r'Query executed in ([\d.]+)s: (.+)', message)
                        if duration_match:
                            duration = float(duration_match.group(1))
                            sql = duration_match.group(2)
                            
                            queries.append({
                                'timestamp': timestamp,
                                'duration': duration,
                                'sql': sql,
                                'level': level
                            })
                except Exception as e:
                    print(f"Error parsing log line: {line.strip()} - {e}")
        
        return queries
    
    def analyze_performance(self, hours_back: int = 24) -> Dict:
        """Analyze query performance over the specified time period"""
        queries = self.parse_query_logs(hours_back)
        
        if not queries:
            return {"error": "No queries found in the specified time period"}
        
        # Calculate statistics
        durations = [q['duration'] for q in queries]
        total_queries = len(queries)
        total_time = sum(durations)
        avg_time = total_time / total_queries
        max_time = max(durations)
        min_time = min(durations)
        
        # Categorize queries by duration
        slow_queries = [q for q in queries if q['duration'] > 0.1]
        very_slow_queries = [q for q in queries if q['duration'] > 0.5]
        
        # Analyze query patterns
        sql_patterns = Counter()
        for query in queries:
            # Extract table names and operation types
            sql = query['sql'].upper()
            if 'SELECT' in sql:
                sql_patterns['SELECT'] += 1
            if 'INSERT' in sql:
                sql_patterns['INSERT'] += 1
            if 'UPDATE' in sql:
                sql_patterns['UPDATE'] += 1
            if 'DELETE' in sql:
                sql_patterns['DELETE'] += 1
        
        # Time-based analysis
        hourly_stats = defaultdict(list)
        for query in queries:
            hour = query['timestamp'].replace(minute=0, second=0, microsecond=0)
            hourly_stats[hour].append(query['duration'])
        
        hourly_averages = {
            hour.isoformat(): sum(durations) / len(durations)
            for hour, durations in hourly_stats.items() if durations
        }
        
        return {
            "summary": {
                "total_queries": total_queries,
                "total_time": round(total_time, 4),
                "average_time": round(avg_time, 4),
                "max_time": round(max_time, 4),
                "min_time": round(min_time, 4),
                "slow_queries_count": len(slow_queries),
                "very_slow_queries_count": len(very_slow_queries)
            },
            "query_types": dict(sql_patterns),
            "hourly_averages": hourly_averages,
            "slowest_queries": sorted(queries, key=lambda x: x['duration'], reverse=True)[:10]
        }
    
    def generate_report(self, hours_back: int = 24, output_file: str | None = None) -> str:
        """Generate a comprehensive performance report"""
        analysis = self.analyze_performance(hours_back)
        
        if "error" in analysis:
            return f"Error: {analysis['error']}"
        
        report = []
        report.append("=" * 60)
        report.append("DATABASE QUERY PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Period: Last {hours_back} hours")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary section
        summary = analysis["summary"]
        report.append("PERFORMANCE SUMMARY:")
        report.append("-" * 30)
        report.append(f"Total Queries: {summary['total_queries']}")
        report.append(f"Total Execution Time: {summary['total_time']}s")
        report.append(f"Average Query Time: {summary['average_time']}s")
        report.append(f"Fastest Query: {summary['min_time']}s")
        report.append(f"Slowest Query: {summary['max_time']}s")
        report.append(f"Slow Queries (>100ms): {summary['slow_queries_count']}")
        report.append(f"Very Slow Queries (>500ms): {summary['very_slow_queries_count']}")
        report.append("")
        
        # Query types section
        report.append("QUERY TYPE DISTRIBUTION:")
        report.append("-" * 30)
        for query_type, count in analysis["query_types"].items():
            percentage = (count / summary['total_queries']) * 100
            report.append(f"{query_type}: {count} ({percentage:.1f}%)")
        report.append("")
        
        # Slowest queries section
        report.append("TOP 10 SLOWEST QUERIES:")
        report.append("-" * 30)
        for i, query in enumerate(analysis["slowest_queries"], 1):
            report.append(f"{i}. {query['duration']:.4f}s - {query['sql'][:100]}...")
        report.append("")
        
        # Hourly performance section
        report.append("HOURLY AVERAGE PERFORMANCE:")
        report.append("-" * 30)
        for hour, avg_time in sorted(analysis["hourly_averages"].items()):
            report.append(f"{hour}: {avg_time:.4f}s average")
        
        report_text = "\n".join(report)
        
        if output_file is not None:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text
    
    def get_slow_queries(self, min_duration: float = 0.1) -> List[Dict]:
        """Get all queries slower than the specified duration"""
        queries = self.parse_query_logs()
        return [q for q in queries if q['duration'] >= min_duration]
    
    def export_json(self, hours_back: int = 24, output_file: str | None = None) -> str:
        """Export analysis data as JSON"""
        analysis = self.analyze_performance(hours_back)
        
        if output_file is not None:
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"JSON export saved to: {output_file}")
        
        return json.dumps(analysis, indent=2, default=str)

def main():
    parser = argparse.ArgumentParser(description="Database Query Performance Analyzer")
    parser.add_argument("--hours", type=int, default=24, help="Hours to analyze (default: 24)")
    parser.add_argument("--output", type=str, help="Output file for report")
    parser.add_argument("--json", action="store_true", help="Export as JSON")
    parser.add_argument("--slow-only", type=float, help="Show only queries slower than specified seconds")
    
    args = parser.parse_args()
    
    analyzer = DatabaseQueryAnalyzer()
    
    if args.slow_only:
        slow_queries = analyzer.get_slow_queries(args.slow_only)
        print(f"Found {len(slow_queries)} queries slower than {args.slow_only}s:")
        for query in slow_queries:
            print(f"  {query['duration']:.4f}s - {query['sql'][:100]}...")
    elif args.json:
        output_file = args.output or f"db_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.export_json(args.hours, output_file)
    else:
        output_file = args.output or f"db_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report = analyzer.generate_report(args.hours, output_file)
        print(report)

if __name__ == "__main__":
    main()
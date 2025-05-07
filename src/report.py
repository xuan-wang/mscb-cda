import matplotlib.pyplot as plt
from datetime import datetime

def generate_markdown_report(portfolio, metrics, plot_filename="portfolio_analysis.png"):
    """Generate a markdown report with metrics and embedded plot"""
    
    # Create markdown content
    report = f"""# Portfolio Analysis Report
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Performance Metrics

### Final Portfolio Values
"""
    
    # Add metrics for each strategy
    for strategy in metrics:
        report += f"""
#### Strategy: {strategy}
- Total Cash Contributions: ${metrics[strategy]['total_contributions']:,.2f}
- Final Total Assets: ${metrics[strategy]['final_value']:,.2f}
- Money-weighted Return: {metrics[strategy]['money_weighted_return']:.2%}
- Sharpe Ratio: {metrics[strategy]['sharpe_ratio']:.2f}
- Time-weighted CAGR: {metrics[strategy]['cagr']:.2%}
- Maximum Drawdown: {metrics[strategy]['max_drawdown']:.2%}
"""

    # Add plot reference
    report += f"""
## Portfolio Analysis Charts
![Portfolio Analysis]({plot_filename})
"""
    
    # Write report to file
    try:
        with open("reports/analysis_report.md", "w") as f:
            f.write(report)
    except Exception as e:
        print(f"Error writing report: {str(e)}")
        return None

    return report
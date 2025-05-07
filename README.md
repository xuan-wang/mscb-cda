# README.md

# Trading Backtest Tool

A backtesting tool for quantitative trading strategies with monthly capital contributions.

## Features

- Monthly capital contribution simulation
  - Configurable initial investment
  - Regular monthly contributions
- Multiple strategy comparison
- Performance metrics calculation:
  - Total cash contributions
  - Final total assets
  - Money-weighted returns (IRR)
  - Sharpe ratio
  - Time-weighted CAGR
  - Maximum drawdown
- Visual analysis with four-panel charts:
  - Cash-only portfolio value
  - Strategy total values comparison
  - Time-weighted returns
  - Asset price history
- Markdown report generation

## Project Structure

```
trading-backtest/
├── src/
│   ├── main.py          # Main entry point
│   ├── backtester.py    # Backtesting engine
│   ├── portfolio.py     # Portfolio management
│   ├── metrics.py       # Performance metrics calculation
│   ├── plotting.py      # Visualization functions
│   └── report.py        # Report generation
├── data/
│   ├── prices.csv       # Asset price history
│   └── strategies/      # Strategy trade signals
├── reports/             # Generated reports
└── tests/              # Unit tests
```

## Input Data Format

### prices.csv
```csv
Date,Close
2024-01-01,6511.34
2024-01-02,6575.80
...
```

### strategies/strategy_name.csv
```csv
Date,Amount
2024-01-15,1000  # Buy $1000 worth of asset
2024-02-01,500   # Buy $500 worth of asset
...
```

Note: Amount represents the dollar value to invest, not the number of shares.

## Usage

1. Prepare your input data:
   - Place price history in `data/prices.csv`
   - Add strategy files in `data/strategies/`

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backtest:
```bash
python src/main.py
```

4. View results:
   - Performance metrics in `reports/analysis_report.md`
   - Visual analysis in `reports/portfolio_analysis.png`

## Requirements

- Python 3.8+
- numpy>=1.21.0
- pandas>=1.5.0
- matplotlib>=3.5.0
- scipy>=1.9.0
- numpy-financial>=1.0.0
- seaborn>=0.11.0

## Testing

Run the tests using:
```bash
python -m pytest tests/
```
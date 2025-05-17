import pandas as pd
from pathlib import Path
from backtester import Backtester
from portfolio import Portfolio
from metrics import PerformanceMetrics
from plotting import PortfolioVisualizer
from report import generate_markdown_report
import logging

logger = logging.getLogger(__name__)

def main():
    # Create necessary directories
    Path("reports").mkdir(exist_ok=True)
    Path("data/strategies").mkdir(parents=True, exist_ok=True)

    # Initialize the portfolio with monthly contribution settings
    initial_amount = 30000
    monthly_contribution = 1000
    portfolio = Portfolio(initial_amount, monthly_contribution)

    # Load and validate daily closing prices
    try:
        prices = pd.read_csv('data/prices.csv', parse_dates=['Date'], index_col='Date')
        prices = prices.sort_index()  # Ensure data is sorted by date
    except FileNotFoundError:
        logger.error("Error: prices.csv not found in data directory")
        return
    except Exception as e:
        logger.error(f"Error loading prices data: {e}")
        return

    # Initialize components
    backtester = Backtester(portfolio, prices)
    metrics_calculator = PerformanceMetrics()
    visualizer = PortfolioVisualizer()

    # Load strategies and run backtesting
    strategy_files = list(Path("data/strategies").glob("*.csv"))
    strategies = [f.stem for f in strategy_files]  # 已经从文件名中获取策略名

    if not strategies:
        logger.warning("No strategy files found in data/strategies directory")
        return

    for strategy in strategies:
        try:
            strategy_data = pd.read_csv(
                f'data/strategies/{strategy}.csv', 
                parse_dates=['Date']
            )
            strategy_data = strategy_data.sort_values('Date')
            backtester.run_backtest(strategy_data, strategy)
        except Exception as e:
            logger.error(f"Error processing strategy {strategy}: {e}")
            continue

    # Calculate performance metrics using backtester results
    metrics = metrics_calculator.calculate_metrics(backtester.get_all_results(), portfolio)

    # Get backtest results
    strategy_results = backtester.get_all_results()
    if not strategy_results:
        logger.error("No strategy results available")
        return

    # Get dates from first strategy (all strategies should have same dates)
    dates = strategy_results[list(strategy_results.keys())[0]]['dates']

    # Create DataFrames for visualization
    asset_values_df = pd.DataFrame({
        strategy: pd.Series(
            data['portfolio_values'],  # This contains cash + position values
            index=data['dates']
        )
        for strategy, data in strategy_results.items()
    })

    returns_df = pd.DataFrame({
        strategy: pd.Series(
            data['returns'],
            index=data['dates']
        )
        for strategy, data in strategy_results.items()
    })

    # Get deposits history for cash-only portfolio visualization
    deposits_df = portfolio.get_contribution_history()

    # Generate plots
    plot_filename = "portfolio_analysis.png"
    save_path = f"reports/{plot_filename}"

    # Add debug logging
    logger.debug("Creating visualization with:")
    for strategy in strategy_results:
        logger.debug(f"{strategy} final values:")
        logger.debug(f"  Cash: {strategy_results[strategy]['cash_values'][-1]:.2f}")
        logger.debug(f"  Position: {strategy_results[strategy]['position_values'][-1]:.2f}")
        logger.debug(f"  Total: {strategy_results[strategy]['portfolio_values'][-1]:.2f}")

    visualizer.create_analysis_plots(
        deposits=deposits_df,
        asset_values=asset_values_df,
        returns=returns_df,
        prices=prices,
        strategies=strategies,
        save_path=save_path
    )

    # Only generate report if plots were created successfully
    report = generate_markdown_report(portfolio, metrics)
    if report:
        logger.info("Backtesting completed. Report generated at reports/analysis_report.md")
    else:
        logger.error("Failed to generate report")

if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, portfolio, prices):
        """Initialize backtester with portfolio and price data"""
        self.portfolio = portfolio
        self.prices = prices.copy()  # Make a copy to avoid modifications
        self.strategies = {}
        self.trading_days = prices.index  # Use all price dates as trading days

    def run_backtest(self, strategy_data: pd.DataFrame, strategy_name: str) -> None:
        """Run backtest for a single strategy"""
        try:
            # Validate and prepare input data
            if strategy_data.empty:
                raise ValueError(f"Empty strategy data for {strategy_name}")
            
            strategy_data = strategy_data.copy()  # Make a copy to avoid modifications
            strategy_data['Date'] = pd.to_datetime(strategy_data['Date'])
            strategy_data.set_index('Date', inplace=True)
            
            # Initialize strategy and data validation
            self.portfolio.initialize_strategy(strategy_name)
            
            # Initialize results storage
            self.strategies[strategy_name] = {
                'portfolio_values': [],  # Will store total value (cash + positions)
                'position_values': [],   # Will store only position values
                'cash_values': [],       # Will store only cash values
                'returns': [],
                'dates': []
            }
            
            # Initialize tracking variables
            prev_value = self.portfolio.initial_amount  # Start with initial cash
            
            # Process each trading day
            for current_date in self.trading_days:
                try:
                    # Handle monthly contribution
                    if current_date.day == 1:
                        pre_contrib_value = self.portfolio.calculate_value(
                            self.prices.loc[current_date, 'Close'],
                            strategy_name
                        )
                        self.portfolio.add_monthly_contribution(current_date)
                    
                    # Execute trades if any
                    if current_date in strategy_data.index:
                        trade_amount = strategy_data.loc[current_date, 'Amount']
                        current_price = self.prices.loc[current_date, 'Close']
                        try:
                            self.portfolio.execute_trade(
                                amount=trade_amount,
                                date=current_date,
                                strategy_name=strategy_name,
                                price=current_price
                            )
                        except ValueError as e:
                            logger.warning(f"Trade skipped for {strategy_name} on {current_date}: {str(e)}")
                    
                    # Calculate current values
                    current_price = self.prices.loc[current_date, 'Close']
                    position_value = self.portfolio.positions[strategy_name] * current_price
                    cash_value = self.portfolio.strategy_cash[strategy_name]
                    current_total_value = position_value + cash_value
                    
                    # Calculate return (handling contribution days specially)
                    if current_date.day == 1 and len(self.strategies[strategy_name]['dates']) > 0:
                        daily_return = (current_total_value - self.portfolio.monthly_contribution) / pre_contrib_value - 1
                    else:
                        daily_return = (current_total_value / prev_value - 1) if prev_value > 0 else 0
                    
                    # Store all values
                    self.strategies[strategy_name]['dates'].append(current_date)
                    self.strategies[strategy_name]['portfolio_values'].append(current_total_value)
                    self.strategies[strategy_name]['position_values'].append(position_value)
                    self.strategies[strategy_name]['cash_values'].append(cash_value)
                    self.strategies[strategy_name]['returns'].append(daily_return)
                    
                    prev_value = current_total_value
                    
                    logger.debug(
                        f"{strategy_name} on {current_date}: "
                        f"Cash={cash_value:.2f}, "
                        f"Position={position_value:.2f}, "
                        f"Total={current_total_value:.2f}"
                    )
                    
                except Exception as day_error:
                    logger.error(f"Error on {current_date} for {strategy_name}: {str(day_error)}")
                    continue
            
            # Convert lists to numpy arrays
            for key in ['portfolio_values', 'position_values', 'cash_values', 'returns']:
                self.strategies[strategy_name][key] = np.array(self.strategies[strategy_name][key])
            self.strategies[strategy_name]['dates'] = pd.DatetimeIndex(self.strategies[strategy_name]['dates'])
            
        except Exception as e:
            logger.error(f"Error in backtesting {strategy_name}: {str(e)}")
            raise

    def get_strategy_results(self, strategy_name):
        """
        Get results for a specific strategy
        
        Args:
            strategy_name: String identifier for the strategy
            
        Returns:
            dict containing strategy results
        """
        return self.strategies.get(strategy_name)

    def get_all_results(self):
        """Get results for all strategies with aligned dates"""
        return {
            strategy_name: {
                'portfolio_values': data['portfolio_values'],
                'returns': data['returns'],
                'dates': data['dates'],
                'cash_values': data['cash_values'],
                'position_values': data['position_values']
            }
            for strategy_name, data in self.strategies.items()
        }
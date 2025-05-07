import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Portfolio:
    def __init__(self, initial_amount: float, monthly_contribution: float):
        """Initialize portfolio with initial amount and monthly contribution"""
        self.initial_amount = initial_amount
        self.monthly_contribution = monthly_contribution
        self.positions = {}  # Strategy positions
        self.strategy_cash = {}  # Strategy cash balances
        self.strategy_contributions = {}  # Track contributions per strategy
        self.contributions = []  # Track overall contributions
        self.last_contribution_dates = {}  # Track last contribution date per strategy

    def initialize_strategy(self, strategy_name: str) -> None:
        """Initialize a new strategy with initial cash"""
        if strategy_name not in self.strategy_cash:
            logger.info(f"Initializing strategy: {strategy_name}")
            self.positions[strategy_name] = 0.0
            self.strategy_cash[strategy_name] = self.initial_amount
            self.strategy_contributions[strategy_name] = []
            self.last_contribution_dates[strategy_name] = None

    def execute_trade(self, amount: float, date: datetime, strategy_name: str, price: float) -> None:
        """
        Execute a trade for a specific strategy
        
        Args:
            amount: Dollar amount to invest
            date: Trade date
            strategy_name: Strategy identifier
            price: Asset price on trade date
        """
        if strategy_name not in self.strategy_cash:
            raise ValueError(f"Strategy {strategy_name} not initialized")
        
        if amount > self.strategy_cash[strategy_name]:
            raise ValueError(f"Insufficient cash for trade in {strategy_name}: {amount}")
        
        # Calculate shares to buy based on dollar amount
        shares = amount / price
        
        # Update cash and positions
        self.strategy_cash[strategy_name] -= amount
        self.positions[strategy_name] += shares
        
        logger.debug(
            f"Trade executed for {strategy_name} on {date}: "
            f"Amount=${amount:.2f}, "
            f"Price=${price:.2f}, "
            f"Shares={shares:.4f}"
        )

    def add_monthly_contribution(self, date: datetime) -> None:
        """Add monthly contribution to each strategy independently"""
        for strategy_name in self.strategy_cash:
            # Check if this strategy needs a contribution this month
            last_date = self.last_contribution_dates[strategy_name]
            if (last_date is None or
                (date.year, date.month) > (last_date.year, last_date.month)):
                
                # Add contribution to this strategy's cash
                self.strategy_cash[strategy_name] += self.monthly_contribution
                
                # Record contribution for this strategy
                self.strategy_contributions[strategy_name].append({
                    'Date': date,
                    'amount': self.monthly_contribution,
                    'cumulative': (self.initial_amount + 
                                 len(self.strategy_contributions[strategy_name]) * 
                                 self.monthly_contribution)
                })
                
                # Also record in overall contributions (only once per month)
                if len(self.contributions) == 0 or date > self.contributions[-1]['Date']:
                    self.contributions.append({
                        'Date': date,
                        'amount': self.monthly_contribution,
                        'cumulative': (self.initial_amount + 
                                     len(self.contributions) * 
                                     self.monthly_contribution)
                    })
                
                self.last_contribution_dates[strategy_name] = date

    def calculate_value(self, current_price: float, strategy_name: str) -> float:
        """
        Calculate total value for a strategy including both positions and cash
        
        Args:
            current_price: Current asset price
            strategy_name: Strategy identifier
        
        Returns:
            float: Total value (position value + remaining cash)
        """
        if strategy_name not in self.positions:
            raise ValueError(f"Strategy {strategy_name} not initialized")
            
        # Calculate position value
        position_value = self.positions[strategy_name] * current_price
        
        # Add remaining cash
        total_value = position_value + self.strategy_cash[strategy_name]
        
        logger.debug(
            f"Strategy: {strategy_name} - "
            f"Position Value: {position_value:.2f}, "
            f"Cash: {self.strategy_cash[strategy_name]:.2f}, "
            f"Total: {total_value:.2f}"
        )
        
        return total_value

    def get_contribution_history(self) -> pd.DataFrame:
        """Get contribution history as DataFrame"""
        if not self.contributions:
            return pd.DataFrame(columns=['Date', 'amount', 'cumulative'])
            
        df = pd.DataFrame(self.contributions)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        return df

    def get_strategy_contribution_history(self, strategy_name: str) -> pd.DataFrame:
        """Get contribution history for a specific strategy"""
        if strategy_name not in self.strategy_contributions:
            return pd.DataFrame(columns=['Date', 'amount', 'cumulative'])
            
        df = pd.DataFrame(self.strategy_contributions[strategy_name])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        return df
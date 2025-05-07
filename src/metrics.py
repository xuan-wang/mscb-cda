import numpy as np
import numpy_financial as npf  # Add this import
import pandas as pd
from typing import Dict, List, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Class to handle all performance metric calculations"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize with risk-free rate
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.daily_rf_rate = (1 + risk_free_rate) ** (1/252) - 1

    def calculate_metrics(self, strategy_results: Dict, portfolio) -> Dict:
        """Calculate performance metrics for each strategy"""
        metrics = {}
        
        # Calculate total contributions
        total_contributions = portfolio.initial_amount
        if portfolio.contributions:
            total_contributions += sum(c['amount'] for c in portfolio.contributions)
        
        for strategy_name, data in strategy_results.items():
            metrics[strategy_name] = {
                'total_contributions': total_contributions,  # Add total contributions
                'final_value': data['portfolio_values'][-1],
                'money_weighted_return': self._calculate_irr(portfolio, data['portfolio_values'][-1], data['dates'][-1]),
                'sharpe_ratio': self._calculate_sharpe_ratio(data['returns']),
                'cagr': self._calculate_cagr(data['portfolio_values'], data['dates']),
                'max_drawdown': self._calculate_max_drawdown(data['portfolio_values'])
            }
        
        return metrics

    def _calculate_strategy_metrics(self, portfolio, strategy_name: str, data: Dict) -> Dict[str, float]:
        """Calculate metrics for a single strategy"""
        portfolio_values = data['portfolio_values']
        returns = data['returns']
        dates = data['dates']
        
        metrics = {
            'final_assets': portfolio_values[-1],
            'money_weighted_return': self._calculate_irr(portfolio, portfolio_values[-1], dates[-1]),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'time_weighted_cagr': self._calculate_cagr(portfolio_values, dates),
            'max_drawdown': self._calculate_max_drawdown(portfolio_values)
        }
        
        return metrics

    def _calculate_irr(self, portfolio, final_value: float, end_date: datetime) -> float:
        """
        Calculate money-weighted return using IRR
        """
        try:
            if not portfolio.contributions:
                return np.nan
                
            # Create cashflows array (negative for contributions, positive for final value)
            cashflows = [-c['amount'] for c in portfolio.contributions]
            cashflows.append(final_value)
            cashflows = np.array(cashflows)
            
            # Calculate IRR using numpy_financial
            irr = npf.irr(cashflows)
            
            # Convert to annual rate and handle edge cases
            if np.isnan(irr) or np.isinf(irr):
                return 0.0
                
            # Convert to percentage
            annual_rate = (1 + irr) ** 12 - 1
            
            logger.debug(f"IRR calculation - Cashflows: {cashflows}, IRR: {irr}, Annual: {annual_rate}")
            
            return annual_rate
            
        except Exception as e:
            logger.error(f"Error calculating IRR: {str(e)}")
            return np.nan

    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Calculate annualized Sharpe ratio"""
        if len(returns) <= 1:
            return np.nan
            
        excess_returns = returns - self.daily_rf_rate
        return np.sqrt(252) * np.mean(excess_returns) / np.std(returns, ddof=1)

    def _calculate_cagr(self, values: np.ndarray, dates: pd.DatetimeIndex) -> float:
        """Calculate time-weighted CAGR"""
        days = (dates[-1] - dates[0]).days
        if days > 0:
            return (values[-1] / values[0]) ** (365/days) - 1
        return np.nan

    def _calculate_max_drawdown(self, values: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
            
        return max_dd

    def _get_empty_metrics(self) -> Dict[str, float]:
        """Return dictionary with NaN values for all metrics"""
        return {
            'final_assets': np.nan,
            'money_weighted_return': np.nan,
            'sharpe_ratio': np.nan,
            'time_weighted_cagr': np.nan,
            'max_drawdown': np.nan
        }

    def calculate_rolling_metrics(self, backtester, window: int = 252) -> Dict[str, Dict[str, pd.Series]]:
        """Calculate rolling performance metrics"""
        rolling_metrics = {}
        
        for strategy_name, data in backtester.get_all_results().items():
            returns = pd.Series(data['returns'], index=data['dates'])
            
            rolling_metrics[strategy_name] = {
                'rolling_sharpe': self._calculate_rolling_sharpe(returns, window),
                'rolling_volatility': returns.rolling(window).std() * np.sqrt(252),
                'rolling_return': (1 + returns).rolling(window).prod() - 1
            }
        
        return rolling_metrics

    def _calculate_rolling_sharpe(self, returns: pd.Series, window: int) -> pd.Series:
        """Calculate rolling Sharpe ratio"""
        return returns.rolling(window).apply(
            lambda x: np.sqrt(252) * x.mean() / x.std() if len(x) > 1 else np.nan
        )
import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from src.backtester import Backtester
from src.portfolio import Portfolio

class TestBacktester(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.initial_amount = 10000
        self.monthly_contribution = 1000
        self.portfolio = Portfolio(self.initial_amount, self.monthly_contribution)
        
        # Create sample price data
        self.prices = pd.DataFrame({
            'Close': [100.0, 101.0, 102.0, 103.0],
            'Date': pd.date_range(start='2023-01-01', periods=4, freq='D')
        }).set_index('Date')
        
        self.backtester = Backtester(self.portfolio, self.prices)

    def test_strategy_initialization(self):
        """Test strategy initialization"""
        strategy_data = pd.DataFrame({
            'Date': ['2023-01-02'],
            'Amount': [1000]
        })
        self.backtester.run_backtest(strategy_data, 'test_strategy')
        self.assertIn('test_strategy', self.backtester.strategies)

    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation with trades"""
        strategy_data = pd.DataFrame({
            'Date': ['2023-01-02'],
            'Amount': [1000]
        })
        self.backtester.run_backtest(strategy_data, 'test_strategy')
        results = self.backtester.get_all_results()
        
        self.assertIn('test_strategy', results)
        self.assertTrue(len(results['test_strategy']['portfolio_values']) > 0)

    def test_monthly_contribution(self):
        """Test monthly contribution handling"""
        strategy_data = pd.DataFrame({
            'Date': ['2023-02-01'],
            'Amount': [1000]
        })
        self.backtester.run_backtest(strategy_data, 'test_strategy')
        results = self.backtester.get_all_results()
        
        # Should include initial amount + monthly contribution
        self.assertGreaterEqual(
            results['test_strategy']['portfolio_values'][-1],
            self.initial_amount + self.monthly_contribution
        )

if __name__ == '__main__':
    unittest.main()
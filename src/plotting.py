import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PortfolioVisualizer:
    """Handles portfolio visualization and chart generation"""
    
    def __init__(self):
        """Initialize visualizer with figure settings"""
        self.figsize = (12, 16)
        self.title_fontsize = 20    # Main title font size
        self.subtitle_fontsize = 14  # Subplot titles font size
        self.label_fontsize = 12    # Axis labels font size

    def create_analysis_plots(self, 
                            deposits: pd.DataFrame,
                            asset_values: pd.DataFrame,
                            returns: pd.DataFrame,
                            prices: pd.DataFrame,
                            strategies: List[str],
                            save_path: str = 'reports/portfolio_analysis.png') -> None:
        """Create and save four-panel analysis plot"""
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(4, 1, figsize=self.figsize)
            
            # Add main title with larger font and more space
            fig.suptitle('Portfolio Analysis', 
                        fontsize=self.title_fontsize,
                        y=0.95,  # Move title higher
                        weight='bold')  # Make title bold

            # Plot all panels
            self._plot_contributions(deposits, axes[0])
            self._plot_portfolio_values(asset_values, strategies, axes[1])
            self._plot_time_weighted_returns(returns, strategies, axes[2])
            self._plot_asset_prices(prices, axes[3])

            # Adjust spacing between subplots
            plt.subplots_adjust(hspace=0.35)  # Increase space between subplots
            
            # Ensure directory exists and save plot
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating plots: {str(e)}")
            plt.close()
            return False

    @staticmethod
    def _format_currency_k(x, p):
        """Helper function to format currency in thousands"""
        if x >= 1e6:  # For values >= 1 million
            return f'${x/1e6:.1f}M'
        return f'${x/1000:.0f}K'

    def _plot_contributions(self, deposits: pd.DataFrame, ax):
        """Plot cumulative cash-only portfolio value"""
        if not deposits.empty:
            ax.plot(deposits.index, deposits['cumulative'], 
                   color='blue', label='Cash Only Portfolio', linewidth=2)
            ax.fill_between(deposits.index, deposits['cumulative'], 
                           alpha=0.15, color='blue')
            
            # Format y-axis to show thousands with K
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(self._format_currency_k)
            )
            
            ax.set_title('Cash-Only Portfolio Value', 
                        fontsize=self.subtitle_fontsize,
                        pad=15)  # Add some padding below title
            ax.set_ylabel('Portfolio Value', fontsize=self.label_fontsize)
            ax.tick_params(labelsize=self.label_fontsize)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

    def _plot_portfolio_values(self, asset_values: pd.DataFrame, strategies: List[str], ax):
        """Plot portfolio values for each strategy"""
        for strategy in strategies:
            ax.plot(
                asset_values.index, 
                asset_values[strategy],
                label=f'Strategy: {strategy}'  # 修改标签显示
            )
        
        # Format y-axis to show thousands with K
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(self._format_currency_k)
        )
        
        ax.set_title('Portfolio Total Values Over Time', 
                    fontsize=self.subtitle_fontsize,
                    pad=15)
        ax.set_ylabel('Portfolio Value', fontsize=self.label_fontsize)
        ax.tick_params(labelsize=self.label_fontsize)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _plot_time_weighted_returns(self, returns: pd.DataFrame, strategies: List[str], ax):
        """Plot time-weighted returns"""
        for strategy in strategies:
            # Calculate cumulative returns
            cumulative_returns = (1 + returns[strategy]).cumprod() - 1
            ax.plot(returns.index, cumulative_returns * 100,
                   label=f'Strategy: {strategy}')  # 修改标签显示
        
        ax.set_title('Time-weighted Returns', 
                    fontsize=self.subtitle_fontsize,
                    pad=15)
        ax.set_ylabel('Return (%)', fontsize=self.label_fontsize)
        ax.tick_params(labelsize=self.label_fontsize)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _plot_asset_prices(self, prices: pd.DataFrame, ax):
        """Plot asset prices"""
        ax.plot(prices.index, prices['Close'], 'k-', label='Asset Price')
        ax.set_title('Asset Price History', 
                    fontsize=self.subtitle_fontsize,
                    pad=15)
        ax.set_ylabel('Price', fontsize=self.label_fontsize)
        ax.tick_params(labelsize=self.label_fontsize)
        ax.grid(True)
        ax.legend()
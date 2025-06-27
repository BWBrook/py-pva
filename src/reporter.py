"""Reporting utilities for population viability analysis simulations.

This module defines the `Reporter` class, which produces summary tables
and visualisations from `SimulationResult` instances. Users can generate
plots of population trajectories and histograms of time to extinction.
"""

import pandas as pd
import matplotlib.pyplot as plt

from .simulation import SimulationResult


class Reporter:
    """Generate summary statistics and plots for simulation results.

    Args:
        result: The SimulationResult object containing data to report.
    """

    def __init__(self, result: SimulationResult) -> None:
        self.result = result

    def summary_table(self) -> pd.DataFrame:
        """Return a table summarising extinction outcomes across replicates."""
        return self.result.summary()

    def plot_trajectories(self, output_path: str, show_mean: bool = True) -> None:
        """Plot population trajectories by replicate and save to file.

        A line is drawn for each replicate's total population over
        generations. Optionally, the mean trajectory across replicates
        is superimposed.

        Args:
            output_path: File path to save the figure (e.g. 'traj.png').
            show_mean: Whether to overlay the mean trajectory.
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        for df in self.result.trajectories:
            ax.plot(df['generation'], df['total'], color='grey', alpha=0.3, linewidth=0.5)
        if show_mean:
            combined = pd.concat(self.result.trajectories)
            mean_df = combined.groupby('generation')['total'].mean().reset_index()
            ax.plot(mean_df['generation'], mean_df['total'], color='blue', linewidth=2, label='Mean total')
            ax.legend()
        ax.set_xlabel('Generation')
        ax.set_ylabel('Total population size')
        ax.set_title('Population trajectories')
        fig.tight_layout()
        fig.savefig(output_path)
        plt.close(fig)

    def plot_extinction_hist(self, output_path: str) -> None:
        """Plot a histogram of time to extinction across replicates.

        Args:
            output_path: File path to save the figure (e.g. 'extinction_hist.png').
        """
        times = [t for t in self.result.extinction_times if t < float('inf')]
        fig, ax = plt.subplots(figsize=(6, 4))
        if times:
            ax.hist(times, bins=20, color='salmon', edgecolor='black')
            ax.set_xlabel('Time to extinction')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of time to extinction')
        else:
            ax.text(0.5, 0.5, 'No extinctions observed.', ha='center', va='center')
            ax.axis('off')
        fig.tight_layout()
        fig.savefig(output_path)
        plt.close(fig)

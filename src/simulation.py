"""Simulation engine for two-sex population viability analyses.

This module contains the `Simulation` class, which orchestrates repeated
simulations of the population model, as well as a data class to store
results. Simulations can incorporate demographic and environmental
stochasticity, catastrophes, and carrying capacity.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import pandas as pd

from .vital_rates import VitalRates
from .population import Population
from .catastrophe import Catastrophe


@dataclass
class SimulationResult:
    """Data container for simulation results.

    Attributes:
        trajectories: A list of data frames, one per replicate, holding
            population sizes by generation and sex. Each frame has
            columns 'generation', 'female', 'male' and 'total'.
        extinction_times: List of times to extinction for each replicate.
        q_threshold: Quasi-extinction threshold used in the simulation.
    """

    trajectories: List[pd.DataFrame]
    extinction_times: List[float]
    q_threshold: int

    def summary(self) -> pd.DataFrame:
        """Return a summary table of extinction statistics.

        The table contains the number of replicates, count of extinctions,
        extinction probability, and mean and median times to extinction.
        """
        n_replicates = len(self.extinction_times)
        n_extinct = sum(1 for t in self.extinction_times if t < np.inf)
        extinction_probability = n_extinct / n_replicates if n_replicates else float('nan')
        times = [t for t in self.extinction_times if t < np.inf]
        mean_time = float(np.mean(times)) if times else float('nan')
        median_time = float(np.median(times)) if times else float('nan')
        return pd.DataFrame([
            {
                'replicates': n_replicates,
                'extinct': n_extinct,
                'extinction_probability': extinction_probability,
                'mean_time_to_extinction': mean_time,
                'median_time_to_extinction': median_time,
            }
        ])


class Simulation:
    """Manage execution of multiple population viability simulations.

    Parameters:
        vital_rates: VitalRates object specifying survival and fertility.
        initial_females: Initial female counts by age class.
        initial_males: Initial male counts by age class.
        catastrophe: Optional catastrophe event to include.
        carrying_capacity: Optional population ceiling.
        n_generations: Number of generations to simulate per replicate.
        q_threshold: Quasi-extinction threshold; simulation stops early
            when population size falls below or equals this value.
        n_replicates: Number of replicates to run.
        demo_noise: Whether to include demographic stochasticity.
        env_noise: Whether to include environmental stochasticity.
        seed: Optional random seed for reproducibility.
    """

    def __init__(
        self,
        vital_rates: VitalRates,
        initial_females: np.ndarray,
        initial_males: np.ndarray,
        catastrophe: Optional[Catastrophe] = None,
        carrying_capacity: Optional[int] = None,
        n_generations: int = 100,
        q_threshold: int = 50,
        n_replicates: int = 100,
        demo_noise: bool = True,
        env_noise: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        self.vital_rates = vital_rates
        self.initial_females = initial_females.astype(int)
        self.initial_males = initial_males.astype(int)
        self.catastrophe = catastrophe
        self.carrying_capacity = carrying_capacity
        self.n_generations = n_generations
        self.q_threshold = q_threshold
        self.n_replicates = n_replicates
        self.demo_noise = demo_noise
        self.env_noise = env_noise
        self.seed = seed

    def run(self) -> SimulationResult:
        """Run the population viability simulations.

        Returns:
            SimulationResult object containing trajectories and extinction statistics.
        """
        trajectories: List[pd.DataFrame] = []
        extinction_times: List[float] = []
        base_seed = self.seed if self.seed is not None else np.random.randint(0, 2**32 - 1)
        for replicate in range(self.n_replicates):
            np.random.seed((base_seed + replicate) % (2**32 - 1))
            pop = Population(
                female=self.initial_females.copy(),
                male=self.initial_males.copy(),
                carrying_capacity=self.carrying_capacity,
                reproduction_age=1,
                male_birth_prop=0.5,
            )
            records = []
            extinct_at: float = np.inf
            records.append(
                {
                    'generation': 0,
                    'female': int(pop.female.sum()),
                    'male': int(pop.male.sum()),
                    'total': pop.total_population(),
                }
            )
            for gen in range(1, self.n_generations + 1):
                pop.advance_generation(
                    self.vital_rates,
                    catastrophe=self.catastrophe,
                    demo_noise=self.demo_noise,
                    env_noise=self.env_noise,
                )
                total_size = pop.total_population()
                records.append(
                    {
                        'generation': gen,
                        'female': int(pop.female.sum()),
                        'male': int(pop.male.sum()),
                        'total': total_size,
                    }
                )
                if pop.is_extinct(self.q_threshold):
                    extinct_at = gen
                    break
            if extinct_at < np.inf and extinct_at < self.n_generations:
                for gen2 in range(extinct_at + 1, self.n_generations + 1):
                    records.append(
                        {
                            'generation': gen2,
                            'female': 0,
                            'male': 0,
                            'total': 0,
                        }
                    )
            df = pd.DataFrame(records)
            trajectories.append(df)
            extinction_times.append(extinct_at)
        return SimulationResult(trajectories=trajectories, extinction_times=extinction_times, q_threshold=self.q_threshold)

"""Catastrophic mortality events for population models.

This module defines the `Catastrophe` class, representing rare events
that reduce population numbers dramatically. The event is characterised
by its probability of occurrence per time step and the fraction of
individuals removed when it occurs.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class Catastrophe:
    """Represent a stochastic catastrophe causing mass mortality.

    Attributes:
        probability: Probability of the catastrophe occurring in a given
            generation. A value between zero and one.
        mortality_rate: Proportion of individuals removed if the event
            occurs. A value between zero and one.
    """

    probability: float
    mortality_rate: float

    def occurs(self) -> bool:
        """Return True if the catastrophe occurs in the current generation."""
        return np.random.random() < self.probability

    def apply(self, new_f: np.ndarray, new_m: np.ndarray, demo_noise: bool = True) -> None:
        """Apply the catastrophe to the given population arrays.

        If the catastrophe occurs, a fraction of individuals in each age
        class is removed according to the mortality rate. Demographic noise
        determines whether removal is stochastic (binomial sampling) or
        deterministic (scaling down by the survival fraction).

        Args:
            new_f: Array of female counts by age class. Modified in place.
            new_m: Array of male counts by age class. Modified in place.
            demo_noise: If True, perform binomial sampling for removals;
                otherwise, scale counts deterministically.
        """
        if self.occurs():
            for i in range(len(new_f)):
                if demo_noise:
                    new_f[i] = np.random.binomial(new_f[i], 1.0 - self.mortality_rate)
                    new_m[i] = np.random.binomial(new_m[i], 1.0 - self.mortality_rate)
                else:
                    new_f[i] = int(round(new_f[i] * (1.0 - self.mortality_rate)))
                    new_m[i] = int(round(new_m[i] * (1.0 - self.mortality_rate)))

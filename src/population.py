"""Population state and update functions for two-sex PVA models.

This module defines the `Population` class, encapsulating the counts of
female and male individuals across age classes. It supports advancing
population numbers through survival, reproduction, carrying capacity,
and catastrophic mortality events.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from .vital_rates import VitalRates
from .catastrophe import Catastrophe


@dataclass
class Population:
    """Represent the age-structured population of two sexes.

    Attributes:
        female: Array of female counts by age class.
        male: Array of male counts by age class.
        carrying_capacity: Optional maximum population size. If set,
            population numbers are scaled down when the total exceeds
            this limit.
        reproduction_age: Minimum age (inclusive) at which females
            reproduce. Age classes are indexed from zero.
        male_birth_prop: Proportion of births that are male. Defaults
            to 0.5 for equal sex ratio.
    """

    female: np.ndarray
    male: np.ndarray
    carrying_capacity: Optional[int] = None
    reproduction_age: int = 1
    male_birth_prop: float = 0.5

    def advance_generation(
        self,
        vital_rates: VitalRates,
        catastrophe: Optional[Catastrophe] = None,
        demo_noise: bool = True,
        env_noise: bool = True,
    ) -> None:
        """Advance the population by one generation.

        The update sequence is: apply environmental noise to vital rates;
        compute survival and update age classes; perform reproduction;
        apply catastrophe; enforce carrying capacity; and finally update
        the internal state of the population.

        Args:
            vital_rates: Vital rates for survival and reproduction.
            catastrophe: Optional catastrophe event applied after reproduction.
            demo_noise: If True, demographic stochasticity is included via
                binomial and Poisson distributions. If False, survivals and
                births are deterministic.
            env_noise: If True, environmental noise is applied to vital
                rates. If False, raw rates are used.
        """
        # Determine survival and fertility rates with environmental noise
        if env_noise:
            f_survival, m_survival, f_fertility, m_fertility = vital_rates.apply_environmental_noise()
        else:
            f_survival, m_survival, f_fertility, m_fertility = (
                vital_rates.female_survival,
                vital_rates.male_survival,
                vital_rates.female_fertility,
                vital_rates.male_fertility,
            )

        age_classes = len(self.female)
        new_f = np.zeros_like(self.female)
        new_m = np.zeros_like(self.male)

        # Survival: shift individuals from age i to i+1, keep max age class
        for i in range(age_classes - 1):
            if demo_noise:
                surv_f = np.random.binomial(self.female[i], f_survival[i])
                surv_m = np.random.binomial(self.male[i], m_survival[i])
            else:
                surv_f = int(round(self.female[i] * f_survival[i]))
                surv_m = int(round(self.male[i] * m_survival[i]))
            new_f[i + 1] += surv_f
            new_m[i + 1] += surv_m
        # Last age class survival
        if demo_noise:
            surv_f = np.random.binomial(self.female[-1], f_survival[-1])
            surv_m = np.random.binomial(self.male[-1], m_survival[-1])
        else:
            surv_f = int(round(self.female[-1] * f_survival[-1]))
            surv_m = int(round(self.male[-1] * m_survival[-1]))
        new_f[-1] += surv_f
        new_m[-1] += surv_m

        # Reproduction: iterate over females at or above reproduction age
        births = 0
        for i in range(self.reproduction_age, age_classes):
            n_females = new_f[i]
            rate = f_fertility[i]
            if demo_noise:
                births_i = np.random.poisson(n_females * rate)
            else:
                births_i = int(round(n_females * rate))
            births += births_i
        # Assign sexes to births
        if births > 0:
            if demo_noise:
                n_male_births = np.random.binomial(births, self.male_birth_prop)
            else:
                n_male_births = int(round(births * self.male_birth_prop))
            n_female_births = births - n_male_births
        else:
            n_female_births = 0
            n_male_births = 0
        # Age zero individuals are new births
        new_f[0] = n_female_births
        new_m[0] = n_male_births

        # Apply catastrophe
        if catastrophe is not None:
            catastrophe.apply(new_f, new_m, demo_noise=demo_noise)

        # Enforce carrying capacity via proportional scaling
        if self.carrying_capacity is not None:
            total = int(new_f.sum() + new_m.sum())
            if total > self.carrying_capacity and total > 0:
                ratio = self.carrying_capacity / float(total)
                if demo_noise:
                    scaled_f = np.array([
                        np.random.binomial(int(new_f[i]), ratio) for i in range(age_classes)
                    ])
                    scaled_m = np.array([
                        np.random.binomial(int(new_m[i]), ratio) for i in range(age_classes)
                    ])
                else:
                    scaled_f = (new_f * ratio).astype(int)
                    scaled_m = (new_m * ratio).astype(int)
                new_f = scaled_f
                new_m = scaled_m

        # Update state
        self.female = new_f
        self.male = new_m

    def total_population(self) -> int:
        """Return total population size across sexes."""
        return int(self.female.sum() + self.male.sum())

    def is_extinct(self, q_threshold: int) -> bool:
        """Return True if total population is less than or equal to q_threshold."""
        return self.total_population() <= q_threshold

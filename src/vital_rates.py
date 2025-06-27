"""Vital rates definitions for two-sex population models.

This module defines the `VitalRates` class, which encapsulates age-specific
survival and fertility rates for female and male individuals. Environmental
stochasticity can be applied to these rates by specifying standard
deviations. Demographic stochasticity is handled in the `Population` class.
"""

from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class VitalRates:
    """Represent age-specific survival and fertility rates for two sexes.

    Attributes:
        female_survival: One-dimensional array of survival probabilities for
            female individuals. Each element corresponds to an age class.
        male_survival: One-dimensional array of survival probabilities for
            male individuals. Each element corresponds to an age class.
        female_fertility: One-dimensional array of fertility rates for
            female individuals. Each element corresponds to an age class.
        male_fertility: One-dimensional array of fertility rates for male
            individuals. Each element corresponds to an age class. These
            rates are rarely used but provided for completeness.
        env_sd_survival: Standard deviation of environmental noise applied to
            survival probabilities. A value of zero implies no noise.
        env_sd_fertility: Standard deviation of environmental noise applied to
            fertility rates. A value of zero implies no noise.
    """

    female_survival: np.ndarray
    male_survival: np.ndarray
    female_fertility: np.ndarray
    male_fertility: np.ndarray
    env_sd_survival: float = 0.0
    env_sd_fertility: float = 0.0

    def apply_environmental_noise(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate survival and fertility arrays with environmental noise.

        This method multiplies each age-specific rate by a random normal
        deviate with mean one and the specified standard deviation. Survival
        probabilities are clipped between zero and one to avoid invalid
        probabilities. Fertility rates are clipped below at zero.

        Returns:
            A tuple containing four arrays: noisy female survival,
            noisy male survival, noisy female fertility, and noisy male
            fertility.
        """
        if self.env_sd_survival > 0:
            f_survival_noise = np.random.normal(1.0, self.env_sd_survival, size=self.female_survival.shape)
            m_survival_noise = np.random.normal(1.0, self.env_sd_survival, size=self.male_survival.shape)
            f_survival = np.clip(self.female_survival * f_survival_noise, 0.0, 1.0)
            m_survival = np.clip(self.male_survival * m_survival_noise, 0.0, 1.0)
        else:
            f_survival = self.female_survival
            m_survival = self.male_survival
        if self.env_sd_fertility > 0:
            f_fertility_noise = np.random.normal(1.0, self.env_sd_fertility, size=self.female_fertility.shape)
            m_fertility_noise = np.random.normal(1.0, self.env_sd_fertility, size=self.male_fertility.shape)
            f_fertility = np.clip(self.female_fertility * f_fertility_noise, 0.0, None)
            m_fertility = np.clip(self.male_fertility * m_fertility_noise, 0.0, None)
        else:
            f_fertility = self.female_fertility
            m_fertility = self.male_fertility
        return f_survival, m_survival, f_fertility, m_fertility

"""Pytest tests for the PVA simulator.

These tests verify deterministic behaviour of survival and reproduction
when demographic and environmental noise are disabled.
"""

import numpy as np

from src.vital_rates import VitalRates
from src.population import Population
from src.catastrophe import Catastrophe


def test_survival_deterministic() -> None:
    """Population should age correctly without births or noise."""
    initial_females = np.array([10, 0])
    initial_males = np.array([10, 0])
    survival = np.array([1.0, 1.0])
    fertility = np.array([0.0, 0.0])
    vr = VitalRates(survival, survival, fertility, fertility)
    pop = Population(initial_females.copy(), initial_males.copy())
    pop.advance_generation(vr, catastrophe=None, demo_noise=False, env_noise=False)
    assert pop.female[1] == 10
    assert pop.male[1] == 10
    assert pop.female[0] == 0
    assert pop.male[0] == 0
    pop.advance_generation(vr, catastrophe=None, demo_noise=False, env_noise=False)
    assert pop.female[1] == 10
    assert pop.male[1] == 10


def test_reproduction_deterministic() -> None:
    """Reproduction should produce deterministic births without noise."""
    initial_females = np.array([0, 10])
    initial_males = np.array([0, 10])
    survival = np.array([1.0, 1.0])
    fertility = np.array([0.0, 2.0])
    vr = VitalRates(survival, survival, fertility, fertility)
    pop = Population(initial_females.copy(), initial_males.copy(), reproduction_age=1)
    pop.advance_generation(vr, catastrophe=None, demo_noise=False, env_noise=False)
    assert pop.female[0] == 10
    assert pop.male[0] == 10
    assert pop.female[1] == 10
    assert pop.male[1] == 10


def test_catastrophe_deterministic() -> None:
    """Catastrophe should remove a fixed fraction deterministically."""
    initial_females = np.array([10, 10])
    initial_males = np.array([10, 10])
    survival = np.array([1.0, 1.0])
    fertility = np.array([0.0, 0.0])
    vr = VitalRates(survival, survival, fertility, fertility)
    cat = Catastrophe(probability=1.0, mortality_rate=0.5)
    pop = Population(initial_females.copy(), initial_males.copy())
    pop.advance_generation(vr, catastrophe=cat, demo_noise=False, env_noise=False)
    assert pop.female[1] + pop.male[1] == 10


def test_carrying_capacity_deterministic() -> None:
    """Carrying capacity should limit total population deterministically."""
    initial_females = np.array([50])
    initial_males = np.array([50])
    survival = np.array([1.0])
    fertility = np.array([0.0])
    vr = VitalRates(survival, survival, fertility, fertility)
    pop = Population(initial_females.copy(), initial_males.copy(), carrying_capacity=50)
    pop.advance_generation(vr, catastrophe=None, demo_noise=False, env_noise=False)
    assert pop.female.sum() + pop.male.sum() == 50


def test_parse_args_yaml(tmp_path) -> None:
    """CLI should load parameters from a YAML file."""
    import yaml
    from main import parse_args

    cfg = {
        'years': 5,
        'n_sim': 2,
        'female_survival': [0.5, 0.5],
        'male_survival': [0.5, 0.5],
        'female_fertility': [0.0, 0.0],
        'male_fertility': [0.0, 0.0],
        'initial_females': [10, 0],
        'initial_males': [10, 0],
    }
    path = tmp_path / 'cfg.yaml'
    path.write_text(yaml.safe_dump(cfg))
    args = parse_args(['--config', str(path)])
    assert args.years == 5
    assert args.n_sim == 2
    assert args.female_survival == '0.5,0.5'


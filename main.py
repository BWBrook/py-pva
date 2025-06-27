"""Command-line interface for the PVA simulator.

This script parses command-line arguments or a YAML configuration file to
configure and run the population viability analysis simulation.
Results are summarised and optionally saved to files. See README.md for
examples.
"""

import argparse
import sys
from typing import Optional
import yaml
import numpy as np

from src.vital_rates import VitalRates
from src.catastrophe import Catastrophe
from src.simulation import Simulation
from src.reporter import Reporter


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run a population viability analysis simulation with age structure and two sexes.'
    )
    parser.add_argument('--config', type=str, default=None, help='YAML file with simulation parameters.')
    parser.add_argument('--years', type=int, default=100, help='Number of generations to simulate.')
    parser.add_argument('--n-sim', type=int, default=100, help='Number of simulation replicates.')
    parser.add_argument('--q-threshold', type=int, default=50, help='Quasi-extinction threshold (population size).')
    parser.add_argument('--carrying-capacity', type=int, default=None, help='Ceiling carrying capacity.')
    parser.add_argument('--env-sd-survival', type=float, default=0.0, help='Environmental SD for survival rates.')
    parser.add_argument('--env-sd-fertility', type=float, default=0.0, help='Environmental SD for fertility rates.')
    parser.add_argument('--no-demo-noise', action='store_true', help='Disable demographic stochasticity.')
    parser.add_argument('--no-env-noise', action='store_true', help='Disable environmental stochasticity.')
    parser.add_argument('--catastrophe-prob', type=float, default=0.0, help='Probability of catastrophe per generation.')
    parser.add_argument('--catastrophe-mort', type=float, default=0.0, help='Mortality fraction when catastrophe occurs.')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility.')
    parser.add_argument('--plot-dir', type=str, default=None, help='Directory to save plots.')
    parser.add_argument('--female-survival', type=str, default='0.5,0.7,0.6,0.4,0.2', help='Comma-separated female survival rates.')
    parser.add_argument('--male-survival', type=str, default='0.5,0.7,0.6,0.4,0.2', help='Comma-separated male survival rates.')
    parser.add_argument('--female-fertility', type=str, default='0,2,2,1,0', help='Comma-separated female fertility rates.')
    parser.add_argument('--male-fertility', type=str, default='0,0,0,0,0', help='Comma-separated male fertility rates.')
    parser.add_argument('--initial-females', type=str, default='10,10,0,0,0', help='Initial female counts per age class.')
    parser.add_argument('--initial-males', type=str, default='10,10,0,0,0', help='Initial male counts per age class.')
    # First parse only known args to get config file
    args, remaining = parser.parse_known_args(argv)
    if args.config:
        with open(args.config, 'r') as fh:
            config_data = yaml.safe_load(fh) or {}
        for k, v in config_data.items():
            if isinstance(v, list):
                config_data[k] = ','.join(str(x) for x in v)
        parser.set_defaults(**config_data)
    # Now parse fully with potential overrides from CLI
    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> None:
    args = parse_args(argv)
    # Parse comma-separated lists
    female_survival = np.array([float(x) for x in args.female_survival.split(',')])
    male_survival = np.array([float(x) for x in args.male_survival.split(',')])
    female_fertility = np.array([float(x) for x in args.female_fertility.split(',')])
    male_fertility = np.array([float(x) for x in args.male_fertility.split(',')])
    initial_females = np.array([int(float(x)) for x in args.initial_females.split(',')])
    initial_males = np.array([int(float(x)) for x in args.initial_males.split(',')])
    n_age = len(female_survival)
    if not (
        len(male_survival) == n_age and len(female_fertility) == n_age and len(male_fertility) == n_age
        and len(initial_females) == n_age and len(initial_males) == n_age
    ):
        sys.exit('Error: All rate and initial count lists must have the same length.')
    vital_rates = VitalRates(
        female_survival=female_survival,
        male_survival=male_survival,
        female_fertility=female_fertility,
        male_fertility=male_fertility,
        env_sd_survival=args.env_sd_survival,
        env_sd_fertility=args.env_sd_fertility,
    )
    catastrophe = None
    if args.catastrophe_prob > 0 and args.catastrophe_mort > 0:
        catastrophe = Catastrophe(probability=args.catastrophe_prob, mortality_rate=args.catastrophe_mort)
    simulation = Simulation(
        vital_rates=vital_rates,
        initial_females=initial_females,
        initial_males=initial_males,
        catastrophe=catastrophe,
        carrying_capacity=args.carrying_capacity,
        n_generations=args.years,
        q_threshold=args.q_threshold,
        n_replicates=args.n_sim,
        demo_noise=not args.no_demo_noise,
        env_noise=not args.no_env_noise,
        seed=args.seed,
    )
    result = simulation.run()
    reporter = Reporter(result)
    summary = reporter.summary_table()
    print(summary.to_string(index=False))
    if args.plot_dir:
        import os
        os.makedirs(args.plot_dir, exist_ok=True)
        traj_path = os.path.join(args.plot_dir, 'trajectories.png')
        ext_path = os.path.join(args.plot_dir, 'extinction_hist.png')
        reporter.plot_trajectories(traj_path)
        reporter.plot_extinction_hist(ext_path)
        print(f'Plots saved to {args.plot_dir}')


if __name__ == '__main__':
    main()

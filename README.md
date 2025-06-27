# Population Viability Analysis Simulator

This repository contains a Python implementation of an age‑structured,
two‑sex population viability analysis (PVA) simulator. The package is
intended for conservation biology and teaching purposes. It provides a
command‑line interface and modular components for modelling survival,
reproduction, environmental noise, demographic noise, catastrophes and
carrying capacity.

## Features

- **Age structure** with arbitrary number of classes.
- **Two sexes**, allowing monitoring of the limiting sex.
- **Demographic and environmental stochasticity** for survival and
  fertility.
- **Catastrophic events** representing rare mass mortality episodes.
- **Carrying capacity** enforced via density‑dependent scaling.
- **Replicate simulations** with user‑defined number of generations and
  quasi‑extinction thresholds.
- **Summary tables and plots** for population trajectories and
  extinction times.

## Requirements

- Python 3.12 or later. The code has been tested under Python 3.11; if
  Python 3.12 is unavailable, the provided bootstrap script falls back
  to the default `python3`.
- A virtual environment tool such as `venv`.

## Installation

Clone this repository and run the bootstrap script to create a virtual
environment and install dependencies:

```bash
bash bootstrap_env.sh
source .venv/bin/activate
```

The bootstrap script installs dependencies listed in
`requirements.txt` using `uv pip` and produces a `requirements.lock`
file with pinned versions via `uv pip freeze`.

## Usage

After activating the virtual environment, run the simulator via
`main.py`:

```bash
python main.py --years 50 --n-sim 1000 --q-threshold 50 \
    --catastrophe-prob 0.1 --catastrophe-mort 0.5 \
    --env-sd-survival 0.1 --env-sd-fertility 0.1 \
    --carrying-capacity 500 --plot-dir results
```

See `python main.py --help` for a full list of options, including how
to customise survival and fertility rates, initial populations and
noise settings.

Parameters can also be provided in a YAML file using the `--config`
option:

```bash
python main.py --config example_params.yaml
```

The repository includes `example_params.yaml` with the default values as
a starting point.

## Testing

To run the tests with `pytest`, install the dependencies and execute:

```bash
pytest -q
```

All tests should pass. Linting can be performed with `ruff` if
available.

## Contributing

Contributions to extend the model (e.g. sensitivity analyses, density
regulation models) are welcome. Please follow the coding style and
provide tests for any new functionality.

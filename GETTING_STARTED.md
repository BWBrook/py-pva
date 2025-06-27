# Getting Started with the PVA Simulator

This guide walks you through setting up and using the population
viability analysis simulator.

1. **Setup the environment**

   Run the bootstrap script to create a virtual environment and install
   dependencies:

   ```bash
   bash bootstrap_env.sh
   source .venv/bin/activate
   ```

2. **Run a simple simulation**

   Execute the `main.py` script with default parameters:

   ```bash
   python main.py
   ```

   The script prints a summary table of extinction outcomes across
   replicates.

3. **Customise the model**

   You can customise vital rates, initial populations, noise levels and
   catastrophe settings via command‑line options. For example:

   ```bash
   python main.py --years 50 --n-sim 500 \
       --female-survival 0.6,0.7,0.5,0.3,0.1 \
       --female-fertility 0,1,2,1,0 \
       --initial-females 20,20,0,0,0 --initial-males 20,20,0,0,0 \
       --q-threshold 20 --carrying-capacity 200
   ```

   Use `--help` to list all available arguments.

4. **Generate plots**

   Specify `--plot-dir` to save population trajectory and extinction
   histogram plots:

   ```bash
   python main.py --plot-dir results
   ```

   This creates `trajectories.png` and `extinction_hist.png` in the
   `results` directory.

## Tips

- Set `--seed` to an integer for reproducible results.
- Use `--no-demo-noise` or `--no-env-noise` to disable stochasticity.
- To run large numbers of replicates efficiently, consider using the
  `joblib` library for parallelisation in future extensions.

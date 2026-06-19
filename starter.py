"""
Starter template: imports the core data-analysis stack and runs a quick
smoke test so you know the environment is wired up correctly.

Run it with:  python3 starter.py
"""

# --- Preliminary settings: import the core libraries ------------------------
import pandas as pd                # data analysis / DataFrames
import numpy as np                 # numerical operations
import matplotlib.pyplot as plt    # plotting
from lets_plot import *            # grammar-of-graphics plotting
import pingouin as pg              # statistical tests
from skimpy import skim            # summary statistic tables

# lets_plot needs to be set up once per session before plotting
LetsPlot.setup_html()


def smoke_test() -> None:
    """Build a tiny DataFrame and exercise each library once."""
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "group": rng.choice(["A", "B"], size=100),
        "x": rng.normal(0, 1, size=100),
        "y": rng.normal(1, 2, size=100),
    })

    # pandas / numpy
    print("DataFrame shape:", df.shape)
    print(df.head(), "\n")

    # skimpy: summary table
    skim(df)

    # pingouin: a simple statistical test (t-test between the two groups)
    ttest = pg.ttest(df.loc[df["group"] == "A", "y"],
                     df.loc[df["group"] == "B", "y"])
    print("\nWelch t-test (group A vs B on y):")
    print(ttest[["T", "dof", "p_val"]], "\n")

    print("Environment is ready. Happy analyzing!")


if __name__ == "__main__":
    smoke_test()

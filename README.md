# Data Analysis Workspace

A ready-to-go Python environment for data analysis projects.

## Setup

```bash
pip install -r requirements.txt
```

## The core stack

At the start of a Python session, import the libraries you'll reach for again
and again:

| Library      | Purpose                          |
|--------------|----------------------------------|
| `pandas`     | data analysis / DataFrames       |
| `numpy`      | numerical operations             |
| `matplotlib` | plotting                         |
| `lets_plot`  | grammar-of-graphics plotting     |
| `pingouin`   | statistical tests                |
| `skimpy`     | summary statistic tables         |

## Quick start

`starter.py` imports the whole stack and runs a smoke test (DataFrame, a
`skimpy` summary table, and a `pingouin` t-test) so you can confirm the
environment is wired up correctly:

```bash
python3 starter.py
```

# MNA Circuit Solver & Thévenin / Norton Equivalent Calculator

A Python tool that solves DC electrical circuits using **Modified Nodal Analysis (MNA)** and automatically computes **Thévenin** and **Norton** equivalent circuits between any two nodes.

## Features
- **Nodal Analysis:** Computes node voltages and voltage source currents automatically using matrix equations ($A \cdot x = z$).
- **Interactive SPICE-like CLI Input:** Enter circuit components line-by-line via terminal.
- **Thévenin & Norton Equivalents:** Automatically calculates $V_{th}$, $R_{th}$, $I_n$, and $R_n$.

## How to Run
```bash
python circuitanalsys.py

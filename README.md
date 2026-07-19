# applied-ml-template

> This repo demonstrates a complete machine learning workflow using the California Housing dataset.

- Additional instructions: See the [pro-analytics-02](https://denisecase.github.io/pro-analytics-02/) guide.  
- Project organization: [STRUCTURE](./STRUCTURE.md)  
- Build professional skills:
  - **Environment Management**: Isolated virtual environments
  - **Code Quality**: Automated checks with Ruff and pre-commit
  - **Documentation**: Built with MkDocs
  - **Testing**: Validate functionality
  - **Version Control**: GitHub collaboration

---

## About this Repository

Starter files for the example labs:

- `notebooks/example01` folder  
- `notebooks/example02` folder  

---

## Project 01: Linear Regression on California Housing Data

This project demonstrates a complete ML workflow:

- Load and explore the California Housing dataset
- Visualize feature distributions
- Select predictive features
- Train a linear regression model
- Evaluate model performance using R², MAE, and RMSE

### Files:

- `ml01.ipynb` – Jupyter notebook with step-by-step analysis and commentary  
- `ml01.py` – Standalone script with just the code  
- `README.md` – This file, customized for your lab project  

---

## WORKFLOW 1. Set Up Machine

Follow the setup guide to configure your machine:

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## WORKFLOW 2. Set Up Project

After setup, initialize your Python project:

- [SET UP PROJECT](./SET_UP_PROJECT.md)

```shell
uv venv
uv python pin 3.12
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run python --version
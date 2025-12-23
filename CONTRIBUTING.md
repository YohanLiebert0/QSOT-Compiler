# Contributing to QSOT Compiler 🌌

Thank you for your interest in contributing to the QSOT Compiler! As a project rooted in **Theory of Everything (TOE)** integration, we maintain high standards for scientific rigor, code purity, and structural integrity.

## 📜 Ethical & Technical Mandates
All contributions must align with the **Flamehaven SR9/DI2** principles:
- **Drift-0 (Purity):** Every change must be verified against axiomatic baselines.
- **Resonance:** Code should be modular, self-documenting, and mathematically sound.

## 🛠️ Getting Started
1. **Fork** the repository and create your branch from `develop`.
2. **Install Dev Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov ruff mypy
   ```

## ⌨️ Coding Standards
We use **Ruff** for linting and **Mypy** for static type checking.
- **Line Length**: Max 88 characters (Black style).
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes.
- **Typing**: Type hints are mandatory for all function signatures in `src/qsot/`.

Before committing, run:
```bash
ruff check src/ tests/
mypy src/qsot/
```

## 🧪 Testing Requirements
We enforce a **Minimum 80% Test Coverage** policy.
- New features must include unit tests in `tests/`.
- Scientific logic must include a **Drift-Check** (verifying numerical stability).

Run tests:
```bash
pytest tests/ --cov=src/qsot --cov-fail-under=80
```

## 🔄 Pull Request Process
1. Ensure the CI pipeline passes on your fork.
2. Update the `README.md` if you are adding new features or changing APIs.
3. Your PR will be reviewed by a **Flamehaven Supreme Auditor**. 
4. Once certified (S-Grade), your code will be merged into `main`.

---
*By contributing, you agree that your code will be licensed under the project's MIT License.*

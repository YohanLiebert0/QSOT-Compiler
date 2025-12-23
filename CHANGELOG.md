# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to **Semantic Versioning 2.0.0**.

---

## [Unreleased]

### Planned Features
- WebAssembly compiler for browser-based quantum simulations
- GPU acceleration for large-scale state evolution
- Plugin system for custom quantum channels
- Interactive Jupyter notebook tutorials

---

## [1.2.3] - 2025-12-23

### [*] "Causal Horizon" Module & Open Source Release
This release marks the **public open source debut** of QSOT Compiler on GitHub with production-grade reliability improvements including comprehensive validation, optimization convergence checks, and expanded test coverage.

#### Added
- **[Pub] Open Source Release:** Published to https://github.com/flamehaven01/QSOT-Compiler under MIT License
- **[UI] Prism Dashboard:** Professional glassmorphism interface with Voidwalker dark theme (`src/qsot/server/dashboard.py`)
- **[Viz] Real-time Visualizations:** 4 interactive plots (Kirkwood-Dirac heatmap, axiom integrity, entanglement evolution, memory kernel)
- **[AI] PyTorch Optimizer:** Gradient descent engine for Kirkwood-Dirac quasi-probability minimization (`src/qsot/core/optimizer.py`)
- **[Exp] Artifact Export System:** One-click download of NPZ states, JSON reports, PNG plots, and lab protocol
- **[Tool] Auto-Venv Launcher:** `run_dashboard.bat` with automatic virtual environment setup and PyTorch installation
- **[Doc] Screenshot Gallery:** Added `docs/` folder with dashboard screenshot and example outputs
- **[Doc] Enhanced README:** Complete rewrite with ASCII-safe symbols, installation guide, architecture diagram, troubleshooting section
- **[Doc] Citation Support:** Added BibTeX format and theoretical references (Transfer Tensor Method, Kirkwood-Dirac, Relativistic QI)
- **[Valid] Density Matrix Validation:** New `validate_density_matrix()` function with Hermitian, trace, and positive semi-definite checks
- **[AI] Early Stopping:** Optimizer now includes convergence detection with patience parameter and gradient clipping
- **[Test] Expanded Coverage:** Added `test_physics.py` with parametrized tests for relativity and entanglement modules

#### Changed
- **[Docs] ASCII Safety:** Replaced all Unicode emojis with ASCII alternatives for cross-platform compatibility (cp949/Windows safe)
- **[Docs] Expanded Documentation:** Added Prerequisites, Quick Start (Windows/Linux/macOS), CLI Mode examples, Dashboard Features guide
- **[Build] Version Alignment:** Updated all documentation to reflect v1.2.3 release
- **[UI] Metric Display:** Improved single-qubit vs. multipartite system detection (L1 Coherence vs. Logarithmic Negativity)
- **[UX] Sidebar Layout:** Reorganized configuration panel with clearer labels and helper tooltips
- **[AI] Optimizer Output:** Now includes convergence metadata and contextuality flag in results JSON

#### Fixed
- **[Critical] Simulation Trigger:** Resolved deadlock where RUN SIMULATION button was nested inside conditional display block
- **[Bug] Variable Scope:** Fixed `NameError: velocity` by correcting global variable scope in dashboard
- **[UX] Silent Failures:** Added verbose logging to launcher showing PyTorch download progress (~2.5GB first-time install)
- **[Docs] Badge Accuracy:** Corrected Python version badge (3.9+ instead of 3.10+), marked PyTorch as optional dependency
- **[Robust] Error Handling:** Enhanced error handling in optimizer with try-except blocks and graceful degradation
- **[Stable] Gradient Clipping:** Added max_norm=1.0 clipping to prevent optimization divergence

---

## [1.2.0] - 2025-12-22

### [#] The Great Refactoring & S-Grade Elevation
Transition from research prototype to production-ready S-Grade module with modern Python packaging and comprehensive test coverage.

#### Added
- **[Arch] Source Layout:** Implemented `src/qsot/` structure for proper packaging and modularity
- **[Build] Modern Packaging:** Added `pyproject.toml` with setuptools backend and dependency management
- **[CI] GitHub Actions:** Created `ci.yaml` workflow with pytest, coverage reporting, and drift checks
- **[Gov] Project Governance:** Added `CONTRIBUTING.md`, `SECURITY.md`, and `LICENSE` (MIT) for open source collaboration
- **[Test] Pytest Suite:** Comprehensive test suite in `tests/` with 80%+ coverage target and axiom validation
- **[API] Direct Execution:** Refactored `api_server.py` to use direct Python imports instead of subprocess calls for better performance
- **[Phys] Entanglement Module:** New `src/qsot/physics/entanglement.py` with Logarithmic Negativity and L1 Coherence metrics
- **[Phys] Relativity Module:** Lorentz boost implementation in `src/qsot/physics/relativity.py` for observer velocity corrections
- **[Core] Memory Kernel:** Transfer Tensor Method implementation for non-Markovianity detection
- **[Core] Hash-Chained Trace:** Blockchain-inspired audit trail system for reproducibility

#### Changed
- **[Pkg] Namespace Unification:** Renamed internal modules to unified `qsot` package namespace
- **[Core] Compiler Refactor:** Moved compiler logic to `src/qsot/core/compiler.py` with improved error handling and modularity
- **[Script] ASDP Runner:** Updated `scripts/asdp_run.py` to support relativistic velocity parameter and dynamic PYTHONPATH injection
- **[Deps] Dependency Specification:** Pinned minimum versions in `requirements.txt` (numpy>=1.24.0, scipy>=1.10.0, torch>=2.0.0)

#### Fixed
- **[Bug] Circular Import:** Resolved circular dependency between `loader.py` and `compiler.py` modules
- **[Bug] Path Resolution:** Fixed import errors for relativistic boost functions in physics module
- **[Sec] Artifact Leakage:** Optimized `.gitignore` to prevent committing temporary artifacts and cache files
- **[Type] Type Hints:** Added proper type annotations to all public APIs for mypy compliance

---

## [0.5.0] - 2025-12-18

### [^] Initial Internal Release
Early prototype integrating quantum optimization with PyTorch backend.

#### Added
- **[AI] Kirkwood-Dirac Optimizer:** Initial integration with Flamehaven PyTorch Engine for gradient-based optimization
- **[Phys] Transfer Tensor Method:** Basic implementation of TTM for memory kernel analysis
- **[Core] Basic Compiler:** Proof-of-concept compiler for quantum channel sequences
- **[Utils] Density Matrix Helpers:** Utility functions for random state generation and trace distance calculations

#### Known Limitations
- No packaging structure (flat file layout)
- Limited test coverage (<30%)
- Manual dependency installation required
- No documentation or usage examples

---

## Version History Summary

| Version | Date | Type | Highlights |
|---------|------|------|------------|
| 1.2.3 | 2025-12-23 | Major | Open source release, Prism UI, ASCII-safe docs |
| 1.2.0 | 2025-12-22 | Major | S-Grade refactor, pytest suite, modern packaging |
| 0.5.0 | 2025-12-18 | Minor | Initial prototype, PyTorch optimizer, TTM |

---

## Upgrade Guide

### From 1.2.0 to 1.2.3
No breaking changes. New features are opt-in via dashboard interface.

**Action Required:**
```bash
pip install -r requirements.txt  # Updates streamlit to >=1.27.0
```

### From 0.5.0 to 1.2.0
**Breaking Changes:**
- Package namespace changed from flat imports to `qsot.*` structure
- Config file format updated (old `.py` configs deprecated, use `.json`)

**Migration Steps:**
```bash
# Old import style (0.5.0)
from compiler import run

# New import style (1.2.0+)
from qsot.core.compiler import run
```

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Code style (Ruff, Mypy)
- Testing requirements (80%+ coverage)
- Drift-Free certification process
- Pull request workflow

---

*Built with precision by **Flamehaven-Labs** | Drift-Free Certified*

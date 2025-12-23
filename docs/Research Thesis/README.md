# Academic Publication Package: QSOT Compiler v1.2.3

This directory `docs/Research Thesis` contains the finalized academic artifacts for the QSOT Compiler project, ready for submission to **Computer Physics Communications (CPC)** and **Physical Review A (PRA)**.

## [L] Directory Structure

### 1. `arxiv-cpc/` (Submission Package)
The complete LaTeX source package for arXiv/Journal submission.
- **`Paper_A_Methodology_CPC.tex`**: Main manuscript for CPC. Describes the software architecture, algorithms, and TTM complexity.
- **`Paper_B_Physics.tex`**: Main manuscript for PRA. Reports the physical discovery of "Relativistic Coherence Sudden Death".
- **`Fig1_Relativistic_decay.png`**: Key result figure for Paper B.
- **`Fig2_Architecture.png`**: System diagram for Paper A.

### 2. `project-page/` (Web Portal)
A static HTML project page for showcasing the work.
- **`index.html`**: Customized landing page with abstract, architecture diagram, and links to papers/code.
- **`static/`**: Contains CSS/JS assets.

### 3. `*.md` Drafts
- `Paper_A_Methodology_CPC.md`: Markdown draft of Paper A.
- `Paper_B_Physics_PRA.md`: Markdown draft of Paper B.
- `Publication_Roadmap.md`: Strategic plan.

---

## [>] How to Submit

1.  **For arXiv:**
    - Zip the `arxiv-cpc` folder.
    - Upload the zip file. The TeX files are pre-configured with `elsarticle` and `revtex4-2` classes.

2.  **For Journals:**
    - **CPC:** Submit `Paper_A_Methodology_CPC.tex` + `Fig2_Architecture.png`.
    - **PRA:** Submit `Paper_B_Physics.tex` + `Fig1_Relativistic_decay.png`.

## [#] DOI
- Zenodo DOI (latest release): 10.5281/zenodo.18035432
- Zenodo DOI (badge target): 10.5281/zenodo.18035246

## [L] Metadata
- **Authors:** Kwansub Yun, AGI OMEGA Modal
- **Affiliation:** Flamehaven AI
- **License:** MIT

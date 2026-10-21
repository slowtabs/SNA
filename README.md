# Social Network Centrality, Communities, and Robustness

Course group project for **Advanced Text and Social Media Analytics (ATSMA)**.  We study Zachary's Karate Club network to answer three connected questions:

1. What does the social network look like?
2. Which members are structurally important under different definitions of importance?
3. Do communities and influential members explain the network's historical split and resilience?

## Project structure

```text
.
├── notebooks/
│   ├── 01_network_exploration.ipynb
│   ├── 02_centrality_analysis.ipynb
│   └── 03_communities_and_robustness.ipynb
├── src/                         # Reusable loading, metric, and plotting helpers
├── tests/                       # Algorithm-validation tests
├── results/
│   ├── figures/                 # Generated charts (notebook output)
│   └── tables/                  # Generated CSV files (notebook output)
├── requirements.txt
└── .gitignore
```

The original single-file submission is retained as `SNA_Centrality_Analysis.ipynb` for reference. The project is intentionally delivered through three focused notebooks rather than one monolithic file.

## Collaboration workflow

The maintainer should publish the project foundation and Part 1 first. The other two members should add their assigned work through their own GitHub pull requests:

| Contributor | Branch | Files owned by the pull request |
| --- | --- | --- |
| Member 2 | `feature/centrality-analysis` | `src/centrality_algorithms.py`, `notebooks/02_centrality_analysis.ipynb`, and `tests/test_centrality_algorithms.py` |
| Member 3 | `feature/communities-robustness` | `notebooks/03_communities_and_robustness.ipynb` and result-export additions |

Each contributor should write their own commit message, verify the notebook, open the pull request from their GitHub account, and respond to at least one review comment. This produces a transparent contribution history and makes the project easy to evaluate.

## Team responsibilities

| Part | Notebook | Suggested ownership | Main contribution |
| --- | --- | --- | --- |
| 1 | `01_network_exploration.ipynb` | Member 1 | Dataset loading, network statistics, EDA and visualisation |
| 2 | `02_centrality_analysis.ipynb` | Member 2 | Centrality metrics, manual algorithms and validation |
| 3 | `03_communities_and_robustness.ipynb` | Member 3 | Community-history comparison, robustness and directed-network extension |

All members should review the final README, interpretation, and presentation slides. Replace the suggested ownership labels with your names before submission.

## Dataset

The primary dataset is NetworkX's built-in version of Zachary's Karate Club network: 34 club members, with edges representing social ties observed by Wayne Zachary. During the observation period the club split into factions associated with the instructor (Mr. Hi) and the officer (John A.). The `club` node attribute is used only to compare detected communities with that observed split.

Reference: Zachary, W. W. (1977). *An information flow model for conflict and fission in small groups*. Journal of Anthropological Research, 33(4), 452–473.

## Quick start

```bash
python -m venv .venv
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter lab
```

Run the notebooks in numerical order from the repository root. Part 3 is self-contained and can also be run independently. It writes reproducible figures and tables under `results/`.

## Interactive dashboard

The [`dashboard/`](dashboard/README.md) folder adds **Network Lens**, an interactive React dashboard for the same project. It starts with the Karate Club example, accepts browser-local edge-list uploads, calculates the centrality measures used in the notebooks, detects communities, and visualises targeted-removal robustness.

```bash
cd dashboard
npm install
npm run dev
```

It can be hosted on Vercel (set `dashboard` as the Root Directory) and also includes an Electron wrapper for a local desktop version. See the [dashboard guide](dashboard/README.md) for both workflows.

## Reproducibility

- Python 3.10+ is recommended.
- Randomised experiments use explicit seeds.
- Run `pytest -q` after the reusable algorithms have been added to `src/`.
- Generated files are ignored by Git; keep a small curated set of final figures if your faculty asks for them.

## Key takeaways

- Centrality is not a single concept: degree, closeness, betweenness, eigenvector centrality, and PageRank surface different roles.
- Communities provide a structural view of the Karate Club's historical division.
- Removing highly central nodes damages connectivity faster than a random-removal baseline.
- Directed networks require separate interpretation of in-degree, out-degree, and PageRank.

## References

- Zachary (1977), cited above.
- Brandes, U. (2001). *A faster algorithm for betweenness centrality*. Journal of Mathematical Sociology, 25(2), 163–177.
- [NetworkX documentation](https://networkx.org/documentation/stable/).

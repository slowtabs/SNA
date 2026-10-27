# Data directory

This folder is for optional network datasets used by the notebooks.

The default analysis uses NetworkX's built-in **Zachary's Karate Club** graph, so
the project runs without downloading any data. To analyse another network, put
an edge-list or Matrix Market (`.mtx`) file in this folder and pass its relative
path to `load_graph`, for example:

```python
G = load_graph("data/example_edges.txt")
```

Supported edge-list rows are `source target` or `source,target`. Blank lines and
lines beginning with `#` or `%` are ignored. Use `directed=True` for follower,
reply, or citation networks where edge direction matters.

Do not commit data that is private, licensed for restricted use, or too large
for GitHub. Record the source, licence, collection date, and any preprocessing
in this file when adding a dataset.

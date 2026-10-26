import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, r"D:\Projects\ATSMA\tmp\lab8_report\packages")
os.environ["MPLCONFIGDIR"] = r"D:\Projects\ATSMA\tmp\lab8_report\matplotlib"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


ROOT = Path(r"D:\Projects\ATSMA\tmp\lab8_report")
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)


def top_terms(model, terms, count=10):
    results = []
    for center in model.cluster_centers_:
        indices = center.argsort()[-count:][::-1]
        results.append([terms[index] for index in indices])
    return results


def sarcasm():
    records = json.loads((ROOT / "sarcasm.json").read_text(encoding="utf-8"))
    headlines = [item["headline"] for item in records]
    truth = [item["is_sarcastic"] for item in records]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=3, max_features=5000)
    matrix = vectorizer.fit_transform(headlines)
    model = KMeans(n_clusters=2, n_init=20, random_state=42)
    clusters = model.fit_predict(matrix)
    cluster_majority = {
        cluster: Counter(label for label, assigned in zip(truth, clusters) if assigned == cluster).most_common(1)[0][0]
        for cluster in range(2)
    }
    mapped = [cluster_majority[cluster] for cluster in clusters]
    accuracy = sum(actual == predicted for actual, predicted in zip(truth, mapped)) / len(truth)
    contingency = pd.crosstab(pd.Series(clusters, name="K-means cluster"), pd.Series(truth, name="Dataset label"))
    contingency.to_csv(ROOT / "sarcasm_cluster_vs_label.csv")
    terms = vectorizer.get_feature_names_out()
    terms_by_cluster = top_terms(model, terms)
    silhouette = silhouette_score(matrix[:2500], clusters[:2500], metric="cosine", random_state=42)

    plot = contingency.rename(columns={0: "Not sarcastic", 1: "Sarcastic"})
    axis = plot.plot(kind="bar", stacked=True, color=["#4C78A8", "#F58518"], figsize=(7.0, 4.2))
    axis.set(title="Sarcasm headline clusters compared with dataset labels", xlabel="K-means cluster", ylabel="Headlines")
    axis.legend(title="Dataset label")
    plt.tight_layout()
    plt.savefig(FIGURES / "sarcasm_clusters.png", dpi=200)
    plt.close()
    return {
        "documents": len(headlines), "features": int(matrix.shape[1]),
        "cluster_sizes": {int(k): int(v) for k, v in Counter(clusters).items()},
        "majority_map": {int(k): int(v) for k, v in cluster_majority.items()},
        "majority_agreement": float(accuracy), "silhouette": float(silhouette),
        "terms": terms_by_cluster,
        "contingency": {str(k): {str(a): int(b) for a, b in v.items()} for k, v in contingency.to_dict().items()},
    }


def anthems():
    frame = pd.read_csv(ROOT / "anthems" / "anthems.csv", encoding="utf-8", encoding_errors="replace")
    frame = frame.dropna(subset=["Anthem"]).copy()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2, max_features=3000)
    matrix = vectorizer.fit_transform(frame["Anthem"])
    model = KMeans(n_clusters=5, n_init=50, random_state=42)
    clusters = model.fit_predict(matrix)
    frame["cluster"] = clusters
    terms = vectorizer.get_feature_names_out()
    terms_by_cluster = top_terms(model, terms)
    silhouette = silhouette_score(matrix, clusters, metric="cosine")
    sizes = frame["cluster"].value_counts().sort_index()
    pd.DataFrame({"cluster": sizes.index, "documents": sizes.values}).to_csv(ROOT / "anthem_cluster_sizes.csv", index=False)

    svd = TruncatedSVD(n_components=2, random_state=42)
    reduced = svd.fit_transform(matrix)
    plt.figure(figsize=(7.0, 4.8))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=clusters, cmap="tab10", s=38, alpha=0.8)
    plt.title("National anthems clustered by TF-IDF content")
    plt.xlabel("Latent semantic component 1")
    plt.ylabel("Latent semantic component 2")
    plt.colorbar(scatter, label="K-means cluster")
    plt.tight_layout()
    plt.savefig(FIGURES / "anthem_clusters.png", dpi=200)
    plt.close()
    examples = {
        int(cluster): frame.loc[frame["cluster"] == cluster, "Country"].head(6).tolist()
        for cluster in sorted(frame["cluster"].unique())
    }
    return {
        "documents": len(frame), "features": int(matrix.shape[1]), "cluster_sizes": {int(k): int(v) for k, v in sizes.items()},
        "silhouette": float(silhouette), "terms": terms_by_cluster, "examples": examples,
    }


results = {"sarcasm": sarcasm(), "anthems": anthems()}
(ROOT / "clustering_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))

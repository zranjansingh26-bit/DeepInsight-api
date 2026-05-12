"""
DeepInsight Starter Suite — KMeans Clusterer Engine.

Performs KMeans clustering with automatic K selection via silhouette
score and PCA-based visualization.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def run_clustering(
    df: pd.DataFrame,
    max_k: int = 10,
    min_k: int = 2,
) -> dict[str, Any]:
    """
    Run KMeans clustering with automatic K selection.

    Args:
        df: Input DataFrame
        max_k: Maximum number of clusters to try
        min_k: Minimum number of clusters to try

    Returns:
        Dictionary with cluster labels, centroids, silhouette score, and PCA components.
    """
    numeric_df = df.select_dtypes(include=[np.number]).dropna()

    if numeric_df.shape[0] < min_k:
        return {"error": f"Need at least {min_k} rows for clustering."}
    if numeric_df.shape[1] < 1:
        return {"error": "No numeric columns available for clustering."}

    # Standardize features
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_df)

    # Find optimal K using silhouette score
    max_k = min(max_k, numeric_df.shape[0] - 1)
    if max_k < min_k:
        max_k = min_k

    best_k = min_k
    best_score = -1
    scores = {}

    for k in range(min_k, max_k + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=42, max_iter=300)
        labels = km.fit_predict(scaled_data)
        score = silhouette_score(scaled_data, labels)
        scores[k] = round(float(score), 4)

        if score > best_score:
            best_score = score
            best_k = k

    logger.info("Optimal K=%d with silhouette=%.4f", best_k, best_score)

    # Final clustering with optimal K
    final_km = KMeans(n_clusters=best_k, n_init=10, random_state=42, max_iter=300)
    final_labels = final_km.fit_predict(scaled_data)

    # PCA for 2D visualization
    n_components = min(2, scaled_data.shape[1])
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(scaled_data)

    # Transform centroids to PCA space
    centroid_components = pca.transform(final_km.cluster_centers_)

    # Cluster statistics
    cluster_stats = {}
    for cluster_id in range(best_k):
        mask = final_labels == cluster_id
        cluster_df = numeric_df.iloc[mask]
        cluster_stats[str(cluster_id)] = {
            "size": int(mask.sum()),
            "percentage": round(float(mask.sum() / len(final_labels) * 100), 2),
            "mean_values": {
                col: round(float(cluster_df[col].mean()), 4)
                for col in numeric_df.columns
            },
        }

    result = {
        "optimal_k": best_k,
        "silhouette_score": round(float(best_score), 4),
        "silhouette_scores_by_k": scores,
        "labels": final_labels.tolist(),
        "cluster_stats": cluster_stats,
        "pca_components": components.tolist(),
        "pca_centroids": centroid_components.tolist(),
        "pca_explained_variance": [
            round(float(v), 4) for v in pca.explained_variance_ratio_
        ],
        "features_used": numeric_df.columns.tolist(),
        "inertia": round(float(final_km.inertia_), 4),
    }

    logger.info("Clustering complete: K=%d, %d data points", best_k, len(final_labels))
    return result

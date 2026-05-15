"""
DeepInsight — Evaluation Engine.

Handles detailed metric calculation and result analysis for classification.
"""

import logging
import numpy as np
from typing import Any, Dict
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)

class EvaluationEngine:
    """Computes comprehensive metrics for classification models."""

    @staticmethod
    def calculate_classification_metrics(y_true, y_pred, y_prob=None) -> Dict[str, Any]:
        """
        Calculate Accuracy, Precision, Recall, Weighted F1, ROC-AUC, 
        and Confusion Matrix.
        """
        unique_labels = np.unique(y_true)
        num_classes = len(unique_labels)
        
        # Weighted averaging is usually best for imbalanced real-world data
        avg_method = "weighted" if num_classes > 2 else "binary"
        
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average=avg_method, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average=avg_method, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average=avg_method, zero_division=0)),
        }
        
        # ROC-AUC requires probabilities
        if y_prob is not None:
            try:
                if num_classes == 2:
                    # For binary, y_prob can be 1D (prob of class 1) or 2D
                    if len(y_prob.shape) > 1 and y_prob.shape[1] == 2:
                        y_prob_calc = y_prob[:, 1]
                    else:
                        y_prob_calc = y_prob
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob_calc))
                else:
                    # Multi-class
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted"))
            except Exception as e:
                logger.warning(f"ROC-AUC calculation failed: {e}")
                metrics["roc_auc"] = 0.0
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()
        
        return metrics

    @staticmethod
    def get_feature_importance(model: Any, feature_names: list[str]) -> Dict[str, float]:
        """Extract and rank feature importance."""
        importances = {}
        try:
            if hasattr(model, "feature_importances_"):
                vals = model.feature_importances_
            elif hasattr(model, "coef_"):
                # For linear models, use absolute coefficients
                vals = np.abs(model.coef_)
                if len(vals.shape) > 1: # Multiclass
                    vals = np.mean(vals, axis=0)
            else:
                return {}
                
            # Zip and sort
            raw = {name: float(val) for name, val in zip(feature_names, vals)}
            # Sort by importance descending
            importances = dict(sorted(raw.items(), key=lambda x: x[1], reverse=True))
        except Exception as e:
            logger.error(f"Failed to extract feature importance: {e}")
            
        return importances

    @staticmethod
    def calculate_clustering_metrics(X, labels) -> Dict[str, float]:
        """Calculate clustering-specific metrics."""
        from sklearn.metrics import silhouette_score, davies_bouldin_score
        metrics = {}
        if len(np.unique(labels)) > 1:
            metrics["silhouette"] = float(silhouette_score(X, labels))
            metrics["davies_bouldin"] = float(davies_bouldin_score(X, labels))
        else:
            metrics["silhouette"] = -1.0
            metrics["davies_bouldin"] = -1.0
        return metrics

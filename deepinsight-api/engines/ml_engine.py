"""
DeepInsight — AutoML Engine.

Orchestrates automated model training, comparison, and selection 
with advanced validation, preprocessing, and optimization.
"""

import logging
import time
import pandas as pd
import numpy as np
from typing import Any, Optional
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV

from engines.model_factory import ModelFactory
from engines.validation_engine import ValidationEngine
from engines.preprocessing_pipeline import PreprocessingPipeline
from engines.evaluation_engine import EvaluationEngine

logger = logging.getLogger(__name__)

class AutoMLPipeline:
    """Automated Machine Learning pipeline for multiple problem types."""

    def __init__(self, df: pd.DataFrame, target_col: Optional[str] = None):
        self.df = df
        self.target_col = target_col or ValidationEngine.suggest_target(df)
        self.problem_type = self._detect_problem_type()
        self.best_model = None
        self.trained_models = []
        self.validation_results = {}
        self.preprocessing_summary = {}

    def _detect_problem_type(self) -> str:
        """Detect if the problem is classification or regression."""
        if not self.target_col:
            return "clustering"
        
        target = self.df[self.target_col].dropna()
        unique_vals = target.nunique()
        
        if np.issubdtype(target.dtype, np.number):
            if unique_vals < 15:
                return "classification"
            return "regression"
        else:
            return "classification"

    def run(self, model_name: str | None = None) -> dict[str, Any]:
        """Run the training process with full optimization pipeline."""
        logger.info(f"Starting ML process for {self.problem_type} on target: {self.target_col}")
        
        # 1. Validate
        if self.problem_type == "classification":
            val_res = ValidationEngine.validate_classification(self.df, self.target_col)
            self.validation_results = val_res
            if not val_res["is_valid"]:
                raise ValueError(val_res.get("error", "Invalid dataset for classification"))
        
        # 2. Preprocess
        pipeline = PreprocessingPipeline(self.target_col if self.target_col else "target")
        # Apply SMOTE if imbalance detected
        apply_smote = self.validation_results.get("diagnostics", {}).get("class_distribution", {})
        is_imbalanced = False
        if apply_smote:
             vals = list(apply_smote.values())
             if max(vals) / min(vals) > 2.0:
                 is_imbalanced = True

        X_processed, y_processed = pipeline.fit_transform(self.df, apply_smote=is_imbalanced)
        
        if self.problem_type == "clustering":
            return self._run_clustering(X_processed)

        self.preprocessing_summary = {
            "features_in": len(self.df.columns) - 1,
            "features_out": X_processed.shape[1],
            "samples": X_processed.shape[0],
            "smote_applied": is_imbalanced
        }

        # 3. Split
        # Use Stratified split for classification
        test_size = 0.2
        if self.problem_type == "classification":
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y_processed, test_size=test_size, random_state=42, stratify=y_processed
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y_processed, test_size=test_size, random_state=42
            )
        
        results = []
        models_to_train = [model_name] if model_name else ModelFactory.list_available(self.problem_type)
        
        for name in models_to_train:
            try:
                logger.info(f"Training and optimizing {name}...")
                start_time = time.time()
                
                # Base model
                base_model = ModelFactory.create(name, self.problem_type)
                
                # Hyperparameter Optimization
                grid = ModelFactory.get_grid(name)
                if grid and self.problem_type == "classification":
                    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                    # Use f1_weighted for better balance
                    search = GridSearchCV(base_model, grid, cv=cv, scoring='f1_weighted', n_jobs=-1)
                    search.fit(X_train, y_train)
                    model = search.best_estimator_
                    cv_results = {
                        "best_params": search.best_params_,
                        "best_score": float(search.best_score_),
                        "cv_std": float(search.cv_results_['std_test_score'][search.best_index_])
                    }
                else:
                    model = base_model.fit(X_train, y_train)
                    cv_results = {}
                
                duration = time.time() - start_time
                
                # Evaluation
                y_pred = model.predict(X_test)
                y_prob = None
                
                if self.problem_type == "classification":
                    if hasattr(model, "predict_proba"):
                        y_prob = model.predict_proba(X_test)
                    metrics = EvaluationEngine.calculate_classification_metrics(y_test, y_pred, y_prob)
                else:
                    metrics = EvaluationEngine.calculate_regression_metrics(y_test, y_pred)
                    
                importances = EvaluationEngine.get_feature_importance(model, X_processed.columns.tolist())
                
                res = {
                    "name": name,
                    "model": model,
                    "metrics": metrics,
                    "cv_results": cv_results,
                    "importances": importances,
                    "duration": duration,
                    "problem_type": self.problem_type
                }
                results.append(res)
                
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
                if model_name: raise # Re-throw if user specifically asked for this model
        
        if not results:
            raise RuntimeError("No models were successfully trained.")
            
        # Select best model
        primary_metric = "f1_score" if self.problem_type == "classification" else "r2_score"
        self.best_model = max(results, key=lambda x: x["metrics"].get(primary_metric, 0))
        self.trained_models = results
        
        return {
            "problem_type": self.problem_type,
            "best_model_name": self.best_model["name"],
            "best_metrics": self.best_model["metrics"],
            "all_results": [
                {
                    "name": r["name"], 
                    "metrics": r["metrics"], 
                    "duration": r["duration"],
                    "cv_results": r["cv_results"]
                } for r in results
            ],
            "encoders": pipeline.encoders,
            "preprocessing_summary": self.preprocessing_summary,
            "validation_results": self.validation_results,
            "visualization_data": {
                "y_test": y_test.tolist(),
                "y_pred": y_pred.tolist(),
                "y_prob": y_prob.tolist() if y_prob is not None else None,
                "feature_names": X_processed.columns.tolist(),
                "target_name": self.target_col,
                "importances": self.best_model["importances"]
            }
        }

    def _run_clustering(self, df_processed: pd.DataFrame) -> dict[str, Any]:
        """Run multiple clustering algorithms and compare them."""
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        
        X = df_processed
        results = []
        
        # 1. KMeans
        for k in [3, 5]:
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(X)
            metrics = EvaluationEngine.calculate_clustering_metrics(X, labels)
            results.append({"name": f"KMeans (k={k})", "metrics": metrics, "model": model})
            
        # 2. DBSCAN
        model_db = DBSCAN(eps=0.5, min_samples=5)
        labels_db = model_db.fit_predict(X)
        metrics_db = EvaluationEngine.calculate_clustering_metrics(X, labels_db)
        results.append({"name": "DBSCAN", "metrics": metrics_db, "model": model_db})
        
        # 3. Hierarchical
        model_hc = AgglomerativeClustering(n_clusters=3)
        labels_hc = model_hc.fit_predict(X)
        metrics_hc = EvaluationEngine.calculate_clustering_metrics(X, labels_hc)
        results.append({"name": "Hierarchical", "metrics": metrics_hc, "model": model_hc})
        
        # Select best based on Silhouette score
        self.trained_models = results
        self.best_model = max(results, key=lambda x: x["metrics"].get("silhouette", -1))
        
        return {
            "problem_type": "clustering",
            "best_model_name": self.best_model["name"],
            "best_metrics": self.best_model["metrics"],
            "all_results": [
                {"name": r["name"], "metrics": r["metrics"]}
                for r in results
            ]
        }

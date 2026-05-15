"""
DeepInsight Starter Suite — ML Service.

Orchestrates AutoML training, persistence, and prediction.
"""

import logging
import io
import time
import joblib
from typing import Any, Optional

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from db import repository
from config import get_settings
from services import dataset_service
from engines.ml_engine import AutoMLPipeline
from engines.ml_visualizer import (
    generate_confusion_matrix_chart,
    generate_feature_importance_chart,
    generate_model_comparison_chart
)

logger = logging.getLogger(__name__)

async def train_selected_model(
    dataset_id: str, 
    user_id: str, 
    model_name: str, 
    target_col: str | None = None
) -> dict[str, Any]:
    """
    Train ONLY the selected model on the dataset.
    """
    settings = get_settings()
    
    # 1. Fetch dataset
    dataset = repository.get_dataset(dataset_id)
    if not dataset:
        raise ValueError("Dataset not found")
        
    df = dataset_service.get_dataframe(dataset)
    
    # 2. Run Training for specific model
    pipeline = AutoMLPipeline(df, target_col=target_col)
    results = pipeline.run(model_name=model_name)
    
    trained_model_info = pipeline.best_model
    encoders = results["encoders"]
    
    # 3. Save model to Storage
    model_data = {
        "model": trained_model_info["model"],
        "encoders": encoders,
        "feature_names": results["visualization_data"]["feature_names"],
        "target_col": pipeline.target_col,
        "problem_type": results["problem_type"]
    }
    
    buffer = io.BytesIO()
    joblib.dump(model_data, buffer)
    buffer.seek(0)
    
    storage_path = repository.upload_file_to_storage(
        user_id=user_id,
        file_name=f"model_{trained_model_info['name'].replace(' ', '_')}_{int(time.time())}.joblib",
        file_content=buffer.read(),
        content_type="application/octet-stream",
        bucket=settings.supabase_models_bucket
    )
    
    # 4. Save to Database
    saved_model = repository.save_trained_model(
        user_id=user_id,
        dataset_id=dataset_id,
        model_name=trained_model_info["name"],
        problem_type=results["problem_type"],
        training_time=trained_model_info["duration"],
        metrics=trained_model_info["metrics"],
        storage_path=storage_path
    )
    
    # 5. Generate visualizations
    viz = results["visualization_data"]
    charts = {}
    if results["problem_type"] == "classification":
        charts["confusion_matrix"] = generate_confusion_matrix_chart(viz["y_test"], viz["y_pred"])
        if viz.get("y_prob") is not None:
             charts["roc_curve"] = generate_roc_curve(viz["y_test"], np.array(viz["y_prob"]))
        if viz.get("importances"):
            charts["feature_importance"] = generate_feature_importance_chart(
                list(viz["importances"].keys())[:10], 
                list(viz["importances"].values())[:10]
            )
    
    return {
        "model_id": saved_model["id"],
        "model_name": saved_model["model_name"],
        "metrics": trained_model_info["metrics"],
        "charts": charts,
        "validation": results["validation_results"],
        "preprocessing": results["preprocessing_summary"]
    }

def list_available_models(problem_type: str) -> list[str]:
    """List supported models for a problem type."""
    from engines.model_factory import ModelFactory
    return ModelFactory.list_available(problem_type)

async def get_dataset_comparison(user_id: str, dataset_id: str) -> list[dict]:
    """Get performance comparison of all models trained on this dataset."""
    return repository.get_model_comparison(user_id, dataset_id)

async def run_ml_task(
    dataset_id: str,
    user_id: str,
    task_type: str,
    model_name: str | None = None,
    target_col: str | None = None,
    k: int = 3
) -> dict[str, Any]:
    """
    Unified entry point for task-based ML with rich dashboard results.
    """
    settings = get_settings()
    dataset = repository.get_dataset(dataset_id)
    if not dataset:
        raise ValueError("Dataset not found")
        
    df = dataset_service.get_dataframe(dataset)
    
    if task_type == "clustering":
        from engines import clusterer
        result = clusterer.run_clustering(df, max_k=k, min_k=k)
        
        df_with_clusters = df.copy()
        df_with_clusters["Cluster"] = result["labels"]
        
        return {
            "task_type": "clustering",
            "message": "Clustering complete!",
            "metrics": {"silhouette": result["silhouette_score"]},
            "sample_data": df_with_clusters.head(20).to_dict(orient="records"),
            "columns": df_with_clusters.columns.tolist()
        }
    
    # Supervised Learning
    if not model_name:
        model_name = "Linear Regression" if task_type == "regression" else "Random Forest"
    
    pipeline = AutoMLPipeline(df, target_col=target_col)
    if task_type == "regression":
        pipeline.problem_type = "regression"
    elif task_type == "classification":
        pipeline.problem_type = "classification"

    results = pipeline.run(model_name=model_name)
    best = pipeline.best_model
    viz = results["visualization_data"]
    
    # Generate Charts
    charts = {}
    if task_type == "classification":
        charts["confusion_matrix"] = generate_confusion_matrix_chart(viz["y_test"], viz["y_pred"])
        from engines.ml_visualizer import generate_roc_curve
        if viz.get("y_prob") is not None:
            charts["roc_curve"] = generate_roc_curve(viz["y_test"], np.array(viz["y_prob"]))
    else:
        from engines.ml_visualizer import generate_residual_plot
        charts["residual_plot"] = generate_residual_plot(np.array(viz["y_test"]), np.array(viz["y_pred"]))
        
    # Feature Importance
    if viz.get("importances"):
        charts["feature_importance"] = generate_feature_importance_chart(
            list(viz["importances"].keys())[:10], 
            list(viz["importances"].values())[:10]
        )
    
    # Save to Database for history/leaderboard
    repository.save_trained_model(
        user_id=user_id,
        dataset_id=dataset_id,
        model_name=best["name"],
        problem_type=pipeline.problem_type,
        training_time=best["duration"],
        metrics=best["metrics"],
        storage_path="internal://session_model"
    )
    
    # Get comparison for leaderboard
    comparison = await get_dataset_comparison(user_id, dataset_id)
    
    return {
        "task_type": task_type,
        "model_name": best["name"],
        "metrics": best["metrics"],
        "duration": best["duration"],
        "charts": charts,
        "comparison": comparison,
        "validation": results["validation_results"],
        "preprocessing": results["preprocessing_summary"],
        "message": f"Model trained and optimized: {best['name']}"
    }

def self_get_feature_importance(model: Any, feature_names: list[str]) -> dict[str, float]:
    """Extract feature importance from a model if available."""
    try:
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_)
            if len(importances.shape) > 1: # Multiclass Logistic
                importances = importances.mean(axis=0)
        else:
            return {}
            
        return {
            name: float(imp) for name, imp in zip(feature_names, importances)
        }
    except Exception:
        return {}

async def run_prediction(model_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Load model and run prediction."""
    settings = get_settings()
    
    # 1. Fetch model metadata
    model_meta = repository.get_trained_model(model_id)
    if not model_meta:
        raise ValueError("Model not found")
        
    # 2. Download model file
    model_bytes = repository.download_file_from_storage(
        model_meta["storage_path"],
        bucket=settings.supabase_models_bucket
    )
    
    buffer = io.BytesIO(model_bytes)
    model_bundle = joblib.load(buffer)
    
    model = model_bundle["model"]
    encoders = model_bundle["encoders"]
    feature_names = model_bundle["feature_names"]
    
    # 3. Preprocess input
    input_df = pd.DataFrame([input_data])
    
    # Apply encoders and scaling
    # Note: In a production environment, this needs to be more robust
    # handling missing features, types, etc.
    for col, enc in encoders.items():
        if col in input_df.columns and hasattr(enc, "transform"):
            input_df[col] = enc.transform(input_df[col].astype(str))
            
    if "scaler" in encoders:
        input_df[feature_names] = encoders["scaler"].transform(input_df[feature_names])
        
    # 4. Predict
    start_time = time.time()
    prediction = model.predict(input_df[feature_names])
    latency = (time.time() - start_time) * 1000
    
    # If classification and we have label encoder for target
    result = prediction[0]
    target_col = model_bundle["target_col"]
    if target_col in encoders and hasattr(encoders[target_col], "inverse_transform"):
        result = encoders[target_col].inverse_transform([result])[0]
        
    # 5. Log prediction
    repository.log_prediction(
        model_id=model_id,
        input_data=input_data,
        prediction=str(result),
        latency_ms=latency
    )
    
    return {
        "prediction": result,
        "latency_ms": latency,
        "model_name": model_meta["model_name"]
    }

async def generate_interpretation(model_results: dict) -> str:
    """Generate an AI interpretation of the model performance and results."""
    from services import llm_client
    import json
    
    system_prompt = (
        "You are an expert data scientist. Provide a concise, professional interpretation "
        "of the following machine learning model training results. "
        "Explain what the metrics mean and suggest potential next steps for improvement."
    )
    
    user_message = f"Model: {model_results['model_name']}\nProblem Type: {model_results['problem_type']}\nMetrics: {json.dumps(model_results['metrics'], indent=2)}"
    
    try:
        response = await llm_client.chat_completion(system_prompt, user_message)
        return response.answer
    except Exception as e:
        logger.error(f"Failed to generate interpretation: {e}")
        return "AI interpretation unavailable."

async def suggest_target(dataset_id: str) -> dict:
    """Suggest a target column and problem type for a dataset."""
    dataset = repository.get_dataset(dataset_id)
    if not dataset:
        raise ValueError("Dataset not found")
        
    df = dataset_service.get_dataframe(dataset)
    pipeline = AutoMLPipeline(df)
    target = pipeline.suggest_target_column()
    # Need to re-trigger detection since target might have changed
    pipeline.target_col = target
    problem_type = pipeline._detect_problem_type() if target else "clustering"
    
    return {
        "suggested_target": target,
        "suggested_problem_type": problem_type,
        "columns": df.columns.tolist()
    }

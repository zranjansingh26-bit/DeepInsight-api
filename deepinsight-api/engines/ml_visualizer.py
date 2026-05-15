"""
DeepInsight Starter Suite — ML Visualization Engine.

Generates Plotly charts for model evaluation and comparison.
"""

import json
import logging
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.metrics import confusion_matrix

logger = logging.getLogger(__name__)

def _fig_to_dict(fig: go.Figure) -> dict[str, Any]:
    """Convert a Plotly figure to a JSON-serializable dict."""
    return json.loads(pio.to_json(fig))

def generate_confusion_matrix_chart(y_true, y_pred, labels=None) -> dict[str, Any]:
    """Generate a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    if labels is None:
        labels = [str(i) for i in range(len(cm))]
        
    fig = px.imshow(
        cm,
        text_auto=True,
        x=labels,
        y=labels,
        labels=dict(x="Predicted", y="Actual", color="Count"),
        title="Confusion Matrix",
        template="plotly_dark",
        color_continuous_scale="Blues"
    )
    fig.update_layout(width=500, height=500)
    return _fig_to_dict(fig)

def generate_feature_importance_chart(feature_names, importances, title="Feature Importance") -> dict[str, Any]:
    """Generate a bar chart for feature importance."""
    df_imp = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    }).sort_values(by="Importance", ascending=True)
    
    # Take top 20 features
    df_imp = df_imp.tail(20)
    
    fig = px.bar(
        df_imp,
        x="Importance",
        y="Feature",
        orientation="h",
        title=title,
        template="plotly_dark",
        color="Importance",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(height=max(400, len(df_imp) * 20))
    return _fig_to_dict(fig)

def generate_model_comparison_chart(results: list[dict[str, Any]], primary_metric="f1_score") -> dict[str, Any]:
    """Generate a comparison chart for multiple models."""
    df_comp = pd.DataFrame([
        {
            "Model": r["name"],
            "Metric": primary_metric,
            "Value": r["metrics"].get(primary_metric, 0)
        }
        for r in results
    ]).sort_values(by="Value", ascending=False)
    
    fig = px.bar(
        df_comp,
        x="Value",
        y="Model",
        orientation="h",
        title=f"Model Comparison — {primary_metric}",
        template="plotly_dark",
        color="Value",
        color_continuous_scale="Plasma"
    )
    return _fig_to_dict(fig)

def generate_residual_plot(y_true, y_pred) -> dict[str, Any]:
    """Generate a residual plot for regression."""
    residuals = y_true - y_pred
    fig = px.scatter(
        x=y_pred,
        y=residuals,
        labels=dict(x="Predicted Values", y="Residuals"),
        title="Residual Plot",
        template="plotly_dark"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    return _fig_to_dict(fig)
def generate_multi_metric_comparison(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a grouped bar chart for multiple metrics across models."""
    data = []
    for r in results:
        for metric, val in r["metrics"].items():
            # Filter out metrics that shouldn't be averaged/compared in this chart
            if metric in ["accuracy", "f1_score", "precision", "recall", "roc_auc", "r2_score"]:
                data.append({
                    "Model": r["name"],
                    "Metric": metric.replace("_", " ").title(),
                    "Score": float(val)
                })
    
    df = pd.DataFrame(data)
    if df.empty:
        return {}
        
    fig = px.bar(
        df,
        x="Model",
        y="Score",
        color="Metric",
        barmode="group",
        title="Comprehensive Model Performance Comparison",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(yaxis_range=[0, 1.1])
    return _fig_to_dict(fig)

def generate_roc_curve(y_true, y_prob, labels=None) -> dict[str, Any]:
    """Generate a ROC curve chart."""
    from sklearn.metrics import roc_curve, auc
    
    fig = go.Figure()
    fig.add_shape(
        type='line', line=dict(dash='dash'),
        x0=0, x1=1, y0=0, y1=1
    )

    # Check if binary or multiclass
    unique_labels = np.unique(y_true)
    if len(unique_labels) == 2:
        # Binary
        if len(y_prob.shape) > 1 and y_prob.shape[1] == 2:
            y_prob_calc = y_prob[:, 1]
        else:
            y_prob_calc = y_prob
            
        fpr, tpr, _ = roc_curve(y_true, y_prob_calc)
        roc_auc = auc(fpr, tpr)
        
        fig.add_trace(go.Scatter(x=fpr, y=tpr, name=f'ROC (AUC={roc_auc:.2f})', mode='lines'))
    else:
        # Multiclass (one-vs-rest)
        from sklearn.preprocessing import label_binarize
        y_true_bin = label_binarize(y_true, classes=unique_labels)
        
        for i in range(len(unique_labels)):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
            roc_auc = auc(fpr, tpr)
            label_name = labels[i] if labels and i < len(labels) else f"Class {unique_labels[i]}"
            fig.add_trace(go.Scatter(x=fpr, y=tpr, name=f'{label_name} (AUC={roc_auc:.2f})', mode='lines'))

    fig.update_layout(
        title="Receiver Operating Characteristic (ROC) Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        template="plotly_dark",
        width=600, height=500,
        legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99)
    )
    
    return _fig_to_dict(fig)

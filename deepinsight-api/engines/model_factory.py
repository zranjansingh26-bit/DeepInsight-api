"""
DeepInsight Starter Suite — ML Model Factory.

Maps model names to their respective scikit-learn or XGBoost classes.
"""

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from xgboost import XGBClassifier, XGBRegressor

class ModelFactory:
    """Factory for creating ML models and their hyperparameter grids."""
    
    MODELS = {
        "classification": {
            "Logistic Regression": LogisticRegression,
            "Random Forest": RandomForestClassifier,
            "Decision Tree": DecisionTreeClassifier,
            "XGBoost": XGBClassifier,
            "SVM": SVC,
            "KNN": KNeighborsClassifier
        },
        "regression": {
            "Linear Regression": LinearRegression,
            "Random Forest": RandomForestRegressor,
            "Decision Tree": DecisionTreeRegressor,
            "XGBoost": XGBRegressor,
            "SVM": SVR,
            "KNN": KNeighborsRegressor
        }
    }

    # Hyperparameter grids for classification
    GRIDS = {
        "Logistic Regression": {
            "C": [0.01, 0.1, 1.0, 10.0, 100.0],
            "solver": ["lbfgs", "liblinear", "saga"],
            "max_iter": [500]
        },
        "Random Forest": {
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4]
        },
        "Decision Tree": {
            "max_depth": [None, 5, 10, 15, 20],
            "min_samples_split": [2, 5, 10],
            "criterion": ["gini", "entropy"]
        },
        "XGBoost": {
            "n_estimators": [100, 200],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "max_depth": [3, 5, 7, 9],
            "subsample": [0.8, 1.0]
        },
        "SVM": {
            "C": [0.1, 1.0, 10.0, 100.0],
            "kernel": ["linear", "rbf", "poly"],
            "gamma": ["scale", "auto"],
            "probability": [True]
        },
        "KNN": {
            "n_neighbors": [3, 5, 7, 9, 11, 15],
            "weights": ["uniform", "distance"],
            "metric": ["euclidean", "manhattan"]
        }
    }

    @classmethod
    def create(cls, model_name: str, problem_type: str, **kwargs):
        """Create a model instance."""
        model_class = cls.MODELS.get(problem_type, {}).get(model_name)
        if not model_class:
            raise ValueError(f"Model '{model_name}' not supported for {problem_type}")
            
        # Add default balanced weights for classification if supported
        if problem_type == "classification":
            if model_name in ["Logistic Regression", "Random Forest", "Decision Tree", "SVM"]:
                if "class_weight" not in kwargs:
                    kwargs["class_weight"] = "balanced"
                    
        return model_class(**kwargs)

    @classmethod
    def get_grid(cls, model_name: str) -> dict:
        """Get hyperparameter grid for a model."""
        return cls.GRIDS.get(model_name, {})

    @classmethod
    def list_available(cls, problem_type: str) -> list[str]:
        """List available model names for a given problem type."""
        return list(cls.MODELS.get(problem_type, {}).keys())

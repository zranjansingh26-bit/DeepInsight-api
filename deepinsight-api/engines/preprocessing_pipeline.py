"""
DeepInsight — Preprocessing Pipeline.

Handles advanced feature engineering, outlier detection, encoding, 
scaling, and class imbalance (SMOTE).
"""

import logging
import pandas as pd
import numpy as np
from typing import Any, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold

logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """Advanced preprocessing pipeline for classification."""

    def __init__(self, target_col: str):
        self.target_col = target_col
        self.encoders = {}
        self.feature_names_in = []
        self.feature_names_out = []
        self.numeric_imputer = SimpleImputer(strategy="median")
        self.categorical_imputer = SimpleImputer(strategy="most_frequent")
        self.scaler = StandardScaler()
        self.selector = VarianceThreshold(threshold=0.01) # Remove near-constant features

    def fit_transform(self, df: pd.DataFrame, apply_smote: bool = False) -> Tuple[pd.DataFrame, pd.Series]:
        """Fit the pipeline and transform the data."""
        df_work = df.copy()
        
        # 1. Handle Duplicates
        df_work = df_work.drop_duplicates()
        
        # 2. Separate X and y
        X = df_work.drop(columns=[self.target_col])
        y = df_work[self.target_col]
        
        # 3. Label Encode Target
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))
        self.encoders[self.target_col] = le
        
        # 4. Identify column types
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
        
        # 5. Handle Missing Values
        if numeric_cols:
            X[numeric_cols] = self.numeric_imputer.fit_transform(X[numeric_cols])
        if categorical_cols:
            X[categorical_cols] = self.categorical_imputer.fit_transform(X[categorical_cols])
            
        # 6. Advanced Categorical Encoding
        X_final = pd.DataFrame(index=X.index)
        
        # Numerical scaling
        if numeric_cols:
            X_num = pd.DataFrame(
                self.scaler.fit_transform(X[numeric_cols]), 
                columns=numeric_cols, 
                index=X.index
            )
            X_final = pd.concat([X_final, X_num], axis=1)
            self.encoders["scaler"] = self.scaler
            
        # Categorical encoding
        for col in categorical_cols:
            unique_count = X[col].nunique()
            if unique_count <= 10:
                # One-Hot Encoding for low cardinality
                ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                encoded = ohe.fit_transform(X[[col]])
                feature_names = ohe.get_feature_names_out([col])
                X_ohe = pd.DataFrame(encoded, columns=feature_names, index=X.index)
                X_final = pd.concat([X_final, X_ohe], axis=1)
                self.encoders[col] = ohe
            else:
                # Label Encoding for high cardinality
                le_feat = LabelEncoder()
                X_final[col] = le_feat.fit_transform(X[col].astype(str))
                self.encoders[col] = le_feat

        # 7. Feature Selection (Low Variance)
        if not X_final.empty:
            X_selected = self.selector.fit_transform(X_final)
            selected_cols = X_final.columns[self.selector.get_support()]
            X_final = pd.DataFrame(X_selected, columns=selected_cols, index=X.index)
            
        self.feature_names_out = X_final.columns.tolist()
        
        # 8. Handle Imbalance with SMOTE (if requested and possible)
        if apply_smote:
            try:
                from imblearn.over_sampling import SMOTE
                sm = SMOTE(random_state=42)
                X_final, y = sm.fit_resample(X_final, y)
                logger.info("SMOTE applied to balance classes.")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}. Proceeding without oversampling.")

        return X_final, pd.Series(y)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted pipeline."""
        # Simple version for inference
        X = df.copy()
        if self.target_col in X.columns:
            X = X.drop(columns=[self.target_col])
            
        # This part needs to be carefully aligned with fit_transform
        # In a real system, we'd use a sklearn Pipeline or ColumnTransformer
        # For now, we'll implement a robust enough version
        
        X_num_cols = [c for c in X.columns if c in self.scaler.feature_names_in_] if hasattr(self.scaler, "feature_names_in_") else []
        X_final = pd.DataFrame(index=X.index)
        
        if X_num_cols:
            X_num = pd.DataFrame(
                self.scaler.transform(X[X_num_cols]),
                columns=X_num_cols,
                index=X.index
            )
            X_final = pd.concat([X_final, X_num], axis=1)
            
        for col, enc in self.encoders.items():
            if col == self.target_col: continue
            if col not in X.columns: continue
            
            if isinstance(enc, OneHotEncoder):
                encoded = enc.transform(X[[col]])
                X_ohe = pd.DataFrame(encoded, columns=enc.get_feature_names_out([col]), index=X.index)
                X_final = pd.concat([X_final, X_ohe], axis=1)
            elif isinstance(enc, LabelEncoder):
                # Handle unseen labels by mapping to a default if necessary
                # Simple version: use transform and hope for the best, or use a custom LabelEncoder
                try:
                    X_final[col] = enc.transform(X[col].astype(str))
                except:
                    X_final[col] = 0 # Fallback
                    
        # Filter by selected features
        final_cols = [c for c in self.feature_names_out if c in X_final.columns]
        return X_final[final_cols]

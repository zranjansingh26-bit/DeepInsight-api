import asyncio
import pandas as pd
import numpy as np
from engines.ml_engine import AutoMLPipeline

def test_automl():
    # Create synthetic classification dataset
    data = {
        'age': np.random.randint(20, 60, 100),
        'salary': np.random.randint(30000, 100000, 100),
        'purchased': np.random.randint(0, 2, 100)
    }
    df = pd.DataFrame(data)
    
    print("Running AutoML for Classification...")
    pipeline = AutoMLPipeline(df, target_col='purchased')
    results = pipeline.run()
    
    print(f"Best Model: {results['best_model_name']}")
    print(f"Best Metrics: {results['best_metrics']}")
    
    # Create synthetic regression dataset
    data_reg = {
        'size': np.random.randint(500, 3000, 100),
        'rooms': np.random.randint(1, 6, 100),
        'price': np.random.randint(100000, 500000, 100)
    }
    df_reg = pd.DataFrame(data_reg)
    
    print("\nRunning AutoML for Regression...")
    pipeline_reg = AutoMLPipeline(df_reg, target_col='price')
    results_reg = pipeline_reg.run()
    
    print(f"Best Model: {results_reg['best_model_name']}")
    print(f"Best Metrics: {results_reg['best_metrics']}")

if __name__ == "__main__":
    test_automl()

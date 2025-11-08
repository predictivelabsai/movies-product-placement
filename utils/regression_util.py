import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


def _prepare_feature_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Build a feature matrix X and label vector y from the movies dataframe.
    - Creates multi-hot genre columns from the 'genres' list column
    - One-hot encodes categorical columns
    - Returns X, y, and the final feature column names
    """
    df_local = df.copy()
    # Normalize genres column to lists
    genre_lists = df_local["genres"].apply(lambda x: x if isinstance(x, list) else [])
    genre_set = sorted({g for gs in genre_lists for g in gs})
    for g in genre_set:
        df_local[f"genre_{g}"] = genre_lists.apply(lambda gs, gg=g: 1 if gg in gs else 0)

    base_cols = [
        "runtime", "vote_average", "vote_count", "popularity", "budget", "release_year",
        "cast_popularity_top3", "director_popularity"
    ]
    cat_cols = ["region", "original_language", "primary_genre"]

    # Ensure presence of expected columns
    for col in base_cols + cat_cols:
        if col not in df_local.columns:
            df_local[col] = np.nan if col in base_cols else "UNK"

    # Build X and y
    genre_cols = [c for c in df_local.columns if c.startswith("genre_")]
    X = df_local[base_cols + cat_cols + genre_cols].copy()
    X = pd.get_dummies(X, columns=cat_cols, dummy_na=True)
    y = df_local["box_office"].astype(float)

    # Drop rows with missing y or all-NaN features
    valid = y.notna()
    X = X.loc[valid]
    y = y.loc[valid]
    X = X.fillna(0)

    return {
        "X": X,
        "y": y,
        "feature_columns": list(X.columns)
    }


def run_random_forest_importance(
    df: pd.DataFrame,
    n_estimators: int = 400,
    max_depth: int = 12,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Train a RandomForestRegressor and compute feature importances.
    Returns:
    - feature_importances (pd.Series, sorted desc)
    - feature_columns (list)
    - r2_train, r2_test (floats)
    """
    prepared = _prepare_feature_matrix(df)
    X, y = prepared["X"], prepared["y"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    feature_importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    return {
        "feature_importances": feature_importances,
        "feature_columns": list(X.columns),
        "r2_train": float(model.score(X_train, y_train)),
        "r2_test": float(model.score(X_test, y_test)),
    }



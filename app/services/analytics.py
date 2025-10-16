from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class StatsSummary:
    count: int
    mean: float
    std: float
    min: float
    max: float


def compute_summary(series: pd.Series) -> StatsSummary:
    clean = series.dropna()
    if clean.empty:
        return StatsSummary(count=0, mean=0.0, std=0.0, min=0.0, max=0.0)
    
    mean_val = clean.mean()
    std_val = clean.std(ddof=1) if clean.count() > 1 else 0.0
    min_val = clean.min()
    max_val = clean.max()
    
    # Verificar se os valores são válidos (não NaN)
    mean_val = 0.0 if np.isnan(mean_val) else float(mean_val)
    std_val = 0.0 if np.isnan(std_val) else float(std_val)
    min_val = 0.0 if np.isnan(min_val) else float(min_val)
    max_val = 0.0 if np.isnan(max_val) else float(max_val)
    
    return StatsSummary(
        count=int(clean.count()),
        mean=mean_val,
        std=std_val,
        min=min_val,
        max=max_val,
    )


def linear_regression(x: pd.Series, y: pd.Series) -> dict[str, float]:
    mask = ~(x.isna() | y.isna())
    x_vals = x[mask].to_numpy()
    y_vals = y[mask].to_numpy()
    if x_vals.size == 0:
        return {"slope": 0.0, "intercept": 0.0, "r2": 0.0}
    # Ajuste linear simples via polyfit
    slope, intercept = np.polyfit(x_vals, y_vals, 1)
    y_pred = slope * x_vals + intercept
    ss_res = float(np.sum((y_vals - y_pred) ** 2))
    ss_tot = float(np.sum((y_vals - np.mean(y_vals)) ** 2))
    r2 = 0.0 if ss_tot == 0.0 else 1.0 - (ss_res / ss_tot)
    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def six_sigma_params(series: pd.Series) -> dict[str, float]:
    clean = series.dropna()
    if clean.empty:
        return {"mean": 0.0, "std": 0.0, "cpk": 0.0}
    
    mean_val = clean.mean()
    std_val = clean.std(ddof=1) if clean.count() > 1 else 0.0
    
    # Verificar se os valores são válidos (não NaN)
    mean_val = 0.0 if np.isnan(mean_val) else float(mean_val)
    std_val = 0.0 if np.isnan(std_val) else float(std_val)
    
    # Cpk depende de limites especificados; como placeholder, considerar LSL/USL +/- 3 sigma
    if std_val == 0.0:
        cpk = 0.0
    else:
        usl = mean_val + 3 * std_val
        lsl = mean_val - 3 * std_val
        cpk = min((usl - mean_val) / (3 * std_val), (mean_val - lsl) / (3 * std_val))
        cpk = 0.0 if np.isnan(cpk) else float(cpk)
    
    return {"mean": mean_val, "std": std_val, "cpk": cpk}


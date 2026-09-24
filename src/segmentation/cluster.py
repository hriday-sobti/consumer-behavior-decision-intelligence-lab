"""Behavioral clustering, evaluation, and segment profiling module.

Implements:
- Skew inspection & log1p transformation of right-skewed features
- Robust feature scaling
- Primary clustering feature set:
    log_total_value
    log_transaction_count
    recency_days
    log_product_count
    mean_interpurchase_days
    value_momentum_pct
    frequency_momentum_pct
- Evaluation over K in (3, 4, 5, 6)
- Selection rule: smallest K with silhouette >= 90% of best, min cluster size >= 5%
- Deterministic behavior-based segment profiling & naming
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.config import analytical_config
from src.logging_config import logger

FEATURE_COLS = [
    "log_total_value",
    "log_transaction_count",
    "recency_days",
    "log_product_count",
    "mean_interpurchase_days",
    "value_momentum_pct",
    "frequency_momentum_pct"
]

def prepare_clustering_features(features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Filters eligible customers and computes standardized primary clustering features."""
    logger.info("Preparing and transforming clustering feature set for eligible customers...")
    eligible_df = features_df[~features_df["insufficient_history"]].copy().reset_index(drop=True)

    # Feature engineering for clustering
    # Cap analytical extreme outliers on momentum at [-1.0, 5.0] to prevent distortion
    val_mom = eligible_df["value_change_pct"].clip(-1.0, 5.0).fillna(0.0)
    freq_mom = eligible_df["frequency_change_pct"].clip(-1.0, 5.0).fillna(0.0)
    
    # Interpurchase days: fill missing (if any) with median
    inter_days = eligible_df["mean_interpurchase_days"].fillna(eligible_df["mean_interpurchase_days"].median())

    trans_df = pd.DataFrame({
        "customer_id": eligible_df["customer_id"],
        "log_total_value": np.log1p(np.maximum(0, eligible_df["total_value"].values)),
        "log_transaction_count": np.log1p(np.maximum(0, eligible_df["transaction_count"].values)),
        "recency_days": eligible_df["recency_days"].values,
        "log_product_count": np.log1p(np.maximum(0, eligible_df["product_count"].values)),
        "mean_interpurchase_days": inter_days.values,
        "value_momentum_pct": val_mom.values,
        "frequency_momentum_pct": freq_mom.values
    })

    scaler = StandardScaler()
    scaled_matrix = scaler.fit_transform(trans_df[FEATURE_COLS])
    scaled_df = pd.DataFrame(scaled_matrix, columns=FEATURE_COLS)
    scaled_df["customer_id"] = trans_df["customer_id"]

    return eligible_df, trans_df, scaled_df, scaler


def evaluate_clusters(scaled_df: pd.DataFrame, k_range: tuple = (3, 4, 5, 6), seed: int = 42) -> tuple[int, pd.DataFrame]:
    """Evaluates K-Means across k_range using inertia, silhouette score, and min cluster share."""
    logger.info(f"Evaluating clustering models for K in {k_range} (seed={seed})...")
    X = scaled_df[FEATURE_COLS].values
    results = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10)
        labels = kmeans.fit_predict(X)
        
        inertia = kmeans.inertia_
        sil = silhouette_score(X, labels)
        
        counts = pd.Series(labels).value_counts()
        min_share = float(counts.min() / len(labels))
        
        results.append({
            "k": k,
            "inertia": round(inertia, 2),
            "silhouette_score": round(sil, 4),
            "min_cluster_size": int(counts.min()),
            "min_cluster_share": round(min_share, 4),
            "meets_5pct_rule": min_share >= analytical_config.min_cluster_share
        })
        logger.info(f"K={k}: Silhouette={sil:.4f}, Inertia={inertia:.2f}, Min Cluster Share={min_share*100:.2f}%")

    eval_df = pd.DataFrame(results)
    
    # Model selection rule:
    # Smallest K whose silhouette is >= 90% of best, provided min cluster share >= 5%
    best_sil = eval_df["silhouette_score"].max()
    threshold_sil = best_sil * analytical_config.silhouette_relative_threshold
    
    eligible_k = eval_df[eval_df["meets_5pct_rule"] & (eval_df["silhouette_score"] >= threshold_sil)]
    if not eligible_k.empty:
        selected_k = int(eligible_k["k"].min())
        logger.info(f"Selection Rule chose K={selected_k} (Silhouette >= 90% of {best_sil:.4f} and min share >= 5%).")
    else:
        # Fallback to highest silhouette
        selected_k = int(eval_df.loc[eval_df["silhouette_score"].idxmax()]["k"])
        logger.warning(f"No K strictly met the 5% rule; selected K={selected_k} with highest silhouette.")

    return selected_k, eval_df


def fit_behavioral_segments(
    eligible_df: pd.DataFrame,
    trans_df: pd.DataFrame,
    scaled_df: pd.DataFrame,
    selected_k: int,
    seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fits final K-Means model, profiles segments behaviorally, and assigns descriptive names."""
    logger.info(f"Fitting final K-Means with K={selected_k}...")
    X = scaled_df[FEATURE_COLS].values
    kmeans = KMeans(n_clusters=selected_k, random_state=seed, n_init=10)
    labels = kmeans.fit_predict(X)

    clustered_df = eligible_df.copy()
    clustered_df["segment_id"] = labels
    for col in FEATURE_COLS:
        clustered_df[col] = trans_df[col]

    # Calculate distance to cluster center
    centers = kmeans.cluster_centers_
    distances = np.linalg.norm(X - centers[labels], axis=1)
    clustered_df["distance_to_center"] = np.round(distances, 4)

    # Behavioral profiling
    total_pop = len(clustered_df)
    total_val_all = clustered_df["total_value"].sum()

    # Temporary storage for ranking
    seg_stats = {}

    for sid in range(selected_k):
        sdf = clustered_df[clustered_df["segment_id"] == sid]
        cnt = len(sdf)
        c_share = cnt / total_pop
        tot_val = sdf["total_value"].sum()
        v_share = tot_val / total_val_all if total_val_all > 0 else 0.0

        med_val = sdf["total_value"].median()
        med_rec = sdf["recency_days"].median()
        med_freq = sdf["transaction_count"].median()
        med_breadth = sdf["product_count"].median()
        med_gap = sdf["mean_interpurchase_days"].median()
        med_vmom = sdf["value_momentum_pct"].median()
        med_fmom = sdf["frequency_momentum_pct"].median()
        med_stab = sdf["interpurchase_gap_cv"].median() if "interpurchase_gap_cv" in sdf.columns else 0.0
        rev_rate = sdf["reversal_rate"].mean()

        seg_stats[sid] = {
            "cnt": cnt, "c_share": c_share, "tot_val": tot_val, "v_share": v_share,
            "med_val": med_val, "med_rec": med_rec, "med_freq": med_freq,
            "med_breadth": med_breadth, "med_gap": med_gap,
            "med_vmom": med_vmom, "med_fmom": med_fmom, "med_stab": med_stab,
            "rev_rate": rev_rate
        }

    # Assign descriptive business names based on measured behaviors (not cluster IDs)
    # Rules based on value, recency, momentum, frequency
    named_segments = {}
    for sid, st in seg_stats.items():
        if st["med_rec"] > 180:
            name = "Low-Activity / Long-Recency"
            prim = "Extended inactivity with high elapsed days since last order."
            sec = "Low historical order frequency and catalog breadth."
            interp = "Customers who transacted historically but have not placed orders in over two quarters."
            q = "What proportion of these accounts represent seasonal buyers vs lost accounts?"
        elif st["med_val"] >= 2500 or st["med_freq"] >= 10:
            if st["med_vmom"] <= -0.15:
                name = "High-Value Softening"
                prim = "High cumulative spend and order counts with negative recent momentum."
                sec = "Substantial contraction in recent 90-day order volume."
                interp = "Core valuable accounts exhibiting marked decelerations in purchasing cadence."
                q = "Which high-tier product categories experienced the largest reduction in basket volume?"
            else:
                name = "High-Value Stable"
                prim = "Sustained high transaction frequency and strong historical monetary value."
                sec = "Consistent repeat order intervals with balanced recent momentum."
                interp = "Commercial and bulk repeat buyers generating the core of transaction volume."
                q = "What delivery and contract terms best protect operational satisfaction for these accounts?"
        elif st["med_vmom"] >= 0.15 or st["med_fmom"] >= 0.15:
            name = "Emerging Engagement"
            prim = "Moderate historical volume with positive recent velocity."
            sec = "Expanding product breadth and frequent recent basket placement."
            interp = "Accounts actively scaling their transaction activity across recent 90-day windows."
            q = "What complementary categories can be introduced during this active expansion phase?"
        else:
            name = "Moderate-Value Regular"
            prim = "Predictable periodic purchasing with mid-tier basket sizes."
            sec = "Steady interpurchase intervals and steady product variety."
            interp = "Reliable repeat customers maintaining stable operational reorders."
            q = "Are replenishment cycles predictable enough to introduce scheduled replenishment?"

        named_segments[sid] = (name, prim, sec, interp, q)

    # Ensure unique names if ties happen
    used_names = {}
    final_names = {}
    for sid, (name, prim, sec, interp, q) in named_segments.items():
        if name in used_names:
            suffix = used_names[name] + 1
            used_names[name] = suffix
            assigned_name = f"{name} Tier {suffix}"
        else:
            used_names[name] = 1
            assigned_name = name
        final_names[sid] = (assigned_name, prim, sec, interp, q)

    # Build final profile rows
    profile_rows = []
    for sid, st in seg_stats.items():
        aname, prim, sec, interp, q = final_names[sid]
        profile_rows.append({
            "segment_id": sid,
            "segment_name": aname,
            "customer_count": st["cnt"],
            "customer_share": round(st["c_share"], 4),
            "total_value": round(st["tot_val"], 4),
            "value_share": round(st["v_share"], 4),
            "median_value": round(st["med_val"], 4),
            "median_recency": int(st["med_rec"]),
            "median_frequency": int(st["med_freq"]),
            "median_product_breadth": int(st["med_breadth"]),
            "median_interpurchase_gap": round(st["med_gap"], 2) if pd.notna(st["med_gap"]) else 0.0,
            "median_value_momentum": round(st["med_vmom"], 4),
            "median_frequency_momentum": round(st["med_fmom"], 4),
            "median_stability": round(st["med_stab"], 4) if pd.notna(st["med_stab"]) else 0.0,
            "reversal_rate": round(st["rev_rate"], 4),
            "primary_behavior": prim,
            "secondary_behavior": sec,
            "interpretation": interp,
            "possible_business_question": q
        })

    profile_df = pd.DataFrame(profile_rows).sort_values("total_value", ascending=False).reset_index(drop=True)
    
    # Map segment names back to clustered dataframe
    name_map = {sid: final_names[sid][0] for sid in range(selected_k)}
    clustered_df["segment_name"] = clustered_df["segment_id"].map(name_map)

    logger.info(f"Segment profiling completed for {selected_k} behavioral segments.")
    return clustered_df, profile_df

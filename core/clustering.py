from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def add_student_clusters(df):
    feature_cols = [
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "TOTAL_SCORE"
    ]

    available_cols = [
        col for col in feature_cols
        if col in df.columns
    ]

    if len(available_cols) < 2:
        df["CLUSTER"] = 0
        return df

    # not enough students for clustering
    if len(df) < 2:
        df["CLUSTER"] = 0
        return df

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[available_cols])

    # dynamic safe clusters
    n_clusters = min(3, len(df))

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    df["CLUSTER"] = model.fit_predict(scaled)

    return df

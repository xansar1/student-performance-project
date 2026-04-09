from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


CLUSTER_FEATURES = [
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE"
]


def add_student_clusters(df, n_clusters=3):
    """
    Add ML-based performance clusters to student dataframe.
    """
    df = df.copy()

    features = df[CLUSTER_FEATURES]
    scaled = StandardScaler().fit_transform(features)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    df["CLUSTER"] = model.fit_predict(scaled)

    return df

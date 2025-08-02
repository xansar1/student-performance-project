
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def perform_clustering(data, n_clusters=3):
    numeric_data = data.select_dtypes(include='number')
    if numeric_data.empty:
        raise ValueError("No numeric columns found for clustering.")
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_data)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)
    
    return clusters

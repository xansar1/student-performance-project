import pandas as pd
import numpy as np

def clean_data(uploaded_file):
    df = pd.read_csv(uploaded_file)

    df.columns = [col.strip().replace(" ", "_").upper() for col in df.columns]

    if "SEMESTER" not in df.columns:
        df["SEMESTER"] = np.random.choice(
            ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
            size=len(df)
        )

    return df

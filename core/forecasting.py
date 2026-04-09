from sklearn.linear_model import LinearRegression


FEATURES = [
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE"
]


def train_forecast_model(df):
    """
    Train MVP next-semester forecasting model.
    """
    model_df = df.copy()

    # weak target assumption:
    # next semester ≈ current + momentum bias
    model_df["NEXT_SEM_TARGET"] = (
        model_df["TOTAL_SCORE"] * 0.85
        + model_df["DOMAIN_SCORE"] * 0.10
        + model_df["GENERAL_SCORE"] * 0.05
    )

    X = model_df[FEATURES]
    y = model_df["NEXT_SEM_TARGET"]

    model = LinearRegression()
    model.fit(X, y)

    return model


def add_next_semester_forecast(df):
    """
    Add next semester predicted score.
    """
    df = df.copy()

    model = train_forecast_model(df)

    predicted = model.predict(df[FEATURES])
    df["NEXT_SEM_PREDICTION"] = predicted.round(2)

    return df

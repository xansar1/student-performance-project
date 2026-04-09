def apply_academic_filters(
    df,
    selected_university,
    selected_program
):
    """
    Filter dataframe by university and program.
    """
    filtered_df = df[
        (df["UNIVERSITY"].isin(selected_university)) &
        (df["PROGRAM"].isin(selected_program))
    ].copy()

    return filtered_df


def validate_filtered_data(df):
    """
    Prevent downstream analytics errors on empty data.
    """
    if df.empty:
        raise ValueError("No students match selected filters.")

    return df

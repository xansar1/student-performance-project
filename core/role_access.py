def apply_role_college_filter(df, user_info):
  if user_info["college"] == "ALL":
    return df

  return df[df["UNIVERSITY"] == user_info["college"]]

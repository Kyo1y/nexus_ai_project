import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> None:
    df.rename(columns=lambda x: x.replace(' ', '_').replace('-', '_').lower(), inplace=True)

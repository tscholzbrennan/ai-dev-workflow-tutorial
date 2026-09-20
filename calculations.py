from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]

NUMERIC_COLUMNS = ["quantity", "unit_price", "total_amount"]


def load_data(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        raise ValueError(f"Could not find data file: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    try:
        df["date"] = pd.to_datetime(df["date"])
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Could not parse 'date' column: {exc}") from exc

    for col in NUMERIC_COLUMNS:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Could not parse '{col}' column as numeric: {exc}") from exc

    return df


def compute_total_sales(df: pd.DataFrame) -> float:
    return float(df["total_amount"].sum())


def compute_total_orders(df: pd.DataFrame) -> int:
    return len(df)

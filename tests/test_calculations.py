import pandas as pd
import pytest

from calculations import compute_total_orders, compute_total_sales, load_data, sales_by_month


def _sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-15", "2024-01-20", "2024-02-05", "2024-02-10"]),
        "category": ["Electronics", "Audio", "Electronics", "Accessories"],
        "region": ["North", "South", "North", "West"],
        "total_amount": [100.0, 50.0, 200.0, 25.0],
    })


def test_load_data_raises_on_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.csv"
    with pytest.raises(ValueError, match="Could not find data file"):
        load_data(str(missing_path))


def test_load_data_raises_on_missing_column(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "date,order_id,product,region,quantity,unit_price,total_amount\n"
        "2024-01-15,ORD-1,Widget,North,1,10.0,10.0\n"
    )
    with pytest.raises(ValueError, match="Missing required column"):
        load_data(str(csv_path))


def test_load_data_returns_dataframe_with_parsed_types(tmp_path):
    csv_path = tmp_path / "good.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-15,ORD-1,Widget,Electronics,North,2,5.0,10.0\n"
    )
    df = load_data(str(csv_path))
    assert len(df) == 1
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df.loc[0, "total_amount"] == 10.0


def test_compute_total_sales():
    df = _sample_df()
    assert compute_total_sales(df) == 375.0


def test_compute_total_orders():
    df = _sample_df()
    assert compute_total_orders(df) == 4


def test_sales_by_month():
    df = _sample_df()
    result = sales_by_month(df)
    assert list(result["month"]) == ["2024-01", "2024-02"]
    assert list(result["total_amount"]) == [150.0, 225.0]

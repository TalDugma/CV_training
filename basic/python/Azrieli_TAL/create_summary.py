import os
import typing
import pandas as pd
import numpy as np
from tqdm import tqdm

# from tqdm import tqdm
from collections import Counter, defaultdict
import itertools
from datetime import datetime
from utils import *
from pathlib import Path

# pd.set_option("future.no_silent_downcasting", True)

MEAN_VELOCITY = 75.75
WEEKEND_START = (6, 16)
WEEKEND_END = (7, 20)
NIGHT_START = 22
NIGHT_END = 6


DATA_PATH = Path("Azrieli_TAL/data")


def fill_missing_taarifs(taarifs: pd.DataFrame, unknown_companies: list[str]):
    def add_missing_customers(taarifs, unknown_companies, per_column_mean):
        for company in unknown_companies:
            taarifs.loc[len(taarifs)] = {"customer": company} | per_column_mean

    cols = taarifs.columns
    cols = [col for col in cols if col != "customer"]
    per_column_mean = {col: taarifs[col].mean() for col in cols}
    add_missing_customers(taarifs, unknown_companies, per_column_mean)
    taarifs = taarifs.fillna(value=per_column_mean)
    return taarifs


#  NOTE original
# def fill_payments(
#     summary_df: pd.DataFrame, taarifs: pd.DataFrame, trips_path=DATA_PATH / "trips_data"
# ):
#     for trip_name in tqdm(os.listdir(trips_path), desc="Processing trips"):
#         df = pd.read_csv(trips_path / trip_name)
#         month = process_month(trip_name.split("_")[0])
#         for index, row in df.iterrows():
#             payment = calculate_drive_payment(row, taarifs)
#             driver_id = row["driver_id"]
#             mask = (summary_df["Month"] == month) & (
#                 summary_df["Driver_id"] == driver_id
#             )
#             current_income = summary_df.loc[mask, "Total_income"].item()
#             if pd.isna(current_income):
#                 current_income = 0
#             summary_df.loc[mask, "Total_income"] = current_income + payment
#     return summary_df


# NOTE v3
def fill_payments(
    summary_df: pd.DataFrame,
    taarifs: pd.DataFrame,
    trips_path=DATA_PATH / "trips_data_processed",
):
    for trip_name in tqdm(os.listdir(trips_path), desc="Processing trips"):
        df = pd.read_csv(trips_path / trip_name)
        month = process_month(trip_name.split("_")[0])

        # Compute payment per row
        df["Payment"] = df.apply(lambda r: calculate_drive_payment(r, taarifs), axis=1)

        # Aggregate by driver for this month
        df_summary = (
            df.groupby("driver_id")[["Payment", "km"]]
            .sum()
            .reset_index()
            # .rename(columns={"km": "Total_km"})
        )
        df_summary["Month"] = month

        # Merge once with summary
        summary_df = summary_df.merge(
            df_summary,
            how="left",
            left_on=["Driver_id", "Month"],
            right_on=["driver_id", "Month"],
        )

        # Update totals safely (handle NaN)
        summary_df["Total_income"] = summary_df["Total_income"].fillna(0) + summary_df[
            "Payment"
        ].fillna(0)
        summary_df["Total_km"] = summary_df["Total_km"].fillna(0) + summary_df[
            "km"
        ].fillna(0)

        # Clean up extra columns
        summary_df = summary_df.drop(
            columns=["driver_id", "Payment", "km"], errors="ignore"
        )

    return summary_df


# NOTE v2
# def fill_payments(
#     summary_df: pd.DataFrame, taarifs: pd.DataFrame, trips_path=DATA_PATH / "trips_data"
# ):
#     # ✅ 1. Make Month + Driver_id the index for O(1) lookups
#     if not summary_df.index.names == ["Month", "Driver_id"]:
#         summary_df = summary_df.set_index(["Month", "Driver_id"])

#     # ✅ 2. Temporary accumulator for faster updates
#     income_accumulator = defaultdict(float)

#     # ✅ 3. Iterate efficiently over trip files
#     for trip_name in tqdm(os.listdir(trips_path), desc="Processing trips"):
#         df = pd.read_csv(trips_path / trip_name)
#         month = process_month(trip_name.split("_")[0])

#         # ✅ 4. Use itertuples() instead of iterrows()
#         for row in df.itertuples(index=False):
#             payment = calculate_drive_payment(pd.Series(row._asdict()), taarifs)
#             driver_id = row.driver_id
#             income_accumulator[(month, driver_id)] += payment

#     # ✅ 5. Apply accumulated results back in one vectorized step
#     for key, payment_sum in income_accumulator.items():
#         if key in summary_df.index:
#             current_income = summary_df.at[key, "Total_income"]
#             if pd.isna(current_income):
#                 current_income = 0
#             summary_df.at[key, "Total_income"] = current_income + payment_sum

#     return summary_df.reset_index()


def calculate_drive_payment(drive: pd.Series, taarifs: pd.DataFrame):
    km = drive["km"]
    customer = drive["customer"]
    start_time = time_to_datetime(drive["start_time"])
    end_time = time_to_datetime(drive["end_time"])
    start_time, end_time = fill_empty_times(km, start_time, end_time, MEAN_VELOCITY)
    if start_time == None and end_time == None:
        return 0
    basic_interval, extra_interval = get_basic_and_extra_milage_intervals(
        km, start_time, end_time, MEAN_VELOCITY
    )
    basic_weekend_time = get_intersection_with_weekend(
        basic_interval[1][0], basic_interval[1][1]
    )
    basic_night_time = get_intersection_with_night(
        basic_interval[1][0], basic_interval[1][1]
    )
    extra_weekend_time = get_intersection_with_weekend(
        extra_interval[1][0], extra_interval[1][1]
    )
    extra_night_time = get_intersection_with_night(
        extra_interval[1][0], extra_interval[1][1]
    )
    taarifs = taarifs[taarifs["customer"] == customer]
    basic_interval_length = get_inetrval_length_hours(basic_interval[1])
    extra_interval_length = get_inetrval_length_hours(extra_interval[1])

    basic_payment = (
        apply_bonuses(
            taarifs,
            taarifs["basic_taarif"],
            basic_interval[0],
            basic_night_time / basic_interval_length,
            basic_weekend_time / basic_interval_length,
        )
        if basic_interval_length != 0
        else 0
    )
    extra_payment = (
        apply_bonuses(
            taarifs,
            taarifs["extra_milage"],
            extra_interval[0],
            extra_night_time / extra_interval_length,
            extra_weekend_time / extra_interval_length,
        )
        if extra_interval_length != 0
        else 0
    )
    return extra_payment + basic_payment


def get_unique_months(trips: list):
    raw_months = np.unique([trip.split("_")[0] for trip in trips])
    months = [process_month(raw_month) for raw_month in raw_months]
    return months


def create_trips_dict(trips_path: Path):

    trips = {}
    filtered_trips = remove_duplicate_trips(os.listdir(trips_path))
    for trip_name in filtered_trips:
        trips[trip_name] = pd.read_csv(trips_path / trip_name)
    return trips


def fill_dry_driver_information(
    summary_df: pd.DataFrame,
    drivers_with_kviut: pd.DataFrame,
    new_drivers: pd.DataFrame,
):
    drivers_genders = get_drivers_genders(drivers_with_kviut, new_drivers)
    drivers_ages = get_drivers_age(drivers_with_kviut, new_drivers)
    drivers_vetek = get_drivers_vetek(drivers_with_kviut, new_drivers)
    for i, driver in enumerate(summary_df["Driver_id"]):
        summary_df.loc[i, "Gender"] = drivers_genders[driver]
        summary_df.loc[i, "Age"] = drivers_ages[driver]
        summary_df.loc[i, "Vetek"] = drivers_vetek[driver]

    return summary_df


# def get_all_driver_ids(trips_path="Azrieli_TAL/data/trips_data", driver ):
#     for


def get_all_drivers(new_drivers: pd.DataFrame, drivers_with_kviut: pd.DataFrame):
    new_drivers_ids = new_drivers["id"].tolist()
    drivers_with_kviut_ids = drivers_with_kviut["id"].tolist()
    return new_drivers_ids + drivers_with_kviut_ids


def fill_drviers_and_months(
    summary_df: pd.DataFrame, drivers: list[str], months: list[str]
):
    # Create all possible combinations
    all_pairs = pd.DataFrame(
        list(itertools.product(months, drivers)), columns=["Month", "Driver_id"]
    )

    # Merge with existing data (if you already have partial entries)
    filled_df = pd.merge(all_pairs, summary_df, on=["Month", "Driver_id"], how="left")

    return filled_df


def main():
    drivers_with_kviut = pd.read_csv(
        DATA_PATH / "Drivers_with_kviut.csv", quotechar='"', skipinitialspace=True
    )

    new_drivers = pd.read_csv(
        DATA_PATH / "new_drivers.csv", quotechar='"', skipinitialspace=True
    )
    taarifs = pd.read_csv(
        DATA_PATH / "taarif_updated.csv", quotechar='"', skipinitialspace=True
    )
    drivers_with_kviut, new_drivers, taarifs = (
        preprocess_df(drivers_with_kviut),
        preprocess_df(new_drivers),
        preprocess_df(taarifs),
    )
    trips = remove_duplicate_trips(os.listdir(DATA_PATH / "trips_data_processed"))
    months = get_unique_months(trips)
    drivers = get_all_drivers(new_drivers, drivers_with_kviut)
    companies = taarifs["customer"].tolist()
    taarifs = fill_missing_taarifs(
        taarifs, get_unkown_companies(companies, trips, DATA_PATH)
    )
    summary_df = pd.DataFrame(
        columns=[
            "Driver_id",
            "Month",
            "Total_income",
            "Total_km",
            "Gender",
            "Age",
            "Vetek",
        ]
    )
    summary_df = fill_drviers_and_months(summary_df, drivers, months)
    summary_df = fill_dry_driver_information(
        summary_df, drivers_with_kviut, new_drivers
    )

    summary_df = fill_payments(summary_df, taarifs)
    summary_df.to_csv(Path("Azrieli_TAL") / "output.csv")


if __name__ == "__main__":
    main()

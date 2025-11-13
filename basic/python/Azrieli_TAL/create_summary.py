import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import Counter
import itertools
from datetime import datetime
from utils import *
from pathlib import Path


DATA_PATH = Path("Azrieli_TAL/data")


def get_unique_months(trips: list):
    def process_month(raw_month: str):
        month_name, year = raw_month.split(" ")[0], raw_month.split(" ")[1]
        month = datetime.strptime(f"{month_name} {year}", "%B %Y").strftime("%m/%Y")
        return month

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
    taarif = pd.read_csv(DATA_PATH / "taarif.csv", quotechar='"', skipinitialspace=True)
    drivers_with_kviut, new_drivers, taarif = (
        preprocess_df(drivers_with_kviut),
        preprocess_df(new_drivers),
        preprocess_df(taarif),
    )
    # taarif = fill_missing_taarifs(taarif)
    trips = remove_duplicate_trips(os.listdir(DATA_PATH / "trips_data"))
    months = get_unique_months(trips)
    drivers = get_all_drivers(new_drivers, drivers_with_kviut)
    companies = taarif["customer"].tolist()
    print(get_unkown_companies(companies, trips, DATA_PATH))
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

    # summary_df = fill_drives_info(su)
    summary_df.to_csv(Path("Azrieli_TAL") / "output.csv")


if __name__ == "__main__":
    main()

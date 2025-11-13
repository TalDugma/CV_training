import pandas as pd
from datetime import datetime
from pathlib import Path


def get_unkown_companies(companies: list, trips: list, data_path: Path):
    new_customers = []
    for trip in trips:
        df = pd.read_csv(data_path / "trips_data" / trip)
        for customer in df["customer"].tolist():
            if customer not in companies:
                if customer not in new_customers:
                    new_customers.append(customer)
    return new_customers


# def fill_missing_taarifs(taarif: pd.DataFrame):
#     missin_companies = ['yes', 'aminach', 'hot']
#     per_column_mean =
#     for i, company in enumerate(taarif["customer"]):
#         if


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    def clean_columns(df: pd.DataFrame):
        df.columns = df.columns.str.replace(" ", "")
        return df

    df = clean_columns(df)
    return df


def remove_duplicate_trips(full_trip_names_list: list):
    return [trip_name for trip_name in full_trip_names_list if "(2)" not in trip_name]


def get_drivers_genders(drivers_with_kviut: pd.DataFrame, new_drivers: pd.DataFrame):
    drivers_genders = {}

    for i, driver in enumerate(new_drivers["id"]):
        drivers_genders[driver] = new_drivers["gender"][i]

    for i, driver in enumerate(drivers_with_kviut["id"]):
        if driver in drivers_genders:
            raise ValueError("Driver duplicate", driver)
        else:
            drivers_genders[driver] = drivers_with_kviut["gender"][i]
    return drivers_genders


def get_drivers_age(drivers_with_kviut: pd.DataFrame, new_drivers: pd.DataFrame):
    def birthdate_to_age(birthdate: str) -> float:
        if birthdate == "01/01/1900" or not birthdate or pd.isna(birthdate):
            return None
        if "/" not in birthdate:
            if "." in birthdate:
                birthdate = birthdate.replace(".", "/")
            elif " " in birthdate:
                birthdate = datetime.strptime(birthdate, "%B %d, %Y")
                birthdate = birthdate.strftime("%#d/%#m/%Y")
            else:
                raise ValueError("missed an option:", birthdate)
        birthdate = datetime.strptime(birthdate, "%d/%m/%Y")
        today = datetime.today()
        age = round((today - birthdate).days / 365.25, 1)
        return age

    drivers_ages = {}

    for i, driver in enumerate(new_drivers["id"]):
        drivers_ages[driver] = birthdate_to_age(new_drivers["birthdate"][i])
    for i, driver in enumerate(drivers_with_kviut["id"]):
        if driver in drivers_ages:
            raise ValueError("Driver duplicate", driver)
        else:
            drivers_ages[driver] = birthdate_to_age(drivers_with_kviut["birthdate"][i])
    return drivers_ages


def get_drivers_vetek(drivers_with_kviut: pd.DataFrame, new_drivers: pd.DataFrame):

    drivers_vetek = {}

    for i, driver in enumerate(new_drivers["id"]):
        drivers_vetek[driver] = round(new_drivers["vetek"][i] / 365.25, 1)
    for i, driver in enumerate(drivers_with_kviut["id"]):
        if driver in drivers_vetek:
            raise ValueError("Driver duplicate", driver)
        else:
            drivers_vetek[driver] = drivers_with_kviut["vetek"][i]

    return drivers_vetek

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os

MEAN_V = 75.74753966299234
BASIC_MILAGE = 200
MEAN_KMS = 66.4966658541842


def get_trip_length(start_time: str, end_time: str) -> float:
    if pd.isna(end_time) or pd.isna(start_time):
        return None
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    hours = (end_time - start_time).total_seconds() / 3600
    return hours


def get_velocity(start_time: str, end_time: str, km: float):
    if pd.isna(end_time) or pd.isna(start_time):
        return None
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    hours = (end_time - start_time).total_seconds() / 3600
    speed_kmh = km / hours
    return speed_kmh


def preprocess_velocities(data_path=Path("Azrieli_TAL/data/trips_data")):
    save_path = (
        data_path.parent / f"{data_path.name}_processed"
        if "processed" not in str(data_path)
        else data_path
    )
    os.makedirs(save_path, exist_ok=True)
    for trip in os.listdir(data_path):
        df = pd.read_csv(data_path / trip)
        for i, (start_time, end_time, km) in enumerate(
            zip(df["start_time"], df["end_time"], df["km"])
        ):
            if pd.isna(start_time) and pd.isna(end_time):
                start_time = datetime_to_time(time_to_datetime())
            velocity = get_velocity(start_time, end_time, km)
            if velocity:
                if velocity < 30 or velocity > 150:
                    print(trip, velocity)
                    df.loc[i, "end_time"] = datetime_to_time(
                        time_to_datetime(start_time) + timedelta(hours=km / MEAN_V)
                    )
        df.to_csv(save_path / trip)
    return save_path


def preprocess_kms(data_path=Path("Azrieli_TAL/data/trips_data")):
    save_path = (
        data_path.parent / f"{data_path.name}_processed"
        if "processed" not in str(data_path)
        else data_path
    )
    os.makedirs(save_path, exist_ok=True)
    for trip in os.listdir(data_path):
        df = pd.read_csv(data_path / trip)
        for i, (start_time, end_time, km) in enumerate(
            zip(df["start_time"], df["end_time"], df["km"])
        ):
            if pd.isna(start_time) and pd.isna(end_time):
                print("h")
            if km:
                if km > 1000:
                    df.loc[i, "km"] = MEAN_KMS
        df.to_csv(save_path / trip)
    return save_path


def get_night_intervals(
    days: list[datetime], night_start_hour=22, night_end_hour=6
) -> list[tuple[datetime, datetime]]:
    if not days:
        return []
    days = sorted(days)
    intervals = []
    for day in days:
        start_night = day.replace(
            hour=night_start_hour, minute=0, second=0, microsecond=0
        )
        end_night = (day + timedelta(days=1)).replace(
            hour=night_end_hour, minute=0, second=0, microsecond=0
        )
        intervals.append((start_night, end_night))
    first_day = days[0]
    prev_start = (first_day - timedelta(days=1)).replace(
        hour=night_start_hour, minute=0, second=0, microsecond=0
    )
    prev_end = first_day.replace(hour=night_end_hour, minute=0, second=0, microsecond=0)
    intervals.insert(0, (prev_start, prev_end))
    return intervals


def get_interval_intersection_hours(interval1, interval2):
    start1, end1 = interval1
    start2, end2 = interval2

    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)

    if overlap_start >= overlap_end:
        return 0.0

    intersection = (overlap_end - overlap_start).total_seconds() / 3600
    return intersection


def percentaged_bonus(
    bonus_percentile: float, taarif: float, km: float, normalized_intersection: float
):
    # new_taarif = taarif *
    return (bonus_percentile / 100) * taarif * km * normalized_intersection


def apply_bonuses(
    taarifs: pd.DataFrame,
    base_taarif: float,
    km: float,
    night_intersection_normalized: float,
    weekend_intersection_normalized: float,
):
    weekend_bonus = taarifs["weekend_bonus"]
    night_bonus = taarifs["night_bonus"]
    return (
        (
            base_taarif * km
            + percentaged_bonus(
                weekend_bonus, base_taarif, km, weekend_intersection_normalized
            )
            + percentaged_bonus(
                night_bonus, base_taarif, km, night_intersection_normalized
            )
        )
        .iloc[0]
        .item()
    )


def get_inetrval_length_hours(interval: tuple[datetime, datetime]):
    return abs(interval[1] - interval[0]).total_seconds() / 3600


def get_intersection_with_night(start_time: datetime, end_time: datetime):

    def get_days_between(start_time: datetime, end_time: datetime) -> list[datetime]:
        days = []
        current = start_time.date()
        while current <= end_time.date():
            days.append(datetime.combine(current, datetime.min.time()))
            current += timedelta(days=1)
        return days

    days_between = get_days_between(start_time, end_time)
    all_nights = get_night_intervals(days_between)
    intersection = 0
    for night in all_nights:
        intersection += get_interval_intersection_hours(night, (start_time, end_time))
    return intersection


def get_intersection_with_weekend(
    start_time: datetime, end_time: datetime, weekend_start=16, weekend_end=20
):
    next_saturday = get_next_saturday(start_time)
    weekend_end = next_saturday.replace(
        hour=weekend_end, minute=0, second=0, microsecond=0
    )
    weekend_start = (weekend_end - timedelta(days=1)).replace(
        hour=weekend_start, minute=0, second=0, microsecond=0
    )
    return get_interval_intersection_hours(
        (start_time, end_time), (weekend_start, weekend_end)
    )


def get_next_saturday(dt: datetime) -> datetime:
    days_ahead = (5 - dt.weekday()) % 7
    return dt + timedelta(days=days_ahead)


def get_basic_and_extra_milage_intervals(
    km: float, start_time: datetime, end_time: datetime, mean_velocity: float
):
    if km <= BASIC_MILAGE:
        return (km, (start_time, end_time)), (0, (end_time, end_time))
    km_basic = BASIC_MILAGE
    km_extra = km - BASIC_MILAGE
    basic_start_time = start_time
    basic_end_time = min(
        basic_start_time + timedelta(seconds=(km_basic / mean_velocity) * 3600),
        end_time,
    )
    extra_start_time = basic_end_time
    extra_end_time = end_time
    return (km_basic, (basic_start_time, basic_end_time)), (
        km_extra,
        (extra_start_time, extra_end_time),
    )


def process_month(raw_month: str) -> datetime:
    month_name, year = raw_month.split(" ")[0], raw_month.split(" ")[1]
    month = datetime.strptime(f"{month_name} {year}", "%B %Y").strftime("%m/%Y")
    return month


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
    def map_raw_gender_to_gender(raw_gender: str) -> str:
        gender_map = {
            "F": ["female", "girl", "f", "woman"],
            "M": ["m", "male", "boy"],
            "None": ["unknown", "none", "null"],
        }
        for key, names in gender_map.items():
            if not raw_gender or pd.isna(raw_gender):
                return "None"
            if raw_gender.lower() in names:
                return key
        raise ValueError(f"{raw_gender} not in gender map.")

    drivers_genders = {}
    for i, driver in enumerate(new_drivers["id"]):
        gender = map_raw_gender_to_gender(new_drivers["gender"][i])
        gender = pd.NA if gender == "None" else gender
        drivers_genders[driver] = gender

    for i, driver in enumerate(drivers_with_kviut["id"]):
        if driver in drivers_genders:
            raise ValueError("Driver duplicate", driver)
        else:
            if driver == 65:
                print("d")
            gender = map_raw_gender_to_gender(drivers_with_kviut["gender"][i])
            gender = pd.NA if gender == "None" else gender
            drivers_genders[driver] = gender
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


def time_to_datetime(time="2015-09-01 06:00:00") -> datetime:
    if not time or pd.isna(time):
        return None
    else:
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")


def datetime_to_time(
    time=datetime.strptime("2015-09-01 15:54:00", "%Y-%m-%d %H:%M:%S")
) -> str:
    if not time:
        return None
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S")


def fill_empty_times(
    km: float, start_time: datetime, end_time: datetime, mean_velocity: float
):
    if start_time == None and end_time == None:
        # NOTE: this should be tackled
        return None, None
    trip_time = (km / mean_velocity) * 3600
    if start_time == None:
        start_time = end_time - timedelta(seconds=trip_time)
    elif end_time == None:
        end_time = start_time + timedelta(seconds=trip_time)
    return start_time, end_time

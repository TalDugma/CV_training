import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from utils import *


import seaborn as sns
import matplotlib.pyplot as plt

DATA_PATH = "Azrieli_TAL/data"
MEAN_V = 75.74753966299234
MEAN_KMS = 66.4966658541842
# NOTE: Median v: 74.99169614486497


def check_unkown_companies(companies: list, trips: list):
    new_customers = []
    for trip in trips:
        df = pd.read_csv(os.path.join(DATA_PATH, "trips_data", trip))
        for customer in df["customer"].tolist():
            if customer not in companies:
                if customer not in new_customers:
                    new_customers.append(customer)
                    print(customer)
    print("finished")


def check_unkown_ids(all_drivers: list, trips: list):
    for trip in trips:
        df = pd.read_csv(os.path.join(DATA_PATH, "trips_data", trip))
        for id in df["driver_id"].tolist():
            if id not in all_drivers:
                print("Missing ID:", id)
    print("finished")


def check_multiplication_of_trips():
    # trips_data_folder = "C:\Users\user\Desktop\CvTrainingTal\CV_training\basic\python\Azrieli_TAL\data\trips_data"
    # files = os.listdir(trips_data_folder)
    # for file_name in files:
    #     file_name_no_extension = file_name.split(".")[0]

    # file1 = pd.read_csv(file_path1)
    # file2 = pd.read_csv(file_path2)
    # print(file1 == file2)
    pass


def check_trip_multiplication(trips_path="Azrieli_TAL/data/trips_data"):
    all_equal = True
    trips = os.listdir(trips_path)
    for trip in trips:
        if trip.split(".")[0].endswith("(2)"):
            orig_trip = trip.replace("(2)", "")
            if orig_trip in trips:
                trip1 = pd.read_csv(os.path.join(trips_path, trip))
                trip2 = pd.read_csv(os.path.join(trips_path, orig_trip))
                if not trip1.equals(trip2):
                    all_equal = False
            else:
                print("oh si")
    return all_equal


def get_unique_months(trips_path="Azrieli_TAL/data/trips_data"):
    trips = os.listdir(trips_path)
    months = [trip.split("_")[0] for trip in trips]
    return np.unique(months)


def get_unique_truck_ids(trips_path="Azrieli_TAL/data/trips_data"):
    trips = os.listdir(trips_path)
    months = [trip.split("_")[1].split(".")[0] for trip in trips]
    return np.unique(months)


def get_trip_length(start_time: str, end_time: str):
    if pd.isna(end_time) or pd.isna(start_time):
        return None
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    hours = (end_time - start_time).total_seconds() / 3600
    return hours


def get_all_velocities(data_path=Path("Azrieli_TAL/data/trips_data_processed")):
    velocities = []
    for trip in os.listdir(data_path):
        df = pd.read_csv(data_path / trip)
        for start_time, end_time, km in zip(df["start_time"], df["end_time"], df["km"]):
            if pd.isna(start_time) and pd.isna(end_time):
                print("h")
            velocity = get_velocity(start_time, end_time, km)
            if velocity:
                velocities.append(velocity)
    return velocities


def get_all_trip_lengths(data_path=Path("Azrieli_TAL/data/trips_data_processed")):
    lengths = []
    for trip in os.listdir(data_path):
        df = pd.read_csv(data_path / trip)
        for driver_id, start_time, end_time, km in zip(
            df["driver_id"], df["start_time"], df["end_time"], df["km"]
        ):
            length = get_trip_length(start_time, end_time)
            if length:
                if length > 48:
                    print(trip, length)
                lengths.append(length)
    return lengths


def get_all_trip_kms(data_path=Path("Azrieli_TAL/data/trips_data")):
    kms = []
    for trip in os.listdir(data_path):
        df = pd.read_csv(data_path / trip)
        for driver_id, km in zip(df["driver_id"], df["km"]):
            if km:
                if km < 100:
                    kms.append(float(km))
    return kms


def violin_plot_velocities():
    velocities = get_all_velocities()
    df = {"Drivers": len(velocities) * ["All Drivers"], "V": velocities}
    plt.figure(figsize=(6, 4))
    sns.violinplot(x="Drivers", y="V", data=df)
    plt.xlabel("")
    plt.ylabel("Velocity (km/h)")
    plt.title("Velocity Violin Plot of All Drivers")
    plt.show()


def violin_plot_kms():
    kms = get_all_trip_kms()
    df = {"Drivers": len(kms) * ["All Drivers"], "V": kms}
    plt.figure(figsize=(6, 4))
    sns.violinplot(x="Drivers", y="V", data=df)
    plt.xlabel("")
    plt.ylabel("Trip Length (km)")
    plt.title("Trip Length Plot of All Drivers")
    plt.show()


# violin_plot_kms()
save_path = preprocess_kms()
preprocess_velocities(save_path)
# all_trips_kms = get_all_trip_kms()
# print(np.mean(all_trips_kms))
# get_all_trip_lengths()
# violin_plot_velocities()
# velocities = get_all_velocities()
# print("Mean v:", np.mean(np.array(velocities)))
# print("Median v:", np.median(np.array(velocities)))

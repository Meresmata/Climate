import os
import typing as tp

import pandas as pd

import prepare as pre


def create_data_frame(start_year: int, creation_fn: tp.Callable, white_list: tp.List[str]) -> pd.DataFrame:
    start_folder = "climate_files"
    data_dict = {}  # dict to hold a the files data

    main_dirs = [main_dir for main_dir in pre.sort_folders(start_folder) if main_dir in white_list]
    for main_dir in main_dirs:
        name = main_dir.title().replace("_", "")

        seasons = pre.sort_folders(os.path.join(start_folder, main_dir))
        for season in seasons:

            season_int = int(season[:2])

            file_names = pre.sort_files(os.path.join(start_folder, main_dir, season))
            file_names = [file for file in file_names if int(file[-10:-6]) >= start_year]

            for file_name in file_names:
                year = int(file_name[-10:-6])

                date = creation_fn(
                    os.path.join(start_folder, main_dir, season, file_name)
                )

                if name in data_dict:
                    if year in data_dict[name]:
                        data_dict[name][year][season_int] = date
                    else:
                        data_dict[name][year] = {season_int: date}
                else:
                    data_dict[name] = {year: {season_int: date}}

    # create dict of list from dict of dicts
    # new dict to create data frame
    new_dict = {"year": [], "season": []}
    for name in sorted(data_dict.keys()):
        new_dict[name] = []
        for year in sorted(data_dict[name].keys()):
            for season_int in range(13, 17):  # 13, 14, 15, 16
                if season_int not in data_dict[name][year].keys():
                    new_dict[name].append(None)
                else:
                    new_dict[name].append(data_dict[name][year][season_int])

                # add year and season only once
                if name == "sunshine_duration".title().replace("_", ""):
                    new_dict["year"].append(year)
                    new_dict["season"].append(season_int)

    df = pd.DataFrame(data_dict)
    return df


def reduce(path: str):
    return pre.reduce_data(pre.parse_file_toInt(path), 5)


if __name__ == "__main__":
    allowed = ["air_temperature_max", "air_temperature_mean", "air_temperature_min", "precipitation",
               "sunshine_duration"]
    data = create_data_frame(1951, reduce, allowed)
    # data.to_hdf(os.path.join("climate_files", "short_1951+_1of20.h5"), key="df", mode="w")
    data.to_pickle(os.path.join("climate_files", "short_1951+_1of5.pkl"))
    data.to_csv(os.path.join("climate_files", "short_1951+_1of5.csv"))

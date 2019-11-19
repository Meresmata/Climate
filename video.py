import os

import numpy as np

import prepare as ana

if __name__ == "__main__":

    minimum = {"air_temperature_max": -112,
               "air_temperature_mean": -146,
               "air_temperature_min": -255,
               "drought_index": 0,
               "precipitation": 0,
               "sunshine_duration": 26}

    maximum = {"air_temperature_max": 306,
               "air_temperature_mean": 244,
               "air_temperature_min": 187,
               "drought_index": 9329,
               "precipitation": 1691,
               "sunshine_duration": 951}

    start_folder = "climate_files"
    # for Argument in Data
    for main_dir in ana.sort_folders(start_folder):
        name = main_dir.title().replace("_", " ")
        print(name)

        sub_dirs = ana.sort_folders(os.path.join(start_folder, main_dir))
        frames = []
        frame_dict = {}

        for sub_dir in sub_dirs:
            season = "Spring" if sub_dir.startswith("13") else "Summer" if sub_dir.startswith(
                "14") else "Autumn" if sub_dir.startswith("15") else "Winter"
            season_int = 12 if sub_dir.startswith("16") else int(sub_dir[:2])
            print(season)

            file_names = ana.sort_files(os.path.join(start_folder, main_dir, sub_dir))
            file_names = [file for file in file_names if int(file[-10:-6]) > 1950]

            for file_name in file_names:
                year = file_name[-10:-6]

                if year in frame_dict:
                    frame_dict[year][season_int] = ana.limit_toByte(
                        ana.parse_file_toInt(
                            os.path.join(start_folder, main_dir, sub_dir, file_name)
                        ),
                        minimum[main_dir],
                        maximum[main_dir]
                    )
                else:
                    frame_dict[year] = {season_int: ana.limit_toByte(
                        ana.parse_file_toInt(
                            os.path.join(start_folder, main_dir, sub_dir, file_name)
                        ),
                        minimum[main_dir],
                        maximum[main_dir]
                    )}

        for year in sorted(frame_dict.keys()):
            for season in sorted(frame_dict[year].keys()):
                frames.append(frame_dict[year][season])

        movie_frames = np.array(frames, dtype="uint8")
        # create one video for every type of data(main_dir)
        ana.create_movie(movie_frames, os.path.join(start_folder, name + ".mp4"), 25)

import os
from math import ceil, floor
import numpy as np
import skvideo.io
import typing as tp
from PIL import Image, ImageDraw, ImageFont


def sort_files(path: str) -> tp.List[str]:
    return sorted([x for x in os.listdir(path) if
                   os.path.isfile(os.path.join(path, x))])


def sort_folders(path: str) -> tp.List[str]:
    return sorted([x for x in os.listdir(path) if
                   os.path.isdir(os.path.join(path, x))])


def parse_file_toInt(path: str) -> np.array:
    with open(path) as file:
        strings = file.readlines()[6:]
        data = np.array([[int(y) if int(y) != -999 else None for y in x.split()] for x in strings], dtype="int32")
        return data


def reduce_data(in_data: np.array, factor: int) -> np.array:
    height, width = in_data.shape
    non_data = -999
    out_data = np.zeros(shape=(ceil(height / factor), ceil(width / factor)), dtype="int32")

    y_index = -1

    for y in range(0, height, factor):

        x_index = -1
        y_index = y_index + 1

        for x in range(0, width, factor):

            x_index = x_index + 1

            x_factor = factor % width if x + factor > width else factor
            y_factor = factor % height if y + factor > height else factor
            temp = in_data[y: y + y_factor, x: x + x_factor]

            num_data = np.count_nonzero(temp != non_data)
            # if more than half of the data are non-data set output to non-data, else to the average of the real data values
            if num_data >= floor(factor * factor / 2):
                out_data[y_index, x_index] = round(np.sum(temp[temp != non_data])/num_data)

            else:
                out_data[y_index, x_index] = non_data

    return out_data


def limit_toByte(data: np.ndarray, min_val: int, max_val: int) -> np.ndarray:
    def map_data(val: int, minimum_val: int, maximum_val: int) -> int:
        return int(254 * (maximum_val - val) / (maximum_val - minimum_val))

    value = np.array([[map_data(value, min_val, max_val) if value != -999 else 255 for value in row] for row in data],
                     dtype="uint8")

    return value


def create_image(data: np.array, txt: str, path: str, mini: int, maxi: int, color: str = "gray"):
    assert (color in ["gray", "hot", "blue"])

    image = Image.fromarray(
        limit_toByte(data, mini, maxi),
        mode="P")

    if color == "blue":
        rgbs = list(
            np.array([[0, 0, 2 * x] if x < 128 else [2 * (x - 128), 2 * (x - 128), 255] for x in range(256)]).flatten())
        image.putpalette(rgbs)
    elif color == "hot":
        rgbs = list(np.array([[255, 255 - x, 0] for x in range(256)]).flatten())
        image.putpalette(rgbs)

    font = ImageFont.truetype(font="arial.ttf", size=50)
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), txt, font=font, fill=254)
    image.save(path + ".png", format='png', transparency=255)


def create_movie(output_data: np.array, out_path: str, fps: int = 4):
    writer = skvideo.io.FFmpegWriter(out_path, outputdict={"-r": str(fps)})
    for i in range(output_data.shape[0]):
        writer.writeFrame(output_data[i, :, :])
    writer.close()


if __name__ == "__main__":

    start_folder = "climate_files"
    # for Argument in Data

    for main_dir in sort_folders(start_folder):
        name = main_dir.title().replace("_", " ")
        print(name)

        # get Min, Max for Argument
        max_list = []
        min_list = []
        print("Test Seasons:")

        seasons = sort_folders(os.path.join(start_folder, main_dir))
        for season in seasons:
            print(season)

            years = sort_files(os.path.join(start_folder, main_dir, season))
            for years_date in years:
                temps = parse_file_toInt(os.path.join(start_folder, main_dir, season, years_date)).flatten()
                max_list.append(np.max(temps))
                min_list.append(np.min(np.array([x for x in temps if x != -999])))
        maximum = max(max_list)
        minimum = min(min_list)

        print("Minimum value: " + str(minimum))
        print("Maximum value: " + str(maximum))

        print("Start processing images")
        # for Season in Argument Data

        sub_dirs = sort_folders(os.path.join(start_folder, main_dir))
        for sub_dir in sub_dirs:
            season = "Spring" if sub_dir.startswith("13") else "Summer" if sub_dir.startswith(
                "14") else "Autumn" if sub_dir.startswith("15") else "Winter"
            print(season)

            file_names = sort_files(os.path.join(start_folder, main_dir, sub_dir))
            for file_name in file_names:
                year = file_name[-10:-6]

                create_image(
                    parse_file_toInt(
                        os.path.join(start_folder, main_dir, sub_dir, file_name)
                    ),
                    txt=name + "\n" + year + ", " + season,
                    # save in it's parent folder:
                    path=os.path.join(start_folder, main_dir, file_name),
                    mini=minimum, maxi=maximum,
                    color="blue" if name == "precipitation".title() else "gray" if name == "sunshine_duration" else "hot"
                )

import requests
import os
import gzip as gz
import shutil


def tree_download(path: str):
    r = requests.get(path, allow_redirects=True)
    html_str = r.text

    begin_tag = "href"
    end_tag = "</a>"
    start = html_str.find(begin_tag)

    while start != -1:
        end = html_str.find(end_tag)

        part_str = html_str[start+len(begin_tag)+2: end-len(end_tag)-1]
        part_end = part_str.find('/"')
        part_str = part_str[:part_end]

        if part_str != "..":

            if part_str.find(".gz") == -1:
                # open deeper links of website
                if not os.path.exists(part_str):
                    os.mkdir(part_str)
                os.chdir(part_str)
                new_path = path + part_str + "/"
                tree_download(new_path)

            else:
                # download the file
                part_end = part_str.find(".gz")
                part_str_gz = part_str[:part_end+len(".gz")]
                part_str = part_str[:part_end]
                file_url = path + part_str_gz
                file = requests.get(file_url)
                if not os.path.exists(part_str):
                    if file.status_code == 200:
                        open(part_str_gz, 'wb').write(file.content)
                        with gz.open(part_str_gz, 'rb') as f_in:
                            with open(part_str, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(part_str_gz)
                        print("Downloaded: " + part_str)
                else:
                    print("Already downloaded: " + part_str)

        html_str = html_str[end+len(end_tag):]
        start = html_str.find(begin_tag)

    os.chdir("..")


if __name__ == "__main__":
    start_url = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/seasonal/"
    if not os.path.exists("climate_files"):
        os.mkdir("climate_files")
    os.chdir("climate_files")

    tree_download(start_url)

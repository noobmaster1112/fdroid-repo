import requests
from requests.structures import CaseInsensitiveDict
import sys
import os
import yaml


# parse apps.yaml
def parse_apps():
    with open('apps.yaml', 'r') as file:
        parsed_file = yaml.safe_load(file)

    for i in parsed_file:
        app_link = parsed_file[i]['git']
        app_name = parsed_file[i]['name']
        app_desc = parsed_file[i]['description']
        app_category = parsed_file[i]['categories']

        download_releases(app_link, app_category, app_desc, app_name)

    fdroid_server()

def fdroid_server():
    os.system("cd fdroid && fdroid update -c")

    os.system("rm fdroid/keystore.p12")
    os.system("rm fdroid/config.yml")


def download_releases(app_link, app_category, app_desc, app_name):
    # create fdroid/repo dir
    create_dir()
    app_link = "/".join(app_link.split("/")[-2:])
    app_link = "https://api.github.com/repos/" + app_link + "/releases?page=1&per_page=2"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/vnd.github+json"

    resp = requests.get(app_link, headers=headers)
    if resp.json():
        for i in resp.json():
            for j in i["assets"]:
                download_link = j["browser_download_url"]
                file_name = download_link.split("/")[-1]
                file_name = "fdroid/repo/" + file_name
                r = requests.get(download_link, stream=True)
                if os.path.exists(file_name):
                    print(f"{file_name} already exists.....Skipping")
                    continue
                with open(file_name, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)


def create_dir():
    try:
        os.system('mkdir -p fdroid/repo')
        print(f"Directory fdroid/repo created successfully")
    except OSError as error:
        print(f"Directory fdroid/repo can not be created\nError: {error}")


if __name__ == "__main__":
    parse_apps()


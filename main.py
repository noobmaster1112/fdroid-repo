import requests
from requests.structures import CaseInsensitiveDict
import subprocess
import os
import yaml
from multiprocess import Pool


# parse apps.yaml
def parse_apps():
    with open('apps.yaml', 'r') as file:
        parsed_file = yaml.safe_load(file)
    r_name = []
    for i in parsed_file:
        app_link = parsed_file[i]['git']
        app_name = parsed_file[i]['name']
        app_desc = parsed_file[i]['description']
        app_category = parsed_file[i]['categories']

        r_name.append(download_releases(app_link, app_category, app_desc, app_name))

    rm_cmd = f"find . ! -name {' ! -name '.join(r_name)} -delete"
    subprocess.run(rm_cmd, cwd="fdroid/repo", shell=True)

    fdroid_server()

def fdroid_server():
    subprocess.run(['fdroid', 'update', '-c'], cwd="fdroid")
    subprocess.run(['rm', 'keystore.p12'], cwd="fdroid")
    subprocess.run(['rm', 'config.yml'], cwd="fdroid")


def download_releases(app_link, app_category, app_desc, app_name):
    # create fdroid/repo dir
    create_dir()
    app_link = "/".join(app_link.split("/")[-2:])
    app_link = "https://api.github.com/repos/" + app_link + "/releases?page=1&per_page=1"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/vnd.github+json"

    resp = requests.get(app_link, headers=headers)
    r_name = []
    if resp.json():
        with Pool() as pool:
            r_name.append(pool.map(download, resp.json()))
    return ' ! -name '.join(' ! -name '.join(i) for i in r_name)


def create_dir():
    try:
        os.system('mkdir -p fdroid/repo')
    except OSError as error:
        print(f"Directory fdroid/repo can not be created\nError: {error}")


def download(i, r_name=[]):
    print(i)
    x = len(i["assets"])
    if x > 2:
        x = 2
    for j in range(x):
        download_link = i["assets"][j]["browser_download_url"]
        file_name = download_link.split("/")[-1]
        r_name.append(file_name)
        file_name = "fdroid/repo/" + file_name
        r = requests.get(download_link, stream=True)
        if os.path.exists(file_name):
            print(f"{file_name} already exists.....Skipping")
            continue
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return ' ! -name '.join(r_name)

if __name__ == "__main__":
    parse_apps()


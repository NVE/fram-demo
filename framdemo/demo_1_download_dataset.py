import zipfile
from pathlib import Path

import requests
from framcore.events import send_error_event, send_info_event, send_warning_event

import framdemo.demo_utils as du


def demo_1_download_dataset() -> None:
    """
    Download the FRAM demo dataset from zenodo to the demo folder and unzip zip files.

    1. Dataset zip file is downloaded from https://doi.org/10.5281/zenodo.17294466 using REST api.
    2. File is unzipped in the dataset folder. The file is unzipped in such a way that it skips the first directory level, so all the db_xx directories should
       be placed in the same folder as the zip file was downloaded to.
    3. Zip file is deleted.

    """
    if du.DATASET_SOURCE is not None:
        assert isinstance(du.DATASET_SOURCE, Path) and du.DATASET_SOURCE.is_dir()
        import os
        import shutil
        from time import time

        t = time()
        send_info_event(demo_1_download_dataset, "downloading dataset")
        os.makedirs(du.DEMO_FOLDER / "database", exist_ok=False)
        for name in os.listdir(du.DATASET_SOURCE):
            path = du.DATASET_SOURCE / name
            send_info_event(demo_1_download_dataset, f"{path}")
            if path.is_dir():
                shutil.copytree(src=path, dst=du.DEMO_FOLDER / "database" / name)
            else:
                shutil.copyfile(src=path, dst=du.DEMO_FOLDER / "database" / name)
        send_info_event(demo_1_download_dataset, f"time download dataset {round(time() - t, 3)} seconds")
        return

    local_dataset_folder: Path = du.DEMO_FOLDER / "database"

    if local_dataset_folder.is_dir() and list(local_dataset_folder.iterdir()):
        send_warning_event(demo_1_download_dataset, f"Skipping download because there is already data in {local_dataset_folder}")
        return

    zenodo_url = "https://zenodo.org/"
    dataset_id = "17570105"
    api_url = zenodo_url + "api/records/" + dataset_id + "/files"  # Insert ID of dataset
    url = zenodo_url + "records/" + dataset_id

    local_dataset_folder.mkdir(exist_ok=True, parents=True)
    send_info_event(demo_1_download_dataset, f"Downloading dataset from {url} (this might take a few minutes)")
    try:
        response = requests.get(api_url)

        if response.status_code != 200:
            message = f"Failed to download dataset from Zenodo. Status code: {response.status_code}, Response text: {response.text}" 
            send_error_event(sender=demo_1_download_dataset, message=message)
            raise RuntimeError(message)
        
        files_data = response.json()

        for file_info in files_data["entries"]:
            file_url = file_info["links"]["self"]
            if not file_url.endswith(".zip"):
                continue
            file_url = zenodo_url + file_url.split(zenodo_url + "api/")[1]
            file_path: Path = local_dataset_folder / file_info["key"]
            if file_path.exists() and zipfile.is_zipfile(str(file_path)):  # for if the file already exists as a valid zip file.
                send_info_event(demo_1_download_dataset, f"Existing file {file_path} exists and is a valid zipfile. Skipping download.")
                continue

            # Download the file
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()
                with file_path.open(mode="wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    except requests.exceptions.RequestException as e:
        message = f"An exception occured during download of dataset from Zenodo: {e}"
        send_error_event(sender=demo_1_download_dataset, message=message, exception_type_name=str(type(e)), traceback=e.__traceback__)
    send_info_event(demo_1_download_dataset, "Dataset download finished.")

    _unzip_files_in_folder(local_dataset_folder)


def _unzip_files_in_folder(dataset_folder: Path) -> None:
    files_to_unzip = [fp for fp in dataset_folder.iterdir() if zipfile.is_zipfile(str(fp))]
    if files_to_unzip:
        send_info_event(_unzip_files_in_folder, f"Found zip files: {files_to_unzip}. Begin unzipping.")
        # Unzipping
        for file_path in files_to_unzip:
            with zipfile.ZipFile(file_path, "r") as zf:
                for member in zf.namelist():
                    member_path = Path(member)

                    # Split the path and remove the first component (top-level folder)
                    parts = member_path.parts

                    if len(parts) > 1:
                        folder_path = dataset_folder
                        for part in parts[:-1]:
                            folder_path = folder_path / part
                        folder_path.mkdir(exist_ok=True, parents=True)
                        new_path = folder_path / parts[-1]

                    else:
                        new_path = dataset_folder / member_path

                    if new_path.exists():
                        continue

                    # Create parent directories if they don't exist
                    if member.endswith("/"):
                        new_path.mkdir(exist_ok=True, parents=True)
                    elif not member.endswith("/"):
                        with new_path.open(mode="wb") as outfile:
                            outfile.write(zf.read(member))
        send_info_event(_unzip_files_in_folder, f"Successfully unzipped to '{dataset_folder}'.")
        _delete_zip_files(files_to_unzip)
    else:
        send_info_event(_unzip_files_in_folder, f"Found no valid files to unzip in '{dataset_folder}'")


def _delete_zip_files(zip_files: list[Path]) -> None:
    for fp in zip_files:
        try:
            fp.unlink()
        except OSError:
            send_info_event(_delete_zip_files, f"Failed to delete zip file {fp}. Continuing without deleting.")


if __name__ == "__main__":
    demo_1_download_dataset()

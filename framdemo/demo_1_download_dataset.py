from framcore.events import send_debug_event

import framdemo.demo_utils as du


def demo_1_download_dataset():
    if not (du.DEMO_FOLDER / "database").is_dir():
        import os
        import shutil
        from time import time

        t = time()
        send_debug_event(demo_1_download_dataset, "downloading dataset")
        os.makedirs(du.DEMO_FOLDER / "database", exist_ok=False)
        for name in os.listdir(du.DATASET_SOURCE):
            path = du.DATASET_SOURCE / name
            send_debug_event(demo_1_download_dataset, f"{path}")
            if path.is_dir():
                shutil.copytree(src=path, dst=du.DEMO_FOLDER / "database" / name)
            else:
                shutil.copyfile(src=path, dst=du.DEMO_FOLDER / "database" / name)
        send_debug_event(demo_1_download_dataset, f"time download dataset {round(time() - t, 3)} seconds")


if __name__ == "__main__":
    demo_1_download_dataset()

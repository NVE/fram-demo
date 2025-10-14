# FRAM demo

## About
See [FRAM demo](https://nve.github.io/fram-demo/) for description of the demo case.

See [FRAM mainpage](https://nve.github.io/fram/) for general description of the FRAM system.

Contact [fram@nve.no](mailto:fram@nve.no) if you have any questions or feedback.

## To install and run the demos

You need Python version >=3.11 and <3.14 on your machine in order to install and run the demos. If you don't already have Python installed, you can get it here: https://www.python.org/.
You can check the version of python installed by running `python --version` in terminal window.

To install and run, follow these steps:
1. Get *fram-demo* to your machine:
    - If you use git, clone *fram-demo* to your machine by running `git clone https://github.com/NVE/fram-demo.git` in your terminal and navigate to the project root folder `cd ./fram-demo`.

    - Or simply download an archived version from `https://github.com/NVE/fram-demo/archive/refs/heads/main.zip`, unzip and open terminal in `fram-demo` folder.

2. Run `python ./framdemo/install_poetry.py` - this should install poetry.exe and create a virtual environment named venv in the root folder of the project. 

    - If `python` is not recongized as a command, or points to an incorrect python version, try to replace `python` with `.\"path\to\correct\python.exe"` and it should work
    
3. Run `./venv/Scripts/activate` - this should activate the virtual environment.
    
4. Run `./poetry.exe install` - this should install packages to the virtual environment.
    
5. Run `python ./framdemo/run_all.py` - this should run all demos and open a dashboard with result visualisation. Demo will take approximately 1 hour +/- if you run it on a CPU with 8 cores, because the demo will try to start 8 processes to run the model. Demo will use around 4,3 GB storage space on your computer. 


We hope you enjoy the demo and give us your feedback!

## Troubleshooting

Here are some known issues that can occur during the installation:


|   Error message   | Possible reason   | Possible solutions   |
|-------------------|-------------------|------------|
| Program 'poetry.exe' failed to run. | Windows Security blocks running exe files on your disc | 1. Check your security policy. Change Windows Security settings if you have administrator access. <br> 2. Create folder on a disc that has no security restrictions. |
| Downloading data from Zenodo (demo_1) goes slowly. | No spesific reason, downloading time may vary depending on Zenodo's server capacity. | Downloading data may take several minutes, just wait. |
| Error during data download:<br> `error: framdemo.demo_1_download_dataset: An exception occured during download of dataset from Zenodo:`<br>`HTTPSConnectionPool: Max retries exceeded with url: /api/records/... Caused by SSLError ... certificate verify failed: Hostname mismatch, certificate is not valid for 'zenodo.org'. ` | Unknown cause, may be something related to security.  We post more information when we know more.  | This error comes and goes on some PCs, try to run the demo again. | 
 Dashboard or demo run slowly.    | Speed can depend on many factors depending on your PC setup and number of CPU cores. | Things you can check: <br> - demo folder is located on the local drive, and not on the drive connected via a network. We generally recommend to have the demo folder locally in order to avoid being dependent on the network speed. <br> - Run demo on a PC that has 8 CPU cores. This is the most optimal setup for the demo as it starts 8 processes. |
| Error when running `.\venv\Scripts\activate`:<br>`File Path\to\demo\fram-demo\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.` <br> `CategoryInfo : SecurityError, PSSecurityException`<br>`FullyQualifiedErrorId : UnauthorizedAccess` | Unknown cause, occurs sporadically on older systems. We post more information when we know more. | Run `Set-ExecutionPolicy RemoteSigned -Scope Process` first. |
| SSL error during data download | Unknown | ... |
| Powershell problems?      | ? | ? |


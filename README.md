# FRAM demo

## About
See [FRAM demo](https://nve.github.io/fram-demo/) for description and documentation.

## To install and run the demos

You need Python version 3.11 or higher to install and run the demos. If you don't already have Python installed, you can get it here: https://www.python.org/

To install and run, follow these steps:
1. Get *fram-demo* to your machine:
- If you use git, clone *fram-demo* to your machine by running `git clone https://github.com/NVE/fram-demo.git` in your terminal and navigate to the project root folder `cd ./fram-demo`.

- Or simply download an archived version from `https://github.com/NVE/fram-demo/archive/refs/heads/main.zip`, unzip and open terminal in `fram-demo` folder.

2. Run `python ./framdemo/install_poetry.py` (this should install poetry.exe and create a virtual environment named venv in the root folder of the project). 

    (If `python` is not recongized as a command, or points to an incorrect python version, try to replace `python` with `.\"path\to\correct\python.exe"` and it should work)


    
3. Run `./venv/Scripts/activate` (this should activate a virtual environment).
    
4. Run `./poetry.exe install` (this should install packages to the virtual environment).
    
5. Run `python ./framdemo/run_all.py` (this should run all demos and open a dashboard with result visualisation).

Enjoy!

## How to run the demo

To run the demo you first need to set up paths in script **demo_utils.py**

Path to the database. The database has already been installed for you when you installed pip install fram-demo. Check where the database was installed and set the path here.

> DATASET_SOURCE = Path(r"path/to/your/database").resolve()

Path to demo folder. Can be any folder on your computer.

> DEMO_FOLDER = Path("path/to/your/demo/folder") 

Path to [Julia]({{ juleslinks.julia }}){:target="_blank"} and will download [Julia]({{ juleslinks.julia }}){:target="_blank"} when none. [Julia]({{ juleslinks.julia }}){:target="_blank"} is an open-source programming language and is used in this demo to run JuLES power market model in this demo and will be installed in this path. If [Julia]({{ juleslinks.julia }}){:target="_blank"} is already downloaded, replace with Path to download.

> JULIA_PATH_EXE = None

## Demo case steps
The demo consists of 8 steps. This includes a demo_0 file that runs all the following steps in the correct order:

1. **demo_1_download_dataset.py** - creates a new model object and populates it with data from the database. Saves the populated object as a pickle file.

2. **demo_2_populate_model.py** - aggregates data per country using node aggregator. Saves the aggregated object as a pickle file.

3. **demo_3_solve_model.py** - configures and solves JulES power market model for the base case. The same configuration is used for both base run and sensitivinty run in this demo. *OBS! Not all JulES configurations are supported yet, contact FRAM team if you want to test your own configuration and get an error.*

4. **demo_4_modified_solve.py** - runs a sensitivity case where CO2 price is scaled up by 20%. JulES configuration is the same.
 
5. **demo_5_detailed_solve.py** - solves model using detailed hydropower data

6. **demo_6_nordic_solve.py** - solved nordic models

6. **demo_7_get_data.py** - will write price, regional volumes and hydropower results to h5 format in order to send them to the dashboard.

6. **demo_8_run_dashboard.py** - will run the dashboard in a browser and visualize results from h5 files.

*Denne siden er uferdig, så ikke klikk* See [description of the demo case](./what_demo_includes.md) to learn what countries and years are included into the model runs. 


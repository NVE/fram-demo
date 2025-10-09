# How to run the demo

To run the demo you first need to set up paths in script **demo_utils.py**

Path to the database. The database has already been installed for you when you installed pip install fram-demo. Check where the database was installed and set the path here.

> PATH_DB = Path(r"path/to/your/database") 

Path to demo folder. Can be any folder on your computer.

> DEMO_FOLDER = Path("path/to/your/demo/folder") 

Path to Julia environment and Julia depot. Can be any folder. [Julia]({{ juleslinks.julia }}){:target="_blank"} is an open-source programming language and is used in this demo to run JuLES power market model in this demo and will be installed in this path. 

> JULIA_PATH_ENV = Path(r"path/to/julia/environment")

> JULIA_PATH_DEPOT = Path(r"path/to/julia/depot") 

## Demo case steps
The demo consists of 6 steps. Between the steps there is an intermediate storage of data so that you can run the steps in different order if you want. 

Run the following steps:

1. **populate_model.py** - creates a new model object and populates it with data from the database. Saves the populated object as a pickle file.

2. **aggregate_model.py** - aggregates data per country using node aggregator. Saves the aggregated object as a pickle file.

3. **solve_model.py** - configures and solves JulES power market model for the base case. The same configuration is used for both base run and sensitivinty run in this demo. *OBS! Not all JulES configurations are supported yet, contact FRAM team if you want to test your own configuration and get an error.*

4. **sensitivity_run.py** - runs a sensitivity case where CO2 price is scaled up by 20%. JulES configuration is the same.
 
5. **get_regional_volumes.py** - gets results for production and demand from the model.

6. **plot_solution.py** - visualizes results in a simple plot.

6. **write_results_to_h5.py** - *work in progress! will write results to h5 format in order to send them to the dashboard.*

6. **run_dashboard.py** - *work in progress! will run the dashboard in a browser and visualize results from h5 files.*

*Denne siden er uferdig, så ikke klikk* See [description of the demo case](./what_demo_includes.md) to learn what countries and years are included into the model runs. 


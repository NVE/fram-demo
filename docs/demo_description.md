# Demo description
The demo case includes **4 model runs**:

* **BASE:** Northern Europe aggregated with aggregated hydropower and elspot price areas 
* **MODIFIED:** the same as BASE but with demand in Norway increased by 20%
* **DETAILED:** the same as BASE but with detailed hydropower in the Nordic region (Norway, Sweden, Finland, Denmark)
* **MODIFIED_NORDIC:** models the Nordic countries endogenously with aggregated hydropower and uses prices from BASE to model all other countries exogenously. Includes a 20% increase in demand in Norway.

These cases correspond to demos 4-6 in the code, see overview of the demo steps below. 

You can run each demo step separately, or just run `run_all.py` to run all steps automatically. 

### Simulation period
Demo case is a series simulation, meaning that the power system is simulated at a given state, and weather years are simulated chronologically. In this demo we simulate the power system in 2023 with 3 weather years simulated after each other (1995, 1996, 1997).

### Geographical areas
The following countries are included into the demo case: 

{{ read_csv('docs/tables/countries.csv') }}

## JulES model
Power system will be simulated using [open-source JulES model]({{ framlinks.jules }}). The model will be installed automatically. 

JulES uses [programming language Julia]({{ framlinks.julia }}) and it will also be installed on your PC for this demo if you do not have it yet. 


## Demo steps
The main demo consists of 8 steps:

1. **demo_1_download_dataset.py** - downloads [demo dataset]({{ framlinks.dataset }}) into the database folder and unzipps files. 

2. **demo_2_populate_model.py** - creates a new model object and populates it with data from the database. Saves the populated object as a pickle file.

3. **demo_3_solve_model.py** - **BASE case** reads populated model, aggregates power nodes and hydro power plants to elspot areas. Saves the aggregated object as a pickle file. Configures JulES power market model, sets time resolution and units. Solves the model with aggregated data.

4. **demo_4_modified_solve.py** -  **MODIFIED case** increases demand in norwegian price areas by 20% in the model object. Runs the model again with the same configuration and the modified model object.
 
5. **demo_5_detailed_solve.py** - **DETAILED case** solves model with detailed hydropower data.

6. **demo_6_nordic_solve.py** - **MODIFIED_NORDIC case** solves the Nordic model.

7. **demo_7_get_data.py** - writes price, regional volumes and hydropower results to h5 format in order to send them to the dashboard.

8. **demo_8_run_dashboard.py** - runs the dashboard in a browser and visualizes results from h5 files.


New demos added in fram v.0.1.0:

9. **demo_9_edit_h5_profiles** - demo of how to edit H5 files, [see description here]({{ framlinks.data_edit_profiles }}).

10. **demo_10_watershed** - demo of how to optimize a single watershed against a price using JulES model. See description below.


## Demo folders
Demo folders will be set up automatically:

* Demo will run in folder **demo_folder** in your parent directory. 
* Demo dataset will appear in subfolder **database**.
* Julia environment for running JulES will be set up in subfolder **julia_depot**.

Model runs will be performed in subfolders with names corresponding to the modelling cases:

* base
* detailed
* modified
* modified_nordic

Results from all model solves will also be converted into h5-files that will be shown in the dashboard.

See demo_utils.py if you want to set up your own paths.

## Demo 10 - optimising a single watershed

Optimizes a single watershed against a price.

In this demo, we isolate a single watershed from the full energy model and set all power nodes to exogenous:
1. Read detailed model (or populated model) and configured JulES solver used in demo 3.
2. Isolate system to only include one watershed, her we choose "BORGUND_H".
3. Aggregate power nodes in model to elspot areas.
4. Set all power nodes to exogenous.
5. Solve the model with JulES and reuse dashboard from previous demos (NB! Will overwrite dashboard data from previous demos).

JulES has a "subsystem mode" which is triggered when there is only exogenous market nodes in the model.
It will then optimize the system using only the stochastic subsystem problems (ignoring price prognosis problems
and market clearing problems). The stochastic subsystem problems are two-stage stochastic programming problem
solved with Benders decomposition.





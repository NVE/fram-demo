def demo_5_detailed_solve():
    """
    Same model as demo 3 except with detailed hydro power instead of aggregated hydropower.

    Solve model.
    1. Read populated model from populate model demo from disk.
    2. Aggregate power nodes in model to elspot areas.
    3. Read configured JulES solver from demo 3.
    4. Make a few configurations (where to save files and to reuse installation)
    5. Create hydro power aggregators and put them into JulES via config
    6. Solve the model with JulES.
    """
    from datetime import timedelta

    import numpy as np
    from framcore import Model
    from framcore.aggregators import HydroAggregator, NodeAggregator
    from framcore.timeindexes import ModelYear, OneYearProfileTimeIndex, WeeklyIndex
    from framcore.timevectors import ListTimeVector
    from framjules import JulES

    import framdemo.demo_utils as du

    # Read populated model from populate model demo from disk.
    model: Model = du.load(du.DEMO_FOLDER / "populated_model.pickle")

    # read configured jules solver used in demo 3 from disk
    jules: JulES = du.load(du.DEMO_FOLDER / "base" / "solver.pickle")
    
    # Make a few configurations (where to save files and to reuse installation)
    config = jules.get_config()
    config.set_solve_folder(du.DEMO_FOLDER / "detailed")
    config.activate_skip_install_dependencies()
    config.set_num_cpu_cores(4)

    # get info from config needed for the next steps
    model_year: ModelYear = config.get_data_period()
    first_weather_year, num_weather_years = config.get_weather_years()
    weekly_index = WeeklyIndex(first_weather_year, num_weather_years)

    # Aggregate power nodes in model to elspot areas.
    node_aggregator = NodeAggregator("Power", "elspot", model_year, weekly_index)
    node_aggregator.aggregate(model)

    # The below is different from demo 3. 
    # In demo 3, we aggregate the input model here.
    # Here, we give JulES the hydro aggregators. This way, JulES will use detailed hydropower 
    # in the simulation, and only use aggregated hydropower when estimating future prices 
    # (we need aggregated hydropower in this step of JulES. Whithout it, the simulation would take forever to finish.
    # You can see for yourself by uncommenting 
    # config.set_short_term_aggregations([hydro_aggregator_norway, hydro_aggregator_sweden_finland])
    # below. This line, which will trigger detailed hydropower in all of JulES) 

    # Make a release_capacity_profile to further restrict the release capacity of the aggregated hydropower plants.
    values = np.array([0.93, 0.88, 0.89, 0.90])
    timeindex = OneYearProfileTimeIndex(period_duration=timedelta(weeks=13), is_52_week_years=True)
    release_capacity_profile = ListTimeVector(timeindex, values, unit=None, is_max_level=None, is_zero_one_profile=True)

    # Aggregate hydro power plants in model to elspot areas.
    #   HydroAggregator will create one run-of-river hydropower module and one reservoir hydropower module per elspot area.
    #   We use different aggregations for Norway and for Sweden and Finland.
    #   We use a ror_threshold of 0.6 for Norway and 0.38 for Sweden and Finland, which indicates what regulation factor
    #       a hydropower plant must have to be grouped as a reservoir hydropower plant.
    hydro_aggregator_norway = HydroAggregator(
        "EnergyEqDownstream",
        model_year,
        weekly_index,
        ror_threshold=0.6,
        metakey_power_node="Country",
        power_node_members=["Norway"],
        release_capacity_profile=release_capacity_profile,
    )

    hydro_aggregator_sweden_finland = HydroAggregator(
        "EnergyEqDownstream",
        model_year,
        weekly_index,
        ror_threshold=0.38,
        metakey_power_node="Country",
        power_node_members=["Sweden", "Finland"],
        release_capacity_profile=release_capacity_profile,
    )
    config.set_short_term_aggregations([hydro_aggregator_norway, hydro_aggregator_sweden_finland])

    # Solve the model with JulES
    jules.solve(model)


if __name__ == "__main__":
    demo_5_detailed_solve()

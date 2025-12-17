def demo_3_solve_model(num_cpu_cores: int) -> None:
    """
    Solve model.

    1. Read populated model from populate model demo from disk.
    2. Aggregate power nodes in model to elspot areas.
    3. Aggregate hydropower modules
    4. Create a JulES solver object.
    5. Configure JulES.
    6. Solve the model with JulES.
    """
    from framcore import Model
    from framcore.aggregators import HydroAggregator, NodeAggregator
    from framcore.timeindexes import ModelYear, WeeklyIndex
    from framjules import JulES

    import framdemo.demo_utils as du

    model_year = ModelYear(2023)
    first_weather_year = 1995
    num_weather_years = 3
    weekly_index = WeeklyIndex(first_weather_year, num_weather_years)

    # Read populated model from populate model demo from disk.
    model: Model = du.load(du.DEMO_FOLDER / "populated_model.pickle")

    # Aggregate power nodes in model to elspot areas.
    node_aggregator = NodeAggregator("Power", "Elspot", model_year, weekly_index)
    node_aggregator.aggregate(model)

    # Aggregate hydropower modules
    #   HydroAggregator will create one run-of-river hydropower module and one reservoir hydropower module per elspot area.
    #   We use different aggregations for Norway and for Sweden and Finland.
    #   We use a ror_threshold of 0.55 for Norway and 0.38 for Sweden and Finland, which indicates what regulation factor
    #       a hydropower plant must have to be grouped as a reservoir hydropower plant.
    hydro_aggregator_norway = HydroAggregator(
        "EnergyEqDownstream",
        model_year,
        weekly_index,
        ror_threshold=0.55,
        metakey_power_node="Country",
        power_node_members=["Norway"],
    )
    hydro_aggregator_norway.aggregate(model)

    hydro_aggregator_sweden_finland = HydroAggregator(
        "EnergyEqDownstream",
        model_year,
        weekly_index,
        ror_threshold=0.38,
        metakey_power_node="Country",
        power_node_members=["Sweden", "Finland"],
    )
    hydro_aggregator_sweden_finland.aggregate(model)

    # Save aggregated model to disk so we can use it later
    du.save(model, path=du.DEMO_FOLDER / "aggregated_model.pickle")

    # Create a JulES solver object.
    jules = JulES()

    # ----- Configure JulES ------

    # Get object to configure JulES
    config = jules.get_config()

    # Configure serial simulation of model_year over all weather years
    config.set_simulation_mode_serial()
    config.set_weather_years(first_weather_year, num_weather_years)
    config.set_data_period(model_year)
    config.set_simulation_years(first_weather_year, num_weather_years)

    # JulES can use this many cpu cores
    config.set_num_cpu_cores(num_cpu_cores)

    # JulES shall write files to this folder
    config.set_solve_folder(du.DEMO_FOLDER / "base")

    # Get object to configure time resolution
    time_resolution = config.get_time_resolution()

    # 2-day clearing problem with 3-hour market periods and 2-day storage periods
    time_resolution.set_clearing_market_minutes(3 * 60)
    time_resolution.set_clearing_storage_minutes(2 * 24 * 60)
    time_resolution.set_clearing_days(2)

    # 1-day short term prognosis problem with 6-hour market periods and 1-day storage periods
    time_resolution.set_short_market_minutes(6 * 60)
    time_resolution.set_short_storage_minutes(24 * 60)
    time_resolution.set_short_days(1)

    # Configure medium and long term prognosis problem
    # and long term storage end value problem
    #   Total lookahead horizon must be at least 4 years
    #   Long term storage periods should be around 6 weeks long
    #   Medium term horizon should be around 26 weeks long
    #   Long term horizon for end value problems should be around 3 years
    time_resolution.set_target_lookahead_days(4 * 365)
    time_resolution.set_target_long_storage_days(6 * 7)
    time_resolution.set_target_med_days(26 * 7)
    time_resolution.set_target_ev_days(3 * 365)

    # JulES can wait this many days between calculation
    # of opportunity cost of long term storage
    config.set_skipmax_days(21)

    # JulES shall use EUR as currency (e.g. for prices)
    config.set_currency("EUR")

    # JulES shall convert to these units for input and output
    #   We set Power as default so all other energy commodities (35 more)
    #   can use the same units as Power.
    #
    #   We must set units for Hydro and CO2 since these commodities
    #   need different units than Power.
    #
    #   For CO2, we only need to set stock unit, because this commodity
    #   is only used for exogenous nodes.
    #
    #   For more information about stock and flow, see: https://en.wikipedia.org/wiki/Stock_and_flow
    config.set_commodity_units(commodity="Power", stock_unit="GWh", flow_unit="MW", is_default=True)
    config.set_commodity_units(commodity="Hydro", stock_unit="Mm3", flow_unit="m3/s")
    config.set_commodity_units(commodity="CO2", stock_unit="t")

    # Install specified git branches for both JulES and TuLiPa
    config.set_jules_version(jules_branch="master", tulipa_branch="master")

    # Tell JulES where to find Julia and where to install JulES
    if du.JULIA_PATH_EXE is not None:
        config.set_julia_exe_path(du.JULIA_PATH_EXE)
    config.set_julia_depot_path(du.JULIA_PATH_DEPOT)
    config.set_julia_env_path(du.JULIA_PATH_ENV)

    # Solve the model with JulES
    jules.solve(model)


if __name__ == "__main__":
    demo_3_solve_model(num_cpu_cores=8)

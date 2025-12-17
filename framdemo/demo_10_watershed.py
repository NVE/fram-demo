def demo_10_watershed(num_cpu_cores: int) -> None:
    """
    Optimize a single watershed against a price.

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

    """
    from framcore import Model
    from framcore.aggregators import NodeAggregator
    from framcore.components import HydroModule, Node
    from framcore.expressions import get_level_value
    from framcore.timeindexes import ModelYear, WeeklyIndex
    from framcore.utils import isolate_subnodes
    from framjules import JulES

    import framdemo.demo_utils as du
    from framdemo.demo_7_get_data import demo_7_get_data
    from framdemo.demo_8_run_dashboard import demo_8_run_dashboard

    # Read populated model from populate model demo from disk.
    model: Model = du.load(du.DEMO_FOLDER / "detailed" / "model.pickle")  # use results from detailed solve
    model.disaggregate()  # disaggregate, prices will be kept
    # model: Model = du.load(du.DEMO_FOLDER / "populated_model.pickle")  # use populated model if it has prices, possible to run for more years

    # read configured jules solver used in demo 3 from disk
    jules: JulES = du.load(du.DEMO_FOLDER / "base" / "solver.pickle")

    # Pick parameters for the watershed demo
    watershed_name = "BORGUND_H"

    # Make a few configurations (where to save files and to reuse installation)
    config = jules.get_config()
    config.set_solve_folder(du.DEMO_FOLDER / watershed_name)
    config.activate_skip_install_dependencies()
    config.set_num_cpu_cores(num_cpu_cores)
    model_year: ModelYear = config.get_data_period()
    first_weather_year, num_weather_years = config.get_weather_years()
    weekly_index = WeeklyIndex(first_weather_year, num_weather_years)

    # Isolate system
    isolate_subnodes(model, "Power", "Watershed", watershed_name)

    # Aggregate power nodes in model to elspot areas.
    node_aggregator = NodeAggregator("Power", "EMPS", model_year, weekly_index)
    node_aggregator.aggregate(model)

    # Set all power nodes to exogenous
    for k, v in model.get_data().items():
        if isinstance(v, Node) and v.get_commodity() == "Power":
            v.set_exogenous()

    # Print model content
    du.display("Model content for watershed demo:", model.get_content_counts())

    # Solve the model with JulES
    jules.solve(model)

    # Show some water values (TODO: Move to dashboard)
    for k, v in model.get_data().items():
        if isinstance(v, HydroModule) and v.get_reservoir():
            water_values = v.get_water_value().get_scenario_vector(model, weekly_index, model_year, "EUR/Mm3")
            eneq = v.get_meta("EnergyEqDownstream").get_value()
            eneq_value = get_level_value(eneq, model, "MWh/Mm3", model_year, weekly_index, False)
            eneq_vector = water_values / eneq_value
            print(f"HydroModule {k} water values (EUR/MWh): {eneq_vector}")

    # Get data (NB! Will overwrite dashboard data from previous demos)
    demo_7_get_data(solve_names=[watershed_name], detailed_solve_name=watershed_name)

    # Run dashboard
    demo_8_run_dashboard()


if __name__ == "__main__":
    demo_10_watershed(num_cpu_cores=1)

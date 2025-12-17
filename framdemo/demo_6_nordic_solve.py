def demo_6_nordic_solve(num_cpu_cores: int) -> None:
    """
    Use same as demo 4, but here we only simulate nordic zones, using prices from demo 3 as exogenous prices.

    1. Read aggregated model from demo 3 from disk
    2. Filter dataset to only contain Nordic power market
    3. Read configured JulES solver used in demo 3 from disk
    4. Make a few configurations
    5. Increase demand in Norway with 20 percent
    6. Solve the modified model with JulES
    """
    from framcore import Model
    from framcore.components import Demand
    from framcore.utils import isolate_subnodes
    from framjules import JulES

    # import code written only for this demo (common names and useful functions)
    import framdemo.demo_utils as du

    # read solved model from demo 3 from disk
    model: Model = du.load(du.DEMO_FOLDER / "base" / "model.pickle")

    # Filter dataset to only contain Nordic power market
    # this will make price zones trading with the nordics
    # exogenous, and price results from demo 3 will be used
    # to represent the price in these zones
    isolate_subnodes(model, "Power", "NordicRegion", ["Inside"])

    # read configured jules solver used in demo 3 from disk
    jules: JulES = du.load(du.DEMO_FOLDER / "base" / "solver.pickle")

    # Make a few configurations (where to save files and to reuse installation)
    config = jules.get_config()
    config.set_solve_folder(du.DEMO_FOLDER / "modified_nordic")
    config.activate_skip_install_dependencies()
    config.set_num_cpu_cores(num_cpu_cores)

    # Increase demand in norwegian price areas with 20 percent
    for value in model.get_data().values():
        if isinstance(value, Demand) and value.get_node() in ["NO1", "NO2", "NO3", "NO4", "NO5"]:
            value.get_capacity().scale(1.2)

    # Solve the model with JulES
    jules.solve(model)


if __name__ == "__main__":
    demo_6_nordic_solve(num_cpu_cores=8)

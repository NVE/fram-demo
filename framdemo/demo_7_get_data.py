def demo_7_get_data():
    """
    Writes results to h5 files that will be sent to dashboard.
    
    1. Get prices for power nodes with existing price data in model for different solves and saves to dashboard_prices.h5 in demo folder.
    2. Get regional volumes for all countries in model for different solves and saves to dashboard_volumes.h5 in demo folder.
    3. Get hydro data for Norway, Sweden and Finland (*zones with hydropower data in model*) for different solves and saves to dashboard_hydro.h5 in demo folder.
    """
    import numpy as np
    import pandas as pd
    import datetime

    from framcore import Model
    from framcore.aggregators import HydroAggregator, NodeAggregator
    from framcore.components import HydroModule, Node
    from framcore.events import send_info_event, send_warning_event
    from framcore.expressions import get_level_value
    from framcore.querydbs import CacheDB
    from framcore.timeindexes import AverageYearRange, DailyIndex, ModelYear, ProfileTimeIndex
    from framcore.utils import get_regional_volumes

    from framjules import JulES

    # import code written only for this demo (common names and useful functions)
    import framdemo.demo_utils as du


    # output file paths
    h5_file_path_prices = du.DEMO_FOLDER / "dashboard_prices.h5"
    h5_file_path_volumes = du.DEMO_FOLDER / "dashboard_volumes.h5"
    h5_file_path_hydro = du.DEMO_FOLDER / "dashboard_hydro.h5"

    # ==========================
    # Section: Price data
    # ==========================

    # get all power nodes

    solve_names = ["base", "modified", "detailed", "modified_nordic"]

    # read configured jules solver used in demo 3 from disk
    jules: JulES = du.load(du.DEMO_FOLDER / solve_names[0] / "solver.pickle")

    # get info from config
    config = jules.get_config()
    first_simulation_year, num_simulation_years = config.get_simulation_years()
    currency = config.get_currency()
    price_unit = f"{currency}/MWh"
    price_time_resolution = "Days"
    daily_index = DailyIndex(first_simulation_year, num_simulation_years)
    data_period: ModelYear = config.get_data_period()
    model_year = data_period.get_start_time().isocalendar().year

    common_metadata_is_not_written = True
    with pd.HDFStore(h5_file_path_prices, mode="w") as store:
        for solve_name in solve_names:
            send_info_event(None, message=f"Getting prices for solve {solve_name}")

            try:
                model: Model = du.load(du.DEMO_FOLDER / f"{solve_name}/model.pickle")
            except Exception:
                send_warning_event(None, message=f"Found no model for {solve_name}")
                continue

            db = CacheDB(model)
            data = db.get_data()

            for key, value in data.items():
                if isinstance(value, Node) and value.get_commodity() == "Power":
                    sanitized_zone = key.replace(" ", "_")
                    store_key = f"{solve_name}/{sanitized_zone}"
                    vector = value.get_price().get_scenario_vector(db, daily_index, data_period, price_unit)
                    store.put(key=store_key, value=pd.DataFrame({"value": vector}))

            if common_metadata_is_not_written:
                store.root._v_attrs.global_metadata = {
                    "model_year": model_year,
                    "weather_years": list(
                        range(first_simulation_year, first_simulation_year + num_simulation_years),
                    ),
                    "currency": price_unit,
                    "time_resolution": price_time_resolution,
                }
                common_metadata_is_not_written = False

    send_info_event(None, message=f"Saved price data to {h5_file_path_prices}")

    # ==========================
    # Section: Regional volumes
    # ==========================
    category_total = "Total"
    with pd.HDFStore(h5_file_path_volumes, mode="w") as store:
        for solve_name in solve_names:
            send_info_event(None, message=f"Getting regional volumes for solve {solve_name}")

            try:
                model: Model = du.load(du.DEMO_FOLDER / f"{solve_name}/model.pickle")
            except Exception:
                continue

            db = CacheDB(model)
            data = db.get_data()

            regional_volumes = get_regional_volumes(
                db,
                commodity="Power",
                node_category="Country",
                production_category="HighLevelSource",
                consumption_category="TotalConsumption",
                data_period=data_period,
                scenario_period=AverageYearRange(first_simulation_year, num_simulation_years),
                unit="GWh/year",
            )

            production = regional_volumes.get_production()
            consumption = regional_volumes.get_consumption()
            _import = regional_volumes.get_import()
            export = regional_volumes.get_export()

            for name, d in [("Production", production), ("Consumption", consumption)]:
                for country, category_data in d.items():
                    sanitized_country = country.replace(" ", "_")
                    total = None
                    for category, volume in category_data.items():
                        sanitized_category = "NA" if category is None else category
                        assert sanitized_category != category_total
                        key = f"{solve_name}/{sanitized_country}/{name}/{sanitized_category}"
                        store.put(key=key, value=pd.DataFrame({"volume": volume}))
                        if total is None:
                            total = volume
                        else:
                            np.add(total, volume, out=total)
                    key = f"{solve_name}/{sanitized_country}/{name}/{category_total}"
                    store.put(key=key, value=pd.DataFrame({"volume": total}))

            for name, d in [("Import", _import), ("Export", export)]:
                for country, category_data in d.items():
                    sanitized_country = country.replace(" ", "_")
                    total = None
                    for trading_partner, volume in category_data.items():
                        sanitized_trading_partner = trading_partner.replace(" ", "_")
                        key = f"{solve_name}/{sanitized_country}/{name}/{sanitized_trading_partner}"
                        store.put(key=key, value=pd.DataFrame({"volume": volume}))
                        if total is None:
                            total = volume
                        else:
                            np.add(total, volume, out=total)
                    key = f"{solve_name}/{sanitized_country}/{name}/{category_total}"
                    store.put(key=key, value=pd.DataFrame({"volume": total}))

    send_info_event(None, message=f"Saved regional volume data to {h5_file_path_volumes}")

    # ==========================
    # Section: Hydro data
    # ==========================

    countries = ["Norway", "Sweden", "Finland"]
    with pd.HDFStore(h5_file_path_hydro, mode="w") as store:
        for solve_name in solve_names:
            send_info_event(None, message=f"Getting hydro volumes for solve {solve_name}")

            try:
                model: Model = du.load(du.DEMO_FOLDER / f"{solve_name}/model.pickle")
            except Exception:
                continue

            if solve_name != "detailed":
                model.disaggregate()

            node_aggregator = NodeAggregator("Power", "Country", data_period, daily_index)
            node_aggregator.aggregate(model)
            hydro_aggregator = HydroAggregator("EnergyEqDownstream", data_period, daily_index)
            hydro_aggregator.aggregate(model)

            db = CacheDB(model)

            data = dict()
            for country in countries:
                data[country] = dict()
                for category in ["reservoir_volume", "reservoir_capacity", "production", "inflow"]:
                    data[country][category] = np.zeros(daily_index.get_num_periods(), dtype=np.float32)

            for v in db.get_data().values():
                if not isinstance(v, HydroModule):
                    continue

                # works since hydro module is aggregated to country
                country = v.get_generator().get_power_node()

                reservoir = v.get_reservoir()
                if reservoir is not None:
                    data[country]["reservoir_volume"] += reservoir.get_volume().get_scenario_vector(db, daily_index, data_period, "Mm3")
                    data[country]["reservoir_capacity"] += reservoir.get_capacity().get_scenario_vector(db, daily_index, data_period, "Mm3")

                production = v.get_generator().get_production()
                data[country]["production"] += production.get_scenario_vector(db, daily_index, data_period, "MW")

                inflow = v.get_inflow()
                if inflow is not None:
                    data[country]["inflow"] += inflow.get_scenario_vector(db, daily_index, data_period, "m3/s")

            for country, area_data in data.items():
                if float(area_data["reservoir_capacity"].max()) == 0:
                    area_data["reservoir_percentage"] = area_data["reservoir_capacity"]
                else:
                    area_data["reservoir_percentage"] = area_data["reservoir_volume"] / area_data["reservoir_capacity"]

            for country, area_data in data.items():
                for key, vector in area_data.items():
                    store.put(key=f"{solve_name}/{country}/{key}", value=pd.DataFrame({"value": vector}))

    send_info_event(None, message=f"Saved hydro data to {h5_file_path_hydro}")


    # detailed hydro data
     
    # input solve name and file paths
    solve_name = "detailed"

    solve_dir = du.DEMO_FOLDER / solve_name
    solver_path = solve_dir / "solver.pickle"
    model_path = solve_dir / "model.pickle"

    if not (solve_dir.is_dir() and solver_path.is_file() and model_path.is_file()):
        return

    # output file paths
    output_file_path = du.DEMO_FOLDER / "dashboard_detailed_hydro.h5"

    # get info from configured jules solver
    jules: JulES = du.load(solver_path)
    config = jules.get_config()
    first_simulation_year, num_simulation_years = config.get_simulation_years()
    currency = config.get_currency()
    clearing_market_minutes = config.get_time_resolution().get_clearing_market_minutes()

    # derive query inputs
    data_period: ModelYear = config.get_data_period()
    model_year = data_period.get_start_time().isocalendar().year
    data_dim = ModelYear(model_year)
    scen_dim_yr = AverageYearRange(first_simulation_year, num_simulation_years)
    scen_dim_market = ProfileTimeIndex(first_simulation_year, num_simulation_years, period_duration=datetime.timedelta(minutes=clearing_market_minutes), is_52_week_years=False)

    # get model
    model: Model = du.load(du.DEMO_FOLDER / solve_name / "model.pickle")
    db = CacheDB(model)
    data = model.get_data()

    # create module_df
    send_info_event(demo_7_get_data, "creating module_df")
    eneq_dict = dict()
    rows = []
    for key, value in data.items():
        if not isinstance(value, HydroModule):
            continue
        generator = value.get_generator()
        if generator is not None:
            x = float(generator.get_production().get_scenario_vector(db, scen_dim_yr, data_dim, "GWh/year")[0])
            rows.append((key, "ProductionGWhPerYear", x))
        pump = value.get_pump()
        if pump is not None:
            x = float(pump.get_power_consumption().get_scenario_vector(db, scen_dim_yr, data_dim, "GWh/year")[0])
            rows.append((key, "PumpConsumptionGWhPerYear", x))
        reservoir = value.get_reservoir()
        if reservoir is None:
            continue
        eneq = value.get_meta("EnergyEqDownstream")
        if eneq is None:
            continue
        eneq_kwh_per_m3 = get_level_value(eneq.get_value(), db, "kWh/m3", data_dim, scen_dim_yr, is_max=False)
        if eneq_kwh_per_m3 <= 0:
            continue
        eneq_dict[key] = eneq_kwh_per_m3
        reservoir_cap_mm3 = float(reservoir.get_capacity().get_scenario_vector(db, scen_dim_yr, data_dim, "Mm3").max())
        reservoir_cap_gwh = eneq_kwh_per_m3 * reservoir_cap_mm3
        if reservoir_cap_mm3 <= 0:
            continue
        # TODO: replace dummy data with hydro_module.get_scenario_vector call
        water_value = 50
        # water_value = value.get_water_value().get_scenario_vector(db, scen_dim_yr, data_dim, f"{currency}/m3")
        water_value = water_value / eneq_kwh_per_m3 # EUR/m3 to EUR/kWh
        water_value = water_value * 1000.0          # EUR/kWh to EUR/MWh
        rows.append((key, "ReservoirCapacityMm3", reservoir_cap_mm3))
        rows.append((key, "ReservoirCapacityGWh", reservoir_cap_gwh))
        rows.append((key, "EnergyEqDownstream", eneq_kwh_per_m3))
        rows.append((key, "WaterValueEURPerMWh", water_value))
    modules_df = pd.DataFrame(rows, columns=["Module", "Type", "Value"])

    # find biggest reservoirs
    send_info_event(demo_7_get_data, "finding biggest reservoirs")
    biggest = modules_df.copy()
    biggest = biggest[biggest["Type"] == "ReservoirCapacityGWh"]
    biggest = biggest.sort_values(by="Value", ascending=False)
    biggest = biggest.reset_index(drop=True)
    biggest = list(biggest.iloc[:20]["Module"])

    # find price area for each biggest reservoir
    power_node_dict = dict()
    for key in biggest:
        next_key = key
        power_node = None
        while not power_node:
            hydro_module: HydroModule = data[next_key]
            generator = hydro_module.get_generator()
            if generator is not None:
                power_node = generator.get_power_node()
                break
            pump = hydro_module.get_pump()
            if pump is not None:
                power_node = pump.get_power_node()
                break
            next_key = hydro_module.get_release_to()
        power_node_dict[key] = power_node

    # get prices for each relevant power node
    power_prices = dict()
    for key in set(power_node_dict.values()):
        node: Node = data[key]
        price = node.get_price().get_scenario_vector(db, scen_dim_market, data_dim, f"{currency}/MWh")
        power_prices[key] = price

    # create series_df for the biggest reservoirs
    send_info_event(demo_7_get_data, "creating series_df for biggest reservoirs")
    series_df = dict()
    for key in biggest:
        hydro_module: HydroModule = data[key]
        reservoir = hydro_module.get_reservoir()
        eneq_kwh_per_m3 = eneq_dict[key]
        reservoir_cap_mm3_series = reservoir.get_capacity().get_scenario_vector(db, scen_dim_market, data_dim, "Mm3")
        reservoir_vol_mm3_series = reservoir.get_volume().get_scenario_vector(db, scen_dim_market, data_dim, "Mm3")
        reservoir_filling = reservoir_vol_mm3_series / reservoir_cap_mm3_series
        # TODO: replace dummy data with hydro_module.get_scenario_vector call
        water_values = reservoir_filling.copy()
        water_values.fill(50.0)
        # water_values = hydro_module.get_water_value().get_scenario_vector(db, scen_dim_market, data_dim, f"{currency}/m3")
        np.multiply(water_value, 1000.0 / eneq_kwh_per_m3, out=water_values)
        series_df[f"ReservoirFilling/{key}"] = reservoir_filling
        series_df[f"WaterValueEURPerMWh/{key}"] = water_values
        series_df[f"PowerPriceEURPerMWh/{key}"] = power_prices[power_node_dict[key]]

    series_df = pd.DataFrame(series_df)

    # write result file
    send_info_event(demo_7_get_data, f"writing result file: {output_file_path}")
    with pd.HDFStore(output_file_path, mode="w") as store:
        store.put(key="modules_df", value=modules_df)
        store.put(key="series_df", value=series_df)
    
    
if __name__ == "__main__":
    demo_7_get_data()

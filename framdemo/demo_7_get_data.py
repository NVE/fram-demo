def demo_7_get_data():
    """Writes results to h5 files that will be sent to dashboard."""
    import numpy as np
    import pandas as pd
    from framcore import Model
    from framcore.aggregators import HydroAggregator, NodeAggregator
    from framcore.components import HydroModule, Node
    from framcore.events import send_info_event, send_warning_event
    from framcore.querydbs import CacheDB
    from framcore.timeindexes import AverageYearRange, DailyIndex, ModelYear
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

    solve_names = ["base", "modified", "detailed", "nordic"]

    # read configured jules solver used in demo 3 from disk
    jules: JulES = du.load(du.DEMO_FOLDER / solve_names[0] / "solver.pickle")

    # Make a few configurations
    #   Where to save files
    #   To reuse dependencies already installed in demo 3
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


if __name__ == "__main__":
    demo_7_get_data()

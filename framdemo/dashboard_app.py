"""Simple demo dashboard app."""

import contextlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import framdemo.demo_utils as du

# output file paths
h5_file_path_prices = du.DEMO_FOLDER / "dashboard_prices.h5"
h5_file_path_volumes = du.DEMO_FOLDER / "dashboard_volumes.h5"
h5_file_path_hydro = du.DEMO_FOLDER / "dashboard_hydro.h5"

if not h5_file_path_prices.exists():
    message = f"HDF5 file not found at {h5_file_path_prices}"
    st.error(message)
    raise FileNotFoundError(message)

if not h5_file_path_volumes.exists():
    message = f"HDF5 file not found at {h5_file_path_volumes}"
    st.error(message)
    raise FileNotFoundError(message)

if not h5_file_path_hydro.exists():
    message = f"HDF5 file not found at {h5_file_path_hydro}"
    st.error(message)
    raise FileNotFoundError(message)


# Setting up Dashboard infrastructure
st.title("Simple demo dashboard")
st.write("Path to result files:", du.DEMO_FOLDER)
st.sidebar.title("Navigation")
menu_option = st.sidebar.radio(
    label="Select a page:",
    options=["Price", "Volume", "Hydro"],
    index=0,
)
st.sidebar.markdown("[About FRAM demo](https://nve.github.io/fram-demo/)")
st.sidebar.title("Filters")

# pages

if menu_option == "Price":
    # get keys and metadata
    with pd.HDFStore(h5_file_path_prices, mode="r") as store:
        keys = store.keys()
        # keys = [key.lstrip("/") for key in keys]
        v_attrs = store.root._v_attrs  # noqa: SLF001  # TODO: is there a public method to access this?
        currency = v_attrs.global_metadata["currency"]
        model_year = v_attrs.global_metadata["model_year"]
        weather_years = v_attrs.global_metadata["weather_years"]
        time_resolution = v_attrs.global_metadata["time_resolution"]

    zones = sorted(list(set(key.split("/")[2] for key in keys)))
    solve_names = sorted(list(set(key.split("/")[1] for key in keys)))

    selected_solves = []
    st.sidebar.write("Select solves:")
    for i, solve_name in enumerate(solve_names):
        if st.sidebar.checkbox(label=solve_name, value=i == 0):
            selected_solves.append(solve_name)

    selected_zones = []
    st.sidebar.write("Select zones")
    for i, zone in enumerate(zones):
        if st.sidebar.checkbox(label=zone, value=i == 0):
            selected_zones.append(zone)

    # read data
    combined_data_list = []
    yearly_prices = []
    with pd.HDFStore(h5_file_path_prices, mode="r") as store:
        if selected_solves:
            for zone in zones:
                for solve_name in selected_solves:
                    store_key = f"/{solve_name}/{zone}"
                    data_key = f"{solve_name} {zone}"
                    if store_key in store:
                        data = store[store_key]
                        data = data.rename(columns={data.columns[0]: data_key})
                        combined_data_list.append(data)
                        yearly_prices.append({"Solve": solve_name, "Zone": zone, "EUR/MWh": float(data.mean().iloc[0])})

    # yearly prices bar plot
    if yearly_prices:
        df = pd.DataFrame(yearly_prices)
        df = df.round(2)
        fig = px.bar(
            df, 
            x="Zone", 
            y="EUR/MWh", 
            color="Solve", 
            barmode="group",
            title=f"Mean price per zone, grouped by selected solves",
        )
        fig.update_layout(xaxis={'categoryorder': 'sum descending'})
        st.plotly_chart(fig, use_container_width=True)

    # daily prices plot
    if selected_solves and selected_zones:
        df = pd.concat(combined_data_list, axis=1)
        columns = [f"{solve} {zone}" for solve in selected_solves for zone in selected_zones]
        columns = [c for c in columns if c in df.columns]
        if columns:
            df = df[columns]
            fig = px.line(df, title=f"Price in {model_year}, weather years {weather_years}")
            fig.update_layout(
                xaxis_title=time_resolution,
                yaxis_title=currency,
            )
            st.plotly_chart(fig, use_container_width=True)
    elif selected_zones and not selected_solves:
        st.info("Solve not selected.")
    elif not selected_zones and selected_solves:
        st.info("Zone not selected.")
    else:
        st.info("Zone and solve not selected.")


if menu_option == "Volume":
    # read data
    with pd.HDFStore(h5_file_path_volumes, mode="r") as store:
        production_data = []
        production_data_tech = []
        consumption_data = []
        import_data = []
        export_data = []
        solve_names = set()

        for key in store:
            parts = key.strip("/").split("/")
            solve_name = parts[0]
            solve_names.add(solve_name)
            country = parts[1]
            category = parts[2] if len(parts) > 2 else None
            tech = parts[3] if len(parts) > 3 else None

            if "Production/Total" in key:
                volume = store[key]["volume"].sum()
                if volume == 0:
                    continue
                if country.startswith("EX_"):
                    continue
                production_data.append(
                    {
                        "Solve": solve_name,
                        "Country": country,
                        "Technology": tech,
                        "Volume": volume,
                    },
                )

            if "Production" in key:
                tech = parts[3] if len(parts) > 3 else None
                if tech == "Total":
                    continue
                volume = store[key]["volume"].sum()
                if volume == 0:
                    continue
                if country.startswith("EX_"):
                    continue
                production_data_tech.append(
                    {
                        "Solve": solve_name,
                        "Country": country,
                        "Technology": tech,
                        "Volume": volume,
                    },
                )

            elif "Consumption/Total" in key and "Consumption/TotalConsumption" not in key:
                volume = store[key]["volume"].sum()
                if volume == 0:
                    continue
                if country.startswith("EX_"):
                    continue
                consumption_data.append(
                    {
                        "Solve": solve_name,
                        "Country": country,
                        "Category": category,
                        "Volume": volume,
                    },
                )

            elif "Import" in key and "Total" not in key:
                _, country, _, trade_partner = key.strip("/").split("/")
                volume = store[key]["volume"].sum()
                import_data.append(
                    {
                        "Solve": solve_name,
                        "Country": country,
                        "Trade Partner": trade_partner,
                        "Volume": volume,
                    },
                )

            elif "Export" in key and "Total" not in key:
                _, country, _, trade_partner = key.strip("/").split("/")
                volume = store[key]["volume"].sum()
                export_data.append(
                    {
                        "Solve": solve_name,
                        "Country": country,
                        "Trade Partner": trade_partner,
                        "Volume": volume,
                    },
                )

    solve_names = sorted(list(solve_names))

    production_df = pd.DataFrame(production_data).drop_duplicates()
    consumption_df = pd.DataFrame(consumption_data).drop_duplicates()
    import_df = pd.DataFrame(import_data).drop_duplicates()
    export_df = pd.DataFrame(export_data).drop_duplicates()

    # may become duplicated due to uncategorized pump or transport loss demand (TODO find out)
    # this gives correct volumes
    consumption_df = consumption_df.pivot_table(index=["Solve", "Country", "Category"],values="Volume", aggfunc="max")
    consumption_df = consumption_df.reset_index()

    df = pd.concat([production_df, consumption_df])
    countries = sorted(list(df[df["Volume"] > 0]["Country"].unique()))

    # create filters
    selected_solves = []
    st.sidebar.write("Select solves:")
    for i, solve_name in enumerate(solve_names):
        if st.sidebar.checkbox(label=solve_name, value=i == 0):
            selected_solves.append(solve_name)

    selected_country = st.sidebar.radio(
        label="Select a country:",
        options=countries,
        index=0,
    )

    # total production and consumption bar plot
    production_df["Type"] = "Production"
    consumption_df["Type"] = "Consumption"
    combined_data = pd.concat([production_df, consumption_df])
    combined_data = combined_data[combined_data["Solve"].isin(selected_solves)]
    combined_data["Volume"] /= 1000.0
    bars = []
    for type_ in ["Production", "Consumption"]:
        for solve in selected_solves:
            df = combined_data
            df = df[(df["Type"] == type_) & (df["Solve"] == solve)]
            bar =go.Bar(
                x=df["Country"],
                y=df["Volume"].round(1),
                name=f"{solve} {type_}",
                offsetgroup=f"{solve} {type_}",
                customdata=[solve, type_],
                hovertemplate="<b>Country:</b> %{x}<br>" +
                            "<b>Volume:</b> %{y:.1f} TWh/year<br>" +
                            f"<b>Solve:</b> {solve}<br>" +
                            f"<b>Type:</b> {type_}<extra></extra>"        
            )
            bars.append(bar)
    layout = go.Layout(
        title={'text': 'Production and Consumption for each country, grouped by selected solves'},
        yaxis={'title': {'text': 'TWh/year'}},
        barmode='group',
    )
    fig = go.Figure(data=bars, layout=layout)
    fig.update_layout(xaxis={'categoryorder': 'category ascending'})    
    st.plotly_chart(fig)

    # stacked production tech bar plot
    production_tech_df = pd.DataFrame(production_data_tech)
    production_tech_df = production_tech_df[production_tech_df["Solve"].isin(selected_solves)]
    production_tech_df["Volume"] /= 1000.0
    techs = sorted(list(set(production_tech_df["Technology"])))
    bars = []
    for solve in selected_solves:
        for tech in techs:
            df = production_tech_df
            df = df[(df["Technology"] == tech) & (df["Solve"] == solve)]
            bar =go.Bar(
                x=df["Country"],
                y=df["Volume"].round(1),
                name=f"{solve} {tech}",
                offsetgroup=solve,
                customdata=[solve, tech],
                hovertemplate="<b>Country:</b> %{x}<br>" +
                            "<b>Volume:</b> %{y:.1f} TWh/year<br>" +
                            f"<b>Solve:</b> {solve}<br>" +
                            f"<b>Technology:</b> {tech}<extra></extra>"        
            )
            bars.append(bar)
    layout = go.Layout(
        title={'text': 'Production stacked on technology for each country, grouped by selected solves'},
        yaxis={'title': {'text': 'TWh/year'}},
        barmode='stack',
    )
    fig = go.Figure(data=bars, layout=layout)
    fig.update_layout(xaxis={'categoryorder': 'category ascending'})    
    st.plotly_chart(fig)

    # import and export bar chart
    import_data = import_df[import_df["Country"] == selected_country].copy()
    export_data = export_df[export_df["Country"] == selected_country].copy()
    import_data.loc[:, "Type"] = "Import"
    export_data.loc[:, "Type"] = "Export"
    combined_data = pd.concat([import_data, export_data])
    combined_data["Volume"] /= 1000
    trade_partners = sorted(list(set(combined_data["Trade Partner"])))
    bars = []
    for solve in selected_solves:
        for direction in ["Import", "Export"]:
            df = combined_data
            df = df[(df["Type"] == direction) & (df["Solve"] == solve)]
            bar =go.Bar(
                x=df["Trade Partner"],
                y=df["Volume"].round(1),
                name=f"{solve} {direction}",
                offsetgroup=solve,
                customdata=[solve, direction],
                hovertemplate="<b>Trade:</b> %{y:.1f} TWh/year<br>" +
                            f"<b>Type:</b> {direction}<br>" +
                            f"<b>Solve:</b> {solve}<br>"
            )
            bars.append(bar)
    layout = go.Layout(
        title={'text': f"{selected_country}'s trade with other countries, grouped by selected solves"},
        yaxis={'title': {'text': 'TWh/year'}},
        barmode='stack',
    )
    fig = go.Figure(data=bars, layout=layout)
    fig.update_layout(xaxis={'categoryorder': 'category ascending'})    
    st.plotly_chart(fig)


if menu_option == "Hydro":    
    # read metadata
    solve_names = set()
    countries = set()
    with pd.HDFStore(h5_file_path_hydro, mode="r") as store:
        for key in store.keys():
            if "production" in key:
                __, solve, country, category = key.split("/")
                solve_names.add(solve)
                countries.add(country)
    solve_names = sorted(list(solve_names))
    countries = sorted(list(countries))

    # create filters
    selected_solves = []
    st.sidebar.write("Select solves:")
    for i, solve_name in enumerate(solve_names):
        if st.sidebar.checkbox(label=solve_name, value=i == 0):
            selected_solves.append(solve_name)

    selected_country = st.sidebar.radio(
        label="Select a country:",
        options=countries,
        index=1,
    )

    # read data
    with pd.HDFStore(h5_file_path_hydro, mode="r") as store:
        hydro_data = dict()
        for category in ["inflow", "production", "reservoir_percentage", "reservoir_capacity"]:
            hydro_data[category] = dict()
            for selected_solve in selected_solves:
                store_key = f"/{selected_solve}/{selected_country}/{category}"
                data_key = f"{selected_solve}"
                with contextlib.suppress(Exception):
                    hydro_data[category][data_key] = store[store_key]["value"]
    for key, value in hydro_data.items():
        hydro_data[key] = pd.DataFrame(data=value)

    # display data in app
    reservoir_df: pd.DataFrame = hydro_data["reservoir_percentage"]
    if not reservoir_df.empty:
        reservoir_capacity_df: pd.DataFrame = hydro_data["reservoir_capacity"]
        reservoir_capacity = dict()
        for selected_solve in selected_solves:
            data_key = f"{selected_solve}"
            reservoir_capacity[data_key] = round(float(reservoir_capacity_df[data_key].max())/1000.0, 1)
        new_columns = {k: f"{k} (capacity {v} TWh)" for k, v in reservoir_capacity.items()}
        reservoir_df.rename(columns=new_columns, inplace=True)
        reservoir_df *= 100
        fig = px.line(
            reservoir_df,
            title=f"{selected_country}'s hydro reservoir filling, gouped by selected solve",
            labels={"index": "Days"},
        )
        fig.update_yaxes(range=[0, 101])
        fig.update_yaxes(title="")
        st.plotly_chart(fig)

    production_df: pd.DataFrame = hydro_data["production"]
    if not production_df.empty:
        production_df /= 1000.0 # MW to GW
        production_fig = px.line(
            production_df,
            title=f"{selected_country}'s daily hydro production (GW), gouped by selected solve",
            labels={"value": "GW", "index": "Days"},
        )
        st.plotly_chart(production_fig)

    inflow_df: pd.DataFrame = hydro_data["inflow"]
    if not inflow_df.empty:
        inflow_df *= (3.6 / 1000) # m3/s to GW
        inflow_fig = px.line(
            inflow_df,
            title=f"{selected_country}'s daily hydro inflow (GW), gouped by selected solve",
            labels={"value": "GW", "index": "Days"},
        )
        st.plotly_chart(inflow_fig)

    # detailed hydro
    h5_file_path_detailed_hydro = du.DEMO_FOLDER / "dashboard_detailed_hydro.h5"
    modules_df = pd.DataFrame()
    series_df = pd.DataFrame()
    with contextlib.suppress(Exception):
        with pd.HDFStore(h5_file_path_detailed_hydro, mode="r") as store:
            modules_df = store.get("/modules_df")
            series_df = store.get("/series_df")

    def get_module_name(s: str):
        parts = s.split("_")
        if len(parts) >= 4:
            return "_".join(parts[3:])
        return s

    if not modules_df.empty:
        modules_df["Name"] = modules_df["Module"].apply(get_module_name)

    # add reservoirs filter
    selected_reservoirs = []
    name_to_key = dict()
    if not series_df.empty:
        st.sidebar.write("Select big reservoirs:")
        for i, col_name in enumerate(series_df.columns):
            if col_name.startswith("ReservoirFilling"):
                module_key = col_name.replace("ReservoirFilling/", "")
                module_name = get_module_name(module_key)
                name_to_key[module_name] = module_key
                if st.sidebar.checkbox(label=module_name, value=i == 0):
                    selected_reservoirs.append(module_name)

    # top n yearly generation
    if not modules_df.empty:
        n = 20
        df = modules_df.copy()
        df = df[df["Type"] == "ProductionGWhPerYear"]
        df = df.sort_values(by="Value", ascending=False)
        df = df.reset_index(drop=True)
        df = df.iloc[:n]
        if not df.empty:
            df["TWh/year"] = (df["Value"] / 1000.0).round(1)
            fig = px.bar(
                df,
                x="Name",
                y="TWh/year",
                title=f"Top {n} generating modules in detailed solve",
            )
            fig.update_xaxes(type='category', title="")
            st.plotly_chart(fig)

    # top n yearly pump
    if not modules_df.empty:
        n = 20
        df = modules_df.copy()
        df = df[df["Type"] == "PumpConsumptionGWhPerYear"]
        df = df.sort_values(by="Value", ascending=False)
        df = df.reset_index(drop=True)
        df = df.iloc[:n]
        if not df.empty:
            df["TWh/year"] = (df["Value"] / 1000.0).round(1)
            fig = px.bar(
                df,
                x="Name",
                y="TWh/year",
                title=f"Top {n} pumping modules in detailed solve",
            )
            fig.update_xaxes(type='category', title="")
            st.plotly_chart(fig)

    # selected reservoir filling
    if selected_reservoirs:
        selected_columns = [f"ReservoirFilling/{name_to_key[name]}" for name in selected_reservoirs]
        df = series_df[selected_columns].copy()

        capacities = modules_df.copy()
        capacities = capacities[capacities["Name"].isin(selected_reservoirs)]
        capacities = capacities[capacities["Type"] == "ReservoirCapacityGWh"]
        capacities["Value"] = (capacities["Value"] / 1000.0).round(1)
        capacities = dict(zip(capacities["Name"], capacities["Value"], strict=True))

        new_names = dict(zip(selected_columns, selected_reservoirs, strict=True))
        for key, name in new_names.items():
            new_names[key] = f"{name} (capacity {capacities[name]} TWh)"

        df.rename(columns=new_names, inplace=True)

        df = (df * 100).round(1)

        fig = px.line(
            df,
            title=f"Reservoir filling percentage for selected reservoirs from detailed solve",
        )
        fig.update_xaxes(title="Days")
        fig.update_yaxes(title="", range=[0, 101])
        st.plotly_chart(fig)



        


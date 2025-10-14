def demo_2_populate_model():
    """
    Populate model.

    1. Create model.
    2. Use populator to fill model with data
    3. Save model to disk for use in upcoming demos.
    4. Display model content before and after population.
    """
    from datetime import timedelta

    import numpy as np
    from framcore import Model
    from framcore.components import HydroModule
    from framcore.timeindexes import OneYearProfileTimeIndex
    from framcore.timevectors import ListTimeVector
    from framdata import NVEEnergyModelPopulator

    import framdemo.demo_utils as du

    # create empty model
    model = Model()

    # register model content before populate (for display below)
    before = model.get_content_counts()

    # create populator connected to data source and
    # use it to populate the model with data objects
    populator = NVEEnergyModelPopulator(source=du.DEMO_FOLDER / "database", validate=True)
    populator.populate(model)

    # Restrict the release capacity of the hydropower plants with a profile.
    values = np.array([0.93, 0.88, 0.89, 0.90])
    timeindex = OneYearProfileTimeIndex(period_duration=timedelta(weeks=13), is_52_week_years=True)
    model.get_data()["release_capacity_profile"] = ListTimeVector(timeindex, values, unit=None, is_max_level=None, is_zero_one_profile=True)
    for component in model.get_data().values():
        if isinstance(component, HydroModule) and component.get_generator():
            component.get_release_capacity().set_profile("release_capacity_profile")

    # register model content after populate (for display below)
    after = model.get_content_counts()

    # save populated model to disk so we can use it later
    du.save(model, path=du.DEMO_FOLDER / "populated_model.pickle")

    # display how model was changed
    du.display("Model content before populate:", before)
    du.display("Model content after populate:", after)


if __name__ == "__main__":
    demo_2_populate_model()

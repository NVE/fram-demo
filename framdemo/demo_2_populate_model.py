def demo_2_populate_model():
    """
    Populate model.

    1. Create model.
    2. Use populator to fill model with data
    3. Save model to disk for use in upcoming demos.
    4. Display model content before and after population.
    """
    from framcore import Model
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

    # register model content after populate (for display below)
    after = model.get_content_counts()

    # save populated model to disk so we can use it later
    du.save(model, path=du.DEMO_FOLDER / "populated_model.pickle")

    # display how model was changed
    du.display("Model content before populate:", before)
    du.display("Model content after populate:", after)


if __name__ == "__main__":
    demo_2_populate_model()

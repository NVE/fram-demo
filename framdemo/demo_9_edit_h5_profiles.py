"""Create and edit H5 files saved with time vectors in the FRAM data format."""

from datetime import timedelta

import numpy as np
import pandas as pd
from framdata.database_names import TimeVectorMetadataNames as TvMn
from framdata.file_editors import NVEH5TimeVectorEditor

save_path = r"./example.h5"

# Create h5 editor with dataframe and metadata.
h5_editor = NVEH5TimeVectorEditor()

frequency = timedelta(hours=1)

# Add content to metadata and table.
h5_editor.set_common_index(pd.date_range(start="29/08/2025", periods=7, freq=frequency).to_numpy())
h5_editor.set_vector("v1", np.array([0, 1, 2, 3, 0, -1, -2]))
h5_editor.set_common_metadata({TvMn.START: h5_editor.get_common_index()[0], TvMn.FREQUENCY: frequency, TvMn.NUM_POINTS: 7})

# Replace negative values with zero:
for vector_id in h5_editor.get_vector_ids():
    vector = h5_editor.get_vector(vector_id)
    vector[vector < 0] = 0
    h5_editor.set_vector(vector_id, vector)

# Save the table and metadata.
h5_editor.save_to_h5(save_path)


# To load an existing h5 file, supply a path to the editor.
h5_editor = NVEH5TimeVectorEditor(save_path)

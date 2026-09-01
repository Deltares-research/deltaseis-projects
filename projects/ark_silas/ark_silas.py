import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic, extract_wavelet_from_segy

load_dotenv()
folder = Path(os.environ["ARK_SILAS_FOLDER"])

output_suffix = "_heave_corrected_trace_averaging1_decon"
segy_files = sorted(f for f in folder.iterdir()
                    if f.suffix in ('.sgy', '.segy')
                    and "_trace_averaging1_decon" not in f.stem)

# picked by eye on one representative file
wavelet_source = folder / "Silas_center_line_0822121152SG132.sgy"
wavelet, wavelet_fs = extract_wavelet_from_segy(
    wavelet_source, 13241, 7.35, 7.6
)

for i, segy_file in enumerate(segy_files, start=1):

    print(f"{i}/{len(segy_files)}: processing {segy_file.stem}")
    edit = Segy_edit(segy_file)

    edit.get_seabed_pick(10, 100, 9, 3, truncate=10)
    edit.filter_horizon_savgol("seabed_pick", "seabed_pick_savgol", 101, 4)
    edit.calculate_difference_horizon(
        "seabed_pick_savgol", "seabed_pick", difference_horizon_name="heave"
    )
    edit.vertical_trace_corrections(edit.heave)

    dx_mean = edit.factor * edit.shot_point_interval.mean()
    fs = edit.sampling_rate
    data = np.array(edit.trace_data).T

    print("Start data processing")

    seis = Seismic(data, fs, dx_mean)
    # one wavelet for the whole survey, so amplitudes stay comparable between files
    seis.signature_deconvolution(wavelet, wavelet_fs=wavelet_fs, method='wiener',
                                 epsilon=0.01, prewhiten=False)
    seis.trace_averaging(1)
    seis.convert_to_trace_data(edit.data_sample_format)
    edit.trace_data = seis.data

    # write to SEG-Y
    processed_file = segy_file.with_stem(f"{segy_file.stem}{output_suffix}")
    edit.write(processed_file)

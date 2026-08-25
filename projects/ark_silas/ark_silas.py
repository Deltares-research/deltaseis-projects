import os
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic

load_dotenv()
folder = Path(os.environ["ARK_SILAS_FOLDER"])

segy_files = [Path(f) for f in folder.iterdir() if f.suffix in ('.sgy', '.segy')]

for i, segy_file in enumerate(segy_files):

    print(f"{i+1}/{len(segy_files)}: processing {segy_file.stem}")
    edit = Segy_edit(segy_file)
   
    #trace data processing
    dx_mean = edit.factor*edit.shot_point_interval.mean()
    fs = edit.sampling_rate
    data = np.array(edit.trace_data).T

    print("Start data processing")

    seis = Seismic(data, fs, dx_mean)
    seis.signature_deconvolution(
        trace_number=13241, start_time_ms=7.35, end_time_ms=7.6,
        method='wiener', epsilon=0.01, prewhiten=True, prewhiten_percent=1.0,
        auto_optimize=False,
    )

    #HIER GEBLEVEN: moet nog veel verbeterd worden, het pakt het window ook per file in plaats de signature van een bepaalde file die representatief is voor alle files. Ook moet de signature nog geoptimaliseerd worden, en moet er een check komen of de signature wel goed is.
    seis.trace_averaging(1)
    seis.convert_to_trace_data(edit.data_sample_format)
    edit.trace_data = seis.data

 

    # write to SEG-Y
    processed_file = segy_file.with_stem(f"{segy_file.stem}_trace_averaging1_decon")
    edit.write(processed_file)
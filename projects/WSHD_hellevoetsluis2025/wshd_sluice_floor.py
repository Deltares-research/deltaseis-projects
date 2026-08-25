import os
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic

load_dotenv()
folder = Path(os.environ["WSHD_SLUICE_FLOOR_FOLDER"])

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
    #seis.time_power_gain(2)
    print("Start gain")
   # seis.agc_gain()
    print("End gain")
    seis.trace_averaging(3)
    seis.convert_to_trace_data(edit.data_sample_format)
    edit.trace_data = seis.data
    edit.gain_type = 2 #t2 gain
    #edit.gain_type = 3 #AGC
 

    # write to SEG-Y
    processed_file = segy_file.with_stem(f"{segy_file.stem}_trace_averaging3")
    edit.write(processed_file)
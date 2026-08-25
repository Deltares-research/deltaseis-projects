import os
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic

load_dotenv()
folder = Path(os.environ["WSHD_SLUICE_WALLS_FOLDER"])

segy_files = [Path(f) for f in folder.iterdir() if f.suffix in ('.sgy', '.segy')]

#segy_files = [
 #   Path(r"D:\Projects\Pile foundations\data\SideViewLines\single-beam\seg-y_LF\raw\SideView04_20250115_151845_Q1_CH0_LF.sgy"),
  #  Path(r"D:\Projects\Pile foundations\data\SideViewLines\single-beam\seg-y_LF\raw\SideView04_20250115_152000_Q1_CH0_LF.sgy"),
   # Path(r"D:\Projects\Pile foundations\data\SideViewLines\single-beam\seg-y_LF\raw\SideView04_20250115_152548_Q1_CH0_LF.sgy"),
    #Path(r"D:\Projects\Pile foundations\data\SideViewLines\single-beam\seg-y_LF\raw\SideView04_20250115_152711_Q1_CH0_LF.sgy"),
#]

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
    print("Start AGC")
    seis.agc_gain()
    print("End AGC")
    seis.convert_to_trace_data(edit.data_sample_format)
    edit.trace_data = seis.data
    #edit.gain_type = 2 #t2 gain
    edit.gain_type = 3 #AGC
 
    print("Start QC plot and write to SEG-Y")

    # write to SEG-Y
    processed_file = segy_file.with_stem(f"{segy_file.stem}_AGC")
    edit.write(processed_file)
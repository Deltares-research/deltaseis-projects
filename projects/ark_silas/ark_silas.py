import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

from deltaseis import Segy_edit, Seismic

load_dotenv()
folder = Path(os.environ["ARK_SILAS_FOLDER"])

output_suffix = "_trace_averaging1_decon"
segy_files = sorted(f for f in folder.iterdir()
                    if f.suffix in ('.sgy', '.segy') and not f.stem.endswith(output_suffix))

wavelet_file = folder / "signature_wavelet.npy"
wavelet_meta_file = wavelet_file.with_suffix(".json")

# picked by eye on one representative file, delete the wavelet files to re-pick
wavelet_source = dict(file=segy_files[0].name, trace_number=13241,
                      start_time_ms=7.35, end_time_ms=7.6)


def load_seismic(segy_file):
    edit = Segy_edit(segy_file)
    data = np.array(edit.trace_data).T
    dx_mean = edit.factor * edit.shot_point_interval.mean()
    return edit, Seismic(data, edit.sampling_rate, dx_mean)


if not wavelet_file.exists():
    print(f"Extracting signature wavelet from {wavelet_source['file']}")
    _, reference = load_seismic(folder / wavelet_source["file"])
    np.save(wavelet_file, reference.extract_wavelet(wavelet_source["trace_number"],
                                                    wavelet_source["start_time_ms"],
                                                    wavelet_source["end_time_ms"]))
    wavelet_meta_file.write_text(json.dumps({**wavelet_source, "fs": float(reference.fs)}, indent=2))

wavelet = np.load(wavelet_file)
wavelet_fs = json.loads(wavelet_meta_file.read_text())["fs"]

for i, segy_file in enumerate(segy_files, start=1):

    print(f"{i}/{len(segy_files)}: processing {segy_file.stem}")
    edit, seis = load_seismic(segy_file)

    print("Start data processing")

    # one wavelet for the whole survey, so amplitudes stay comparable between files
    seis.signature_deconvolution(wavelet, wavelet_fs=wavelet_fs, method='wiener',
                                 epsilon=0.01, prewhiten=False)
    seis.trace_averaging(1)
    seis.convert_to_trace_data(edit.data_sample_format)
    edit.trace_data = seis.data

    # write to SEG-Y
    processed_file = segy_file.with_stem(f"{segy_file.stem}{output_suffix}")
    edit.write(processed_file)

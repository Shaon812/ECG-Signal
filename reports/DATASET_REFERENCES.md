# DATASET_REFERENCES

Generated: 2026-11-22
Sources: official PhysioNet dataset pages (fetched 2026-11-22) and the documentation
files bundled inside the downloaded archives. No publication details were invented.

Two **different** PhysioNet databases are used in this project. They must not be
confused with one another.

---

## 1. MIT-BIH Arrhythmia Database (MITDB) — ECG signal source

| Field | Verified value |
|---|---|
| Official name | MIT-BIH Arrhythmia Database |
| PhysioNet identifier | `mitdb` |
| Version used | **1.0.0** (local folder `mit-bih-arrhythmia-database-1.0.0`) |
| Published (PhysioNet) | Feb. 24, 2005 |
| Authors | George Moody, Roger Mark |
| DOI (v1.0.0) | `10.13026/C2F305` |
| URL | https://physionet.org/content/mitdb/1.0.0/ |
| RRID | SCR_007345 |
| License | Open Data Commons Attribution License v1.0 (ODC-BY 1.0) — "Open Access: anyone can access the files provided they conform to the license" |
| Local archive | `data/raw/mitdb/mitdb-1.0.0.zip` (77,030,320 bytes ≈ 73.5 MB) |
| Local evidence | `RECORDS` lists 48 records; `ANNOTATORS` lists `atr`; `SHA256SUMS.txt` present |

**Required dataset citation (from the official page):**

> Moody, G., & Mark, R. (2005). *MIT-BIH Arrhythmia Database* (version 1.0.0).
> PhysioNet. https://doi.org/10.13026/C2F305

**Original publication (also requested by the official page):**

> Moody GB, Mark RG. The impact of the MIT-BIH Arrhythmia Database.
> *IEEE Engineering in Medicine and Biology Magazine* 20(3):45–50 (2001).
> DOI 10.1109/51.932724; PMID 11446209.

**Use in this project:** source of all ECG beats, AAMI labels and the
patient-independent split. Records 201 and 202 are kept in the same patient group
(`patient_201_202`) as required by the database usage notes. Beat windows use the
`atr` reference annotations.

---

## 2. MIT-BIH Noise Stress Test Database (NSTDB) — noise source only

| Field | Verified value |
|---|---|
| Official name | MIT-BIH Noise Stress Test Database |
| PhysioNet identifier | `nstdb` |
| Version used | **1.0.0** (local folder `mit-bih-noise-stress-test-database-1.0.0`) |
| Published (PhysioNet) | Aug. 3, 1999 |
| Authors | George Moody, Roger Mark |
| DOI (v1.0.0) | `10.13026/C2HS3T` |
| URL | https://physionet.org/content/nstdb/1.0.0/ |
| License | Open Data Commons Attribution License v1.0 (ODC-BY 1.0) |
| Local archive | `data/raw/nstdb/mit-bih-noise-stress-test-database-1.0.0.zip` (70,945,297 bytes ≈ 67.7 MB) |
| Local evidence | `RECORDS` lists `bw`, `ma`, `em` plus 12 sample noisy records; `nstdb.txt` / `nstdb.doc` describe the second edition and `old/` the first edition |

**Required citation (from the official page):**

> Moody GB, Muldrow WE, Mark RG. A noise stress test for arrhythmia detectors.
> *Computers in Cardiology* 1984; 11:381–384.
> http://ecg.mit.edu/george/publications/nst-cinc-1984.pdf

The official page also requests the standard PhysioNet citation:

> Pollard, T., Moody, B. E., Lehman, L., Gow, B., Fernandes, C., Xie, C., Johnson, A.,
> Mark, R. G., & Heldt, T. (2026). PhysioNet as a global platform for biomedical
> research. *Nature Health*. https://doi.org/10.1038/s44360-026-00096-z

**Use in this project:** only the noise records **`bw`** (baseline wander) and
**`ma`** (muscle artifact), **channel 0**, are used for training/validation noise
augmentation. The `em` record and the pre-generated noisy ECG records (118e*/119e*)
are present locally and are documented by `noise_statistics.csv` /
`nstdb_audit.csv` but are **not** used by the B3 training loop. The `old/` directory
is the first edition and is not used.

---

## Distinction summary

| | MITDB | NSTDB |
|---|---|---|
| Role here | ECG beats + ground-truth labels | additive noise waveforms only |
| Content | 48 half-hour two-channel ECG recordings | 3 half-hour noise recordings + 12 sample noisy ECGs |
| Used records | all 48 records (after patient grouping) | `bw`, `ma` channel 0 |
| Version | 1.0.0 | 1.0.0 |
| DOI | 10.13026/C2F305 | 10.13026/C2HS3T |
| License | ODC-BY 1.0 | ODC-BY 1.0 |

## Note on versions

The local directory names and archive contents match PhysioNet version 1.0.0 for
both databases. No other dataset version was used or implied.

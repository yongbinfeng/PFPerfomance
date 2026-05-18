# PF vs MLPF Performance Comparison (Run-3 High Pileup)

Compares Particle Flow (PF) and ML-based Particle Flow (MLPF) reconstruction on Run-3 high-pileup data.

## Setup

Set up the CMSSW environment and apply the MLPF development branch:

```bash
export SCRAM_ARCH=el9_amd64_gcc13
cmsrel CMSSW_16_1_0_pre3
cd CMSSW_16_1_0_pre3/src
cmsenv
git cms-init
git cms-merge-topic -u yongbinfeng:jp_mlpf_20260302_dev_dump_tracking
scram b -j8
```

Then copy `reco_mlpf.py` into the working directory and run reconstruction as usual.

## Dataset

```
/JetMET0/Run2025G-v1/RAW
```

Run numbers: `397954`, `397962`, `398902`, `398903`

> **Note:** Some runs may be on tape. Submit a tape-recall request via the CMS data management tools (e.g., Rucio or the DBS transfer request interface) before attempting to access the files.

## Producing NanoAOD Output

After running reconstruction, the output NanoAOD ROOT files are expected to be named:

- `nano_pf.root` — standard PF reconstruction
- `nano_mlpf_2.root` — MLPF reconstruction

## Scripts

### `compare.py` — PF vs MLPF comparison

Compares AK4/AK8 jet kinematics, PF candidate distributions (inclusive and per particle type), and 2D eta×phi profiles using PyROOT + RDataFrame. Saves one PDF per variable to `plots/`.

Plot categories produced:
- AK4 jet kinematics (pT, eta, phi, mass, multiplicity)
- AK8 jet kinematics (pT, eta, phi, soft-drop mass, multiplicity)
- PF candidates: inclusive (pT, eta, phi, mass, PUPPI weight, dz, dxy, fromPV, particleId)
- PF candidates: per particle type (charged hadron, neutral hadron, photon, HF EM, HF hadron)
- PF candidates: pT × PUPPI weight per particle type
- 2D profiles: mean pT and mean pT×PUPPI weight vs eta×phi per particle type
- Global event variables (e.g. PV_npvsGood)

**Run with defaults** (`nano_pf.root` vs `nano_mlpf_2.root`):
```bash
python compare.py
```

**Run with custom files and labels:**
```bash
python compare.py file1.root file2.root --tree Events --labels "PF,MLPF" --outdir plots/
```

### `make_plots.py` — Pileup / primary-vertex plots

Produces pileup and PV diagnostic plots from NanoAOD files using CMS TDR style (`cmsplots/`). Supports both data and MC modes.

Plots produced:
- 1D distributions: `PV_npvsGood`, `PV_npvs`, `PV_z`, `PV_ndof`, jet multiplicities
- MC-only: truth pileup (`Pileup_nPU`, `Pileup_nTrueInt`), `GenVtx_z`, Δz(PV − GenVtx)
- 2D correlations: reco vs truth vertex counts, PV_z vs pileup, ndof vs pileup, etc.
- Overlay canvas: normalized PV_npvsGood / npvs (/ nPU / nTrueInt for MC)
- Overview grid and `histograms.root` saved to `plots/Data/` or `plots/MC/`

**Run on data:**
```bash
python make_plots.py --data
```

**Run on MC (default):**
```bash
python make_plots.py
```

File patterns are hardcoded at the top of the script (`DATA_FILE_PATTERN`, `MC_FILE_PATTERN`) — edit them to point to your NanoAOD files.

> **Dependency:** requires the `cmsplots/` submodule (provides `tdrstyle` and `cms_lumi`).

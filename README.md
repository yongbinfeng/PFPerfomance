# PF vs MLPF Performance Comparison (Run-3 High Pileup)

Compares Particle Flow (PF) and ML-based Particle Flow (MLPF) reconstruction on Run-3 high-pileup data.

## Setup

Set up the CMSSW environment and apply the MLPF development branch:

```bash
cmsrel CMSSW_16_1_0_pre3
cd CMSSW_16_1_0_pre3/src
cmsenv
git cms-init
git cms-merge-topic -u yongbinfeng:jp_mlpf_20260302_dev
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
- `nano_mlpf.root` — MLPF reconstruction

## Comparison Script

`compare.py` compares AK4/AK8 jet kinematics and PF candidate distributions using PyROOT + RDataFrame, saving one PDF per variable to `plots/`.

**Run with defaults** (uses `nano_pf.root` and `nano_mlpf.root`):
```bash
python compare.py
```

**Run with custom files and labels:**
```bash
python compare.py file1.root file2.root --tree Events --labels "PF,MLPF"
```

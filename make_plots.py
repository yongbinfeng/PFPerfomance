#!/usr/bin/env python3
"""
make_plots.py

Plot pileup / primary-vertex variables from NanoAOD files using PyROOT RDataFrame.
Uses CMS TDR style (tdrstyle) and CMS lumi label (cms_lumi).

Outputs saved to plots/.
"""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmsplots"))

import ROOT
ROOT.gROOT.SetBatch(True)

import cms_lumi
import tdrstyle

# ── configuration ──────────────────────────────────────────────────────────────

_parser = argparse.ArgumentParser(description="Make pileup / PV plots from NanoAOD.")
_parser.add_argument("--data", action="store_true", help="Run on data (drops truth-level plots)")
_args = _parser.parse_args()

IS_DATA = _args.data

MC_FILE_PATTERN   = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/moanwar/mlpf/mc_run3/st_pf/nano_pf_9*.root"
DATA_FILE_PATTERN = "/eos/cms/store/group/phys_pf/vslokenb/JetMET0_Run2025G/job_*root"

FILE_PATTERN = DATA_FILE_PATTERN if IS_DATA else MC_FILE_PATTERN
TREE_NAME    = "Events"
OUTPUT_DIR   = "plots/Data" if IS_DATA else "plots/MC"

cms_lumi.lumi_sqrtS     = "(13.6 TeV)"
cms_lumi.extraText      = "Preliminary" if IS_DATA else "Simulation Preliminary"
cms_lumi.writeExtraText = True

# ── per-variable definitions ───────────────────────────────────────────────────
# key -> (branch, axis title, nbins, xmin, xmax, c++ cast)
VARS = {
    "npvsGood" : ("PV_npvsGood",     "N_{Good PV}",                        250,  0,   250, "int"),
    "npvs"     : ("PV_npvs",         "N_{Total PV}",                       250,  0,   250, "int"),
    "nPU"      : ("Pileup_nPU",      "Truth n_{PU}",                      200,  0,   200, "int"),
    "nTrueInt" : ("Pileup_nTrueInt", "Truth n_{TrueInt}",                 200,  0,   200, "float"),
    "pvz"      : ("PV_z",            "PV z [cm]",                         120, -30,   30, "float"),
    "ndof"     : ("PV_ndof",         "PV d.o.f.",                          80,  0,   300, "float"),
    "genvtxz"  : ("GenVtx_z",        "Truth PV z [cm]",                   120, -30,   30, "float"),
    "dz"       : ("dz",              "PV_{z} #minus GenVtx_{z} [cm]",     200, -20,   20, "float"),
    "nJet"     : ("nJet",            "N_{jets} (AK4)",                     15,  0,    15, "int"),
    "nFatJet"  : ("nFatJet",         "N_{jets} (AK8)",                     5,  0,    5, "int"),
}

# Variables that require MC truth branches — excluded in data mode
TRUTH_VARS = {"nPU", "nTrueInt", "genvtxz", "dz"}

COLORS = {
    "npvsGood" : (ROOT.kAzure   + 1, ROOT.kAzure   - 9),
    "npvs"     : (ROOT.kViolet  + 1, ROOT.kViolet  - 9),
    "nPU"      : (ROOT.kRed     + 1, ROOT.kRed     - 9),
    "nTrueInt" : (ROOT.kGreen   + 2, ROOT.kGreen   - 9),
    "pvz"      : (ROOT.kOrange  + 7, ROOT.kOrange  - 9),
    "ndof"     : (ROOT.kCyan    + 1, ROOT.kCyan    - 9),
    "genvtxz"  : (ROOT.kMagenta + 1, ROOT.kMagenta - 9),
    "dz"       : (ROOT.kTeal    + 2, ROOT.kTeal    - 9),
    "nJet"     : (ROOT.kBlue    + 2, ROOT.kBlue    - 9),
    "nFatJet"  : (ROOT.kSpring  + 4, ROOT.kSpring  - 9),
}

# ── helpers ────────────────────────────────────────────────────────────────────

def setup_style():
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.09)
    ROOT.gStyle.SetPadBottomMargin(0.14)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetTitleSize(0.05, "XYZ")
    ROOT.gStyle.SetTitleYOffset(1.4)
    ROOT.gStyle.SetTitleXOffset(1.2)
    ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)
    ROOT.TGaxis.SetMaxDigits(4)
    ROOT.gStyle.SetPalette(ROOT.kViridis)


def save(canvas, name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    canvas.Print(f"{OUTPUT_DIR}/{name}.png")
    canvas.Print(f"{OUTPUT_DIR}/{name}.pdf")
    print(f"  -> {OUTPUT_DIR}/{name}.{{png,pdf}}")


def draw2d(h, cname, fname, cw=900, ch=700):
    c = ROOT.TCanvas(cname, "", cw, ch)
    c.SetRightMargin(0.12)
    h.Draw("COLZ")
    c.Update()           # materialise COLZ palette so ProfileX works
    # Profile (mean y per x bin) drawn on top
    th2 = h.GetValue()
    prof = th2.ProfileX(f"{th2.GetName()}_pfx")
    prof.SetLineColor(ROOT.kRed)
    prof.SetLineWidth(2)
    prof.SetMarkerColor(ROOT.kRed)
    prof.SetMarkerStyle(20)
    prof.SetMarkerSize(0.5)
    prof.Draw("SAME E")
    cms_lumi.CMS_lumi(c, 0, 0)   # after histogram; no pad.Update() inside anymore
    save(c, fname)
    return c


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    setup_style()
    ROOT.EnableImplicitMT()

    # Active variables: drop truth-level branches when running on data
    active_vars = {k: v for k, v in VARS.items()
                   if not (IS_DATA and k in TRUTH_VARS)}

    # 1. Collect files
    files = sorted(glob.glob(FILE_PATTERN))
    if not files:
        sys.exit(f"[ERROR] No files found matching:\n  {FILE_PATTERN}")
    print(f"[INFO] Found {len(files)} file(s):")
    for f in files:
        print(f"       {f}")

    # 2. Build RDataFrame
    rdf = ROOT.RDataFrame(TREE_NAME, ROOT.std.vector("string")(files))

    # 3. Derived columns (must precede the clamping loop)
    if not IS_DATA:
        rdf = rdf.Define("dz", "(double)PV_z - (double)GenVtx_z")

    # Clamped columns — upper bound is xmax - bin_width/2 so clamped values
    # land in the last visible bin (ROOT bins are half-open [xmin, xmax)).
    for key, (branch, _, nbins, xmin, xmax, cast) in active_vars.items():
        clamp_hi = xmax - (xmax - xmin) / (2.0 * nbins)
        rdf = rdf.Define(
            f"{key}_clamped",
            f"std::clamp((double){branch}, (double){xmin}, (double){clamp_hi})"
        )

    # 4. 1-D histograms
    h1 = {}
    for key, (branch, title, nbins, xmin, xmax, _) in active_vars.items():
        h1[key] = rdf.Histo1D(
            (f"h_{key}", f";{title};Events", nbins, xmin, xmax),
            f"{key}_clamped",
        )

    # 5. 2-D histograms
    # Convention: x = truth, y = reco (where applicable)
    def make2d(xkey, ykey):
        _, xtitle, xnbins, xxmin, xxmax, _ = VARS[xkey]
        _, ytitle, ynbins, yymin, yymax, _ = VARS[ykey]
        return rdf.Histo2D(
            (f"h2_{ykey}_vs_{xkey}", f";{xtitle};{ytitle}",
             xnbins, xxmin, xxmax, ynbins, yymin, yymax),
            f"{xkey}_clamped",
            f"{ykey}_clamped",
        )

    h2 = {}
    if not IS_DATA:
        # truth × reco vertex counts
        h2["npvsGood_vs_nTrueInt"] = make2d("nTrueInt", "npvsGood")
        h2["npvs_vs_nTrueInt"]     = make2d("nTrueInt", "npvs")
        h2["npvsGood_vs_nPU"]      = make2d("nPU",      "npvsGood")
        h2["npvs_vs_nPU"]          = make2d("nPU",      "npvs")
        # vertex-count on x, PV_z on y (truth x)
        h2["pvz_vs_nTrueInt"]      = make2d("nTrueInt", "pvz")
        h2["pvz_vs_nPU"]           = make2d("nPU",      "pvz")
        # vertex-count on x, PV_ndof on y (truth x)
        h2["ndof_vs_nTrueInt"]     = make2d("nTrueInt", "ndof")
        h2["ndof_vs_nPU"]          = make2d("nPU",      "ndof")
        # truth z vs reco z
        h2["pvz_vs_genvtxz"]       = make2d("genvtxz",  "pvz")
        # delta-z vs nPU
        h2["dz_vs_nPU"]            = make2d("nPU",      "dz")
        # nJet / nFatJet vs truth pileup (MC only)
        h2["nJet_vs_nTrueInt"]     = make2d("nTrueInt", "nJet")
        h2["nJet_vs_nPU"]          = make2d("nPU",      "nJet")
        h2["nFatJet_vs_nTrueInt"]  = make2d("nTrueInt", "nFatJet")
        h2["nFatJet_vs_nPU"]       = make2d("nPU",      "nFatJet")

    # always-present 2D plots (reco-only axes)
    h2["npvsGood_vs_npvs"]     = make2d("npvs",     "npvsGood")
    h2["pvz_vs_npvsGood"]      = make2d("npvsGood", "pvz")
    h2["pvz_vs_npvs"]          = make2d("npvs",     "pvz")
    h2["ndof_vs_npvsGood"]     = make2d("npvsGood", "ndof")
    h2["ndof_vs_npvs"]         = make2d("npvs",     "ndof")
    h2["pvz_vs_ndof"]          = make2d("ndof",     "pvz")
    # nJet / nFatJet vs reco PV counts (always)
    h2["nJet_vs_npvsGood"]     = make2d("npvsGood", "nJet")
    h2["nJet_vs_npvs"]         = make2d("npvs",     "nJet")
    h2["nFatJet_vs_npvsGood"]  = make2d("npvsGood", "nFatJet")
    h2["nFatJet_vs_npvs"]      = make2d("npvs",     "nFatJet")

    # 6. Draw individual 1-D plots
    print("\n[INFO] Running event loop and writing plots ...")
    CW, CH = 800, 700
    canvases = []

    for key, hptr in h1.items():
        branch_name = active_vars[key][0]
        lc, _ = COLORS[key]
        c = ROOT.TCanvas(f"c_{key}", "", CW, CH)
        hptr.SetLineColor(lc)
        hptr.Draw("HIST")
        cms_lumi.CMS_lumi(c, 0, 0)
        save(c, branch_name)
        canvases.append(c)

    # 7. Combined overlay: PV_npvs* (+ Pileup* for MC), normalized to unit area
    OVERLAY_KEYS = ["npvsGood", "npvs"] if IS_DATA else ["npvsGood", "npvs", "nPU", "nTrueInt"]
    LINE_STYLES  = {"npvsGood": 1, "npvs": 2, "nPU": 1, "nTrueInt": 2}

    c_ov = ROOT.TCanvas("c_pv_pileup_overlay", "", CW, CH)
    leg = ROOT.TLegend(0.55, 0.65, 0.88, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.038)

    h_norms = []
    for key in OVERLAY_KEYS:
        lc, _ = COLORS[key]
        h = h1[key].GetValue().Clone(f"h_{key}_norm")
        integral = h.Integral()
        if integral > 0:
            h.Scale(1.0 / integral)
        h.SetLineColor(lc)
        h.SetLineStyle(LINE_STYLES[key])
        h.SetLineWidth(2)
        h_norms.append(h)

    y_max = max(h.GetMaximum() for h in h_norms)
    for i, (key, h) in enumerate(zip(OVERLAY_KEYS, h_norms)):
        if i == 0:
            h.GetXaxis().SetTitle("nPV")
            h.GetYaxis().SetTitle("Events (normalized)")
            h.GetXaxis().SetRangeUser(0, 250)
            h.GetYaxis().SetRangeUser(0, y_max * 1.3)
            h.Draw("HIST")
        else:
            h.Draw("HIST SAME")
        leg.AddEntry(h, VARS[key][0], "l")

    leg.Draw()
    cms_lumi.CMS_lumi(c_ov, 0, 0)
    save(c_ov, "PV_npvs_and_Pileup_overlay")
    canvases.append(c_ov)
    canvases.extend(h_norms)

    # 8. Draw 2-D plots
    all_plot_names = {
        "npvsGood_vs_nTrueInt" : "PV_npvsGood_vs_Pileup_nTrueInt",
        "npvs_vs_nTrueInt"     : "PV_npvs_vs_Pileup_nTrueInt",
        "npvsGood_vs_nPU"      : "PV_npvsGood_vs_Pileup_nPU",
        "npvs_vs_nPU"          : "PV_npvs_vs_Pileup_nPU",
        "npvsGood_vs_npvs"     : "PV_npvsGood_vs_PV_npvs",
        "pvz_vs_nTrueInt"      : "PV_z_vs_Pileup_nTrueInt",
        "pvz_vs_nPU"           : "PV_z_vs_Pileup_nPU",
        "pvz_vs_npvsGood"      : "PV_z_vs_PV_npvsGood",
        "pvz_vs_npvs"          : "PV_z_vs_PV_npvs",
        "ndof_vs_nTrueInt"     : "PV_ndof_vs_Pileup_nTrueInt",
        "ndof_vs_nPU"          : "PV_ndof_vs_Pileup_nPU",
        "ndof_vs_npvsGood"     : "PV_ndof_vs_PV_npvsGood",
        "ndof_vs_npvs"         : "PV_ndof_vs_PV_npvs",
        "pvz_vs_ndof"          : "PV_z_vs_PV_ndof",
        "pvz_vs_genvtxz"       : "PV_z_vs_GenVtx_z",
        "dz_vs_nPU"            : "PV_z_minus_GenVtx_z_vs_Pileup_nPU",
        "nJet_vs_nTrueInt"     : "nJet_vs_Pileup_nTrueInt",
        "nJet_vs_nPU"          : "nJet_vs_Pileup_nPU",
        "nFatJet_vs_nTrueInt"  : "nFatJet_vs_Pileup_nTrueInt",
        "nFatJet_vs_nPU"       : "nFatJet_vs_Pileup_nPU",
        "nJet_vs_npvsGood"     : "nJet_vs_PV_npvsGood",
        "nJet_vs_npvs"         : "nJet_vs_PV_npvs",
        "nFatJet_vs_npvsGood"  : "nFatJet_vs_PV_npvsGood",
        "nFatJet_vs_npvs"      : "nFatJet_vs_PV_npvs",
    }
    plot_names = {k: v for k, v in all_plot_names.items() if k in h2}
    for key, fname in plot_names.items():
        canvases.append(draw2d(h2[key], f"c_{key}", fname))

    # 9. Overview grid — size adapts to number of active 1D variables
    n_vars = len(h1)
    n_cols = 4
    n_rows = (n_vars + n_cols - 1) // n_cols
    c_grid = ROOT.TCanvas("c_overview", "", n_cols * 800, n_rows * CH)
    c_grid.Divide(n_cols, n_rows)
    for idx, (key, hptr) in enumerate(h1.items(), start=1):
        pad = c_grid.cd(idx)
        lc, _ = COLORS[key]
        hptr.SetLineColor(lc)
        hptr.Draw("HIST")
        cms_lumi.CMS_lumi(pad, 0, 0)
    save(c_grid, "pileup_overview")
    canvases.append(c_grid)

    # 10. Save all histograms to a ROOT file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    root_path = f"{OUTPUT_DIR}/histograms.root"
    tf = ROOT.TFile(root_path, "RECREATE")
    for key, hptr in h1.items():
        h = hptr.GetValue()
        h.SetName(active_vars[key][0])
        h.Write()
    for key, hptr in h2.items():
        h = hptr.GetValue()
        h.SetName(plot_names.get(key, key))
        h.Write()
    tf.Close()
    print(f"  -> {root_path}")

    print("\n[INFO] Done.")


if __name__ == "__main__":
    main()

"""
compare_jets.py
Compare AK4 and AK8 jet kinematics across multiple ROOT files using
PyROOT + RDataFrame.  One canvas (main + ratio pad) per variable.
All PDFs are saved to the plots/ directory.

Usage:
    python compare_jets.py                                       # uses DEFAULT_FILES
    python compare_jets.py file1.root file2.root [file3.root ...]
    python compare_jets.py file1.root file2.root --tree Events --labels "Signal,Background"
"""

# ── default files (edit this list as needed) ─────────────────
import ROOT
import sys
import os
import argparse

DEFAULT_FILES = [
    "nano_pf.root",
    "nano_mlpf_2.root",
]
DEFAULT_LABELS = [
    "PF",
    "MLPF",
]


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetFrameLineWidth(1)
ROOT.EnableImplicitMT()

# ── colour cycle (one per file) ───────────────────────────────
COLORS = [
    ROOT.kAzure + 1,   # blue
    ROOT.kOrange + 7,   # orange
    ROOT.kGreen + 2,   # green
    ROOT.kMagenta + 1,   # magenta
    ROOT.kRed + 1,   # red
    ROOT.kCyan + 1,   # cyan
    ROOT.kYellow + 2,   # yellow
    ROOT.kViolet + 5,   # violet
]
FILLS = [3004, 3005, 3006, 3007, 3013, 3017, 3020, 3022]


# ── histogram specifications ──────────────────────────────────
# (column_expr, filter_expr, nbins, xlo, xhi, xtitle, short_name)
AK4_HISTS = [
    ("nJet",      "",           20,  -0.5,
     19.5, "n_{AK4 jets}",            "nJet"),
    ("Jet_pt",    "nJet > 0",   60,   0,   900,
     "AK4 p_{T} [GeV]",         "Jet_pt"),
    ("Jet_pt[0]", "nJet > 0",   60,   0,   900,
     "Leading AK4 p_{T} [GeV]", "Jet_pt_lead"),
    ("Jet_eta",   "nJet > 0",   50,  -5,     5,
     "AK4 #eta",                "Jet_eta"),
    ("Jet_phi",   "nJet > 0",   36,  -3.2,
     3.2, "AK4 #phi [rad]",          "Jet_phi"),
    ("Jet_mass",  "nJet > 0",   50,   0,    80,
     "AK4 jet mass [GeV]",      "Jet_mass"),
]

AK8_HISTS = [
    ("nFatJet",      "",              10,  -0.5,
     9.5,  "n_{AK8 jets}",            "nFatJet"),
    ("FatJet_pt",    "nFatJet > 0",   60,   0,
     1400,   "AK8 p_{T} [GeV]",         "FatJet_pt"),
    ("FatJet_pt[0]", "nFatJet > 0",   60,   0,  1400,
     "Leading AK8 p_{T} [GeV]", "FatJet_pt_lead"),
    ("FatJet_eta",   "nFatJet > 0",   50,  -5,
     5,   "AK8 #eta",                "FatJet_eta"),
    ("FatJet_phi",   "nFatJet > 0",   36,  -3.2,
     3.2, "AK8 #phi [rad]",          "FatJet_phi"),
    # mass column appended at runtime
]


PFCANDS_HISTS = [
    ("nPFCands",                 "",                 100,
     0, 10000,  "n_{PF candidates}",          "nPFCands"),
    ("PFCands_pt",               "nPFCands > 0",      60,
     0,   10,   "PF candidate p_{T} [GeV]",   "PFCands_pt"),
    ("PFCands_pt[0]",            "nPFCands > 0",      60,   0,
     200,   "Leading PF cand p_{T} [GeV]", "PFCands_pt_lead"),
    ("PFCands_eta",              "nPFCands > 0",      50,  -
     5,    5,   "PF candidate #eta",           "PFCands_eta"),
    ("PFCands_phi",              "nPFCands > 0",      36, -
     3.2,  3.2,  "PF candidate #phi [rad]",     "PFCands_phi"),
    ("PFCands_mass",             "nPFCands > 0",      50,   0,
     2,   "PF candidate mass [GeV]",     "PFCands_mass"),
    ("PFCands_puppiWeight",      "nPFCands > 0",      50,   0,
     1,   "PF cand PUPPI weight",        "PFCands_puppiWeight"),
    ("PFCands_puppiWeightNoLep", "nPFCands > 0",      50,   0,    1,
     "PF cand PUPPI weight (no lep)", "PFCands_puppiWeightNoLep"),
    ("PFCands_dz",               "nPFCands > 0",
     60, -0.5, 0.5, "PF cand d_{z} [cm]",  "PFCands_dz"),
    ("PFCands_dxy",              "nPFCands > 0",      60, -
     0.3, 0.3, "PF cand d_{xy} [cm]", "PFCands_dxy"),
    ("PFCands_fromPV",           "nPFCands > 0",       5,  -
     0.5,  4.5, "PF cand fromPV()",            "PFCands_fromPV"),
    ("PFCands_particleId",       "nPFCands > 0",       8,   0.5,
     8.5, "PF cand particle type",       "PFCands_particleId"),
]


# PF candidate particle types identified by pdgId
# +/-211 = charged pion (ch. hadron), 130 = K0L (neutral hadron),
#   22   = photon, 1 = HF EM deposit, 2 = HF hadronic deposit
PF_PARTICLE_TYPES = {
    "chHad":  ("abs(PFCands_pdgId) == 211", "Charged hadron (#pi^{#pm})"),
    "nHad":   ("PFCands_pdgId == 130",      "Neutral hadron (K^{0}_{L})"),
    "photon": ("PFCands_pdgId == 22",       "Photon"),
    "hfEM":   ("PFCands_pdgId == 1",        "HF EM"),
    "hfHad":  ("PFCands_pdgId == 2",        "HF hadron"),
}

# Kinematic variables plotted separately for each particle type
PFCANDS_PERTYPE_HISTS = [
    ("PFCands_pt",  60,  0,   20,  "p_{T} [GeV]"),
    ("PFCands_eta", 50, -5,    5,  "#eta"),
    ("PFCands_phi", 36, -3.2,  3.2, "#phi [rad]"),
]

# Global event-level variables
# (column, filter, nbins, xlo, xhi, xtitle, sname)
GLOBAL_HISTS = [
    ("PV_npvsGood", "", 50, 50, 150, "Good primary vertices", "PV_npvsGood"),
]

# 2D profile binning: eta × phi
PROFILE2D_ETA_BINS = 50
PROFILE2D_ETA_RANGE = (-5.0, 5.0)
PROFILE2D_PHI_BINS = 36
PROFILE2D_PHI_RANGE = (-3.2, 3.2)

# ─────────────────────────────────────────────────────────────


def detect_tree(fname):
    for name in ("Events", "events", "tree", "T", "ntuple"):
        f = ROOT.TFile.Open(fname)
        if not f or f.IsZombie():
            sys.exit(f"ERROR: cannot open {fname}")
        obj = f.Get(name)
        if obj and obj.InheritsFrom("TTree"):
            f.Close()
            return name
    f = ROOT.TFile.Open(fname)
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.InheritsFrom("TTree"):
            name = obj.GetName()
            f.Close()
            return name
    sys.exit(f"ERROR: no TTree found in {fname}")


def has_column(rdf, col):
    return col in [str(c) for c in rdf.GetColumnNames()]


def book_histograms(rdf, specs, tag):
    """Book all histograms lazily. Returns list of (RResultPtr, xtitle, sname)."""
    results = []
    for i, (col_expr, filt, nb, xlo, xhi, xtitle, sname) in enumerate(specs):
        hname = f"h_{tag}_{i}"
        is_idx = "[" in col_expr and col_expr.endswith("]")
        base_col = col_expr.split("[")[0]

        node = rdf.Filter(filt) if filt else rdf

        if is_idx:
            idx = int(col_expr[col_expr.index("[")+1: col_expr.index("]")])
            tname = f"_tmp_{tag}_{i}"
            node = node.Define(
                tname,
                f"({base_col}).size() > {idx} ? float({base_col}[{idx}]) : -999.f",
            )
            h = node.Histo1D((hname, "", nb, xlo, xhi), tname)
        else:
            h = node.Histo1D((hname, "", nb, xlo, xhi), base_col)

        results.append((h, xtitle, sname))
    return results


def style_hist(h, col, fill):
    h.SetLineColor(col)
    h.SetLineWidth(2)
    h.SetFillColor(col)
    h.SetFillStyle(fill)
    h.SetStats(0)
    h.GetXaxis().SetTitleSize(0.050)
    h.GetYaxis().SetTitleSize(0.050)
    h.GetXaxis().SetLabelSize(0.042)
    h.GetYaxis().SetLabelSize(0.042)


# ─────────────────────────────────────────────────────────────
def make_canvas(hists, xtitle, sname, labels, outdir, logy=False, ratio_ytitle="MLPF / PF"):
    """
    One canvas per variable.
    Top 70 %  → main histogram comparison (raw event counts).
    Bottom 30% → ratio of each file to the first (reference) file.
    logy=True  → log scale on the main pad y-axis.
    """
    c = ROOT.TCanvas(f"c_{sname}", sname, 800, 800)

    split = 0.30
    pMain = ROOT.TPad("pMain",  "", 0, split, 1, 1)
    pRatio = ROOT.TPad("pRatio", "", 0, 0,     1, split)

    pMain.SetTopMargin(0.10)
    pMain.SetBottomMargin(0.02)
    pMain.SetLeftMargin(0.13)
    pMain.SetRightMargin(0.04)
    pRatio.SetTopMargin(0.03)
    pRatio.SetBottomMargin(0.33)
    pRatio.SetLeftMargin(0.13)
    pRatio.SetRightMargin(0.04)
    pRatio.SetGridy()
    pMain.Draw()
    pRatio.Draw()

    # ── main pad ─────────────────────────────────────────────
    pMain.cd()
    if logy:
        pMain.SetLogy()
        ymax = max(h.GetMaximum() for h in hists) * 50
        ymin = 0.5
    else:
        ymax = max(h.GetMaximum() for h in hists) * 1.45
        ymin = 0

    for idx, h in enumerate(hists):
        col = COLORS[idx % len(COLORS)]
        fill = FILLS[idx % len(FILLS)]
        style_hist(h, col, fill)
        h.SetMaximum(ymax)
        h.SetMinimum(ymin)
        if idx == 0:
            h.GetYaxis().SetTitle("Events")
            # hide x-axis title and labels on upper pad to avoid overlap
            h.GetXaxis().SetTitle("")
            h.GetXaxis().SetLabelSize(0)
            h.GetXaxis().SetTitleSize(0)
            h.Draw("HIST")
        else:
            h.Draw("HIST SAME")

    leg = ROOT.TLegend(0.55, 0.65, 0.94, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.042)
    for h, lbl in zip(hists, labels):
        leg.AddEntry(h, lbl, "f")
    leg.Draw()

    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.055)
    tex.SetTextFont(62)
    tex.DrawLatex(0.15, 0.88, xtitle)

    # ── ratio pad ────────────────────────────────────────────
    pRatio.cd()
    ref = hists[0]
    ratios = []
    for idx, h in enumerate(hists[1:], start=1):
        col = COLORS[idx % len(COLORS)]
        ratio = h.Clone(f"_ratio_{sname}_{idx}")
        ratio.SetDirectory(0)
        ratio.Divide(ref)
        ratio.SetTitle("")
        ratio.SetFillStyle(0)
        ratio.SetLineColor(col)
        ratio.SetMarkerColor(col)
        ratio.SetLineWidth(2)
        ratio.GetYaxis().SetTitle(ratio_ytitle)
        ratio.GetYaxis().SetNdivisions(504)
        ratio.GetYaxis().SetTitleSize(0.11)
        ratio.GetYaxis().SetLabelSize(0.10)
        ratio.GetYaxis().SetTitleOffset(0.55)
        ratio.GetYaxis().CenterTitle(True)
        ratio.GetXaxis().SetTitle(xtitle)
        ratio.GetXaxis().SetTitleSize(0.12)
        ratio.GetXaxis().SetLabelSize(0.10)
        ratio.GetXaxis().SetTitleOffset(0.95)
        ratio.GetYaxis().SetRangeUser(0.0, 2.4)
        ratio.Draw("EP" if idx == 1 else "EP SAME")
        ratios.append(ratio)

    xmin = ref.GetXaxis().GetXmin()
    xmax = ref.GetXaxis().GetXmax()
    line = ROOT.TLine(xmin, 1.0, xmax, 1.0)
    line.SetLineColor(ROOT.kRed)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw()

    c.Update()
    outpath = os.path.join(outdir, f"{sname}.pdf")
    c.SaveAs(outpath)
    print(f"  Saved  {outpath}")

    # prevent premature GC
    c._keep = [pMain, pRatio, leg, tex, line, ratios]
    return c


# ─────────────────────────────────────────────────────────────
def draw_profile2d(prof, title, outpath, zrange=None):
    """Draw a single TProfile2D as a COLZ canvas and save."""
    c = ROOT.TCanvas(f"c2d_{prof.GetName()}", title, 900, 700)
    c.SetLeftMargin(0.10)
    c.SetRightMargin(0.15)
    c.SetTopMargin(0.08)
    c.SetBottomMargin(0.10)
    prof.SetTitle(title)
    prof.GetXaxis().SetTitle("#eta")
    prof.GetYaxis().SetTitle("#phi")
    prof.GetXaxis().SetTitleSize(0.045)
    prof.GetYaxis().SetTitleSize(0.045)
    prof.GetZaxis().SetTitleSize(0.040)
    if zrange:
        prof.SetMinimum(zrange[0])
        prof.SetMaximum(zrange[1])
    prof.Draw("COLZ")
    c.Update()
    c.SaveAs(outpath)
    print(f"  Saved  {outpath}")
    return c


def make_profile2d_ratio(prof1, prof2, name, title, outpath):
    """Divide prof1 / prof2 bin-by-bin (using TH2 divide) and save."""
    h1 = prof1.ProjectionXY(f"_hxy1_{name}", "C=E")
    h2 = prof2.ProjectionXY(f"_hxy2_{name}", "C=E")
    h1.SetDirectory(0)
    h2.SetDirectory(0)
    h1.Divide(h2)

    c = ROOT.TCanvas(f"cr2d_{name}", title, 900, 700)
    c.SetLeftMargin(0.10)
    c.SetRightMargin(0.15)
    c.SetTopMargin(0.08)
    c.SetBottomMargin(0.10)
    h1.SetTitle(title)
    h1.GetXaxis().SetTitle("#eta")
    h1.GetYaxis().SetTitle("#phi")
    h1.GetXaxis().SetTitleSize(0.045)
    h1.GetYaxis().SetTitleSize(0.045)
    h1.GetZaxis().SetTitleSize(0.040)
    h1.SetMinimum(0.5)
    h1.SetMaximum(1.5)
    h1.Draw("COLZ")
    c.Update()
    c.SaveAs(outpath)
    print(f"  Saved  {outpath}")
    c._keep = [h1, h2]
    return c


# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Compare jet kinematics across multiple NanoAOD ROOT files.")
    parser.add_argument(
        "files", nargs="*",
        default=DEFAULT_FILES,
        help="ROOT files to compare (at least 2); defaults to DEFAULT_FILES in the script",
    )
    parser.add_argument("--tree",   default=None,
                        help="TTree name (auto-detected if omitted)")
    parser.add_argument("--labels", default=None,
                        help="Comma-separated legend labels, one per file")
    parser.add_argument("--outdir", default="plots",
                        help="Output directory for PDFs (default: plots/)")
    args = parser.parse_args()

    # use DEFAULT_FILES / DEFAULT_LABELS if nothing passed on the command line
    input_files = args.files if args.files else DEFAULT_FILES

    if len(input_files) < 2:
        sys.exit("ERROR: provide at least 2 ROOT files.")
    if len(input_files) > len(COLORS):
        sys.exit(
            f"ERROR: maximum {len(COLORS)} files supported (add more colours to extend).")

    os.makedirs(args.outdir, exist_ok=True)

    # labels: --labels flag > DEFAULT_LABELS (when using defaults) > basename fallback
    if args.labels:
        labels = [l.strip() for l in args.labels.split(",")]
        if len(labels) != len(input_files):
            sys.exit("ERROR: number of --labels must match number of files.")
    elif input_files == DEFAULT_FILES and DEFAULT_LABELS:
        if len(DEFAULT_LABELS) != len(DEFAULT_FILES):
            sys.exit(
                "ERROR: DEFAULT_LABELS and DEFAULT_FILES must have the same length.")
        labels = list(DEFAULT_LABELS)
    else:
        labels = [os.path.basename(f).replace(".root", "")
                  for f in input_files]

    # open one RDataFrame per file
    print("\nOpening files:")
    rdfs = []
    for fname in input_files:
        tree = args.tree or detect_tree(fname)
        rdf = ROOT.RDataFrame(tree, fname)
        print(f"  {fname}  tree={tree}  entries={rdf.Count().GetValue()}")
        rdfs.append(rdf)

    ref_rdf = rdfs[0]

    # ── AK4 ──────────────────────────────────────────────────
    if has_column(ref_rdf, "Jet_pt"):
        print(f"\nAK4 → {len(AK4_HISTS)} plots")
        booked = [book_histograms(rdf, AK4_HISTS, f"f{i}_ak4")
                  for i, rdf in enumerate(rdfs)]

        for var_idx, (*_, xtitle, sname) in enumerate(AK4_HISTS):
            hists = []
            for file_results in booked:
                hp = file_results[var_idx][0]
                h = hp.GetValue().Clone(f"_h_ak4_{var_idx}_{id(hp)}")
                h.SetDirectory(0)
                hists.append(h)
            make_canvas(hists, xtitle, f"ak4_{sname}", labels, args.outdir)
    else:
        print("WARNING: 'Jet_pt' not found – skipping AK4.")

    # ── AK8 ──────────────────────────────────────────────────
    if has_column(ref_rdf, "FatJet_pt"):
        mass_col = "FatJet_msoftdrop" if has_column(ref_rdf, "FatJet_msoftdrop") \
            else "FatJet_mass"
        mass_title = "AK8 m_{soft-drop} [GeV]" if "msoftdrop" in mass_col \
                     else "AK8 jet mass [GeV]"
        mass_sname = "FatJet_msoftdrop" if "msoftdrop" in mass_col \
                     else "FatJet_mass"
        print(f"\nAK8 → {len(AK8_HISTS) + 1} plots  (mass: {mass_col})")

        ak8_specs = AK8_HISTS + [
            (mass_col, "nFatJet > 0", 50, 0, 300, mass_title, mass_sname),
        ]
        booked = [book_histograms(rdf, ak8_specs, f"f{i}_ak8")
                  for i, rdf in enumerate(rdfs)]

        for var_idx, (*_, xtitle, sname) in enumerate(ak8_specs):
            hists = []
            for file_results in booked:
                hp = file_results[var_idx][0]
                h = hp.GetValue().Clone(f"_h_ak8_{var_idx}_{id(hp)}")
                h.SetDirectory(0)
                hists.append(h)
            make_canvas(hists, xtitle, f"ak8_{sname}", labels, args.outdir)
    else:
        print("WARNING: 'FatJet_pt' not found – skipping AK8.")

    # ── PF candidates: inclusive ─────────────────────────────
    if has_column(ref_rdf, "PFCands_pt"):
        # filter to only columns that actually exist in this file
        pf_specs = [spec for spec in PFCANDS_HISTS
                    if has_column(ref_rdf, spec[0].split("[")[0])]
        print(f"\nPFCands (inclusive) → {len(pf_specs)} plots")

        booked = [book_histograms(rdf, pf_specs, f"f{i}_pf")
                  for i, rdf in enumerate(rdfs)]

        LOGY_SNANES = {"PFCands_pt", "PFCands_pt_lead",
                       "PFCands_puppiWeight", "PFCands_puppiWeightNoLep"}
        for var_idx, (*_, xtitle, sname) in enumerate(pf_specs):
            hists = []
            for file_results in booked:
                hp = file_results[var_idx][0]
                h = hp.GetValue().Clone(f"_h_pf_{var_idx}_{id(hp)}")
                h.SetDirectory(0)
                hists.append(h)
            make_canvas(hists, xtitle, f"pf_{sname}", labels, args.outdir,
                        logy=(sname in LOGY_SNANES))

        # ── PF candidates: per particle type ─────────────────
        if has_column(ref_rdf, "PFCands_pdgId"):
            n_pertype = len(PF_PARTICLE_TYPES) * len(PFCANDS_PERTYPE_HISTS)
            print(f"\nPFCands (per type)  -> {n_pertype} plots")

            for type_key, (mask_expr, type_label) in PF_PARTICLE_TYPES.items():
                for col, nb, xlo, xhi, var_label in PFCANDS_PERTYPE_HISTS:
                    sname = f"PFCands_{type_key}_{col.replace('PFCands_', '')}"
                    xtitle = f"{type_label}: {var_label}"

                    hists = []
                    for fi, rdf in enumerate(rdfs):
                        node = rdf.Filter("nPFCands > 0")
                        masked = f"_sel_{type_key}_{col.replace('PFCands_', '')}_f{fi}"
                        # RVec boolean-mask indexing: rvec[bool_rvec]
                        node = node.Define(
                            masked,
                            f"{col}[{mask_expr}]"
                        )
                        hp = node.Histo1D(
                            (f"h_{sname}_f{fi}", "", nb, xlo, xhi), masked
                        )
                        h = hp.GetValue().Clone(f"_clone_{sname}_f{fi}")
                        h.SetDirectory(0)
                        hists.append(h)

                    make_canvas(hists, xtitle, f"pf_{sname}", labels, args.outdir,
                                logy=("_pt" in sname))
        else:
            print("  (skipping per-type plots: PFCands_pdgId not found)")

        # ── PF pt*puppiWeight: one plot per particle type, all files compared ─
        if has_column(ref_rdf, "PFCands_pdgId") and has_column(ref_rdf, "PFCands_puppiWeight"):
            n_ptw = len(PF_PARTICLE_TYPES)
            print(f"\nPFCands pt*puppiWeight per type → {n_ptw} plots")

            for type_key, (mask_expr, type_label) in PF_PARTICLE_TYPES.items():
                sname = f"PFCands_{type_key}_ptPuppi"
                xtitle = f"{type_label}: p_{{T}} #times PUPPI weight [GeV]"

                hists = []
                for fi, rdf in enumerate(rdfs):
                    node = rdf.Filter("nPFCands > 0")
                    col_name = f"_ptw_{type_key}_f{fi}"
                    node = node.Define(
                        col_name,
                        f"(PFCands_pt * PFCands_puppiWeight)[{mask_expr}]"
                    )
                    hp = node.Histo1D(
                        (f"h_{sname}_f{fi}", "", 60, 0, 20), col_name
                    )
                    h = hp.GetValue().Clone(f"_clone_{sname}_f{fi}")
                    h.SetDirectory(0)
                    hists.append(h)

                make_canvas(hists, xtitle,
                            f"pf_{sname}", labels, args.outdir, logy=True)
    else:
        print("WARNING: 'PFCands_pt' not found – skipping PF candidates.")

    # ── Global event variables (e.g. PV_npvsGood) ───────────────
    global_specs = [s for s in GLOBAL_HISTS if has_column(ref_rdf, s[0])]
    if global_specs:
        print(f"\nGlobal → {len(global_specs)} plots")
        booked_glob = [book_histograms(rdf, global_specs, f"f{i}_glob")
                       for i, rdf in enumerate(rdfs)]
        for var_idx, (*_, xtitle, sname) in enumerate(global_specs):
            hists = []
            for file_results in booked_glob:
                hp = file_results[var_idx][0]
                h = hp.GetValue().Clone(f"_h_glob_{var_idx}_{id(hp)}")
                h.SetDirectory(0)
                hists.append(h)
            make_canvas(hists, xtitle, f"glob_{sname}", labels, args.outdir)

    # ── 2D profiles: <pt> and <pt*puppiWeight> vs eta x phi ──────
    if (has_column(ref_rdf, "PFCands_pt") and
            has_column(ref_rdf, "PFCands_eta") and
            has_column(ref_rdf, "PFCands_phi") and
            has_column(ref_rdf, "PFCands_pdgId")):

        ne, emin, emax = PROFILE2D_ETA_BINS,  *PROFILE2D_ETA_RANGE
        np_, pmin, pmax = PROFILE2D_PHI_BINS, *PROFILE2D_PHI_RANGE
        has_puppi = has_column(ref_rdf, "PFCands_puppiWeight")
        quants = ["pt"]
        if has_puppi:
            quants.append("ptPuppi")
        n2d = len(PF_PARTICLE_TYPES) * len(quants) * \
            (len(rdfs) + len(rdfs) - 1)
        print(f"\n2D profiles (eta x phi) → {len(PF_PARTICLE_TYPES) * len(quants)} types x quant, "
              f"{len(rdfs)} per-file + {len(rdfs)-1} ratio plots each")

        for type_key, (mask_expr, type_label) in PF_PARTICLE_TYPES.items():
            # collect TProfile2D for each file and each quantity
            profs = {q: [] for q in quants}

            for fi, rdf in enumerate(rdfs):
                node = rdf.Filter("nPFCands > 0")

                # masked columns for this particle type
                eta_col = f"_eta2d_{type_key}_f{fi}"
                phi_col = f"_phi2d_{type_key}_f{fi}"
                pt_col = f"_pt2d_{type_key}_f{fi}"
                node = node.Define(eta_col, f"PFCands_eta[{mask_expr}]")
                node = node.Define(phi_col, f"PFCands_phi[{mask_expr}]")
                node = node.Define(pt_col,  f"PFCands_pt[{mask_expr}]")

                # <pt> profile
                pname_pt = f"prof_pt_{type_key}_f{fi}"
                hp_pt = node.Profile2D(
                    (pname_pt, "", ne, emin, emax, np_, pmin, pmax),
                    eta_col, phi_col, pt_col
                )
                p_pt = hp_pt.GetValue().Clone(f"_clone_{pname_pt}")
                p_pt.SetDirectory(0)
                profs["pt"].append(p_pt)

                if has_puppi:
                    ptw_col = f"_ptw2d_{type_key}_f{fi}"
                    node = node.Define(ptw_col,
                                       f"(PFCands_pt * PFCands_puppiWeight)[{mask_expr}]")
                    pname_ptw = f"prof_ptPuppi_{type_key}_f{fi}"
                    hp_ptw = node.Profile2D(
                        (pname_ptw, "", ne, emin, emax, np_, pmin, pmax),
                        eta_col, phi_col, ptw_col
                    )
                    p_ptw = hp_ptw.GetValue().Clone(f"_clone_{pname_ptw}")
                    p_ptw.SetDirectory(0)
                    profs["ptPuppi"].append(p_ptw)

            # draw per-file profiles and file1/fileN ratios
            for q in quants:
                zlabel = "#LT p_{T} #GT [GeV]" if q == "pt" else "#LT p_{T} #times w_{PUPPI} #GT [GeV]"

                # per-file
                for fi, prof in enumerate(profs[q]):
                    title = f"{type_label} {zlabel} [{labels[fi]}]"
                    oname = f"prof2d_{type_key}_{q}_{labels[fi].replace(' ', '_')}"
                    draw_profile2d(
                        prof, title,
                        os.path.join(args.outdir, f"{oname}.pdf")
                    )

                # ratio: file1 / fileN  (ref = profs[q][0])
                ref_prof = profs[q][0]
                for fi in range(1, len(profs[q])):
                    title = (f"{type_label} {zlabel} "
                             f"ratio {labels[0]} / {labels[fi]}")
                    oname = (f"prof2d_{type_key}_{q}_ratio_"
                             f"{labels[0].replace(' ', '_')}_over_"
                             f"{labels[fi].replace(' ', '_')}")
                    make_profile2d_ratio(
                        ref_prof, profs[q][fi],
                        oname, title,
                        os.path.join(args.outdir, f"{oname}.pdf")
                    )
    else:
        if not has_column(ref_rdf, "PFCands_pt"):
            print("Skipping 2D profiles: PFCands_pt not found.")

    print(f"\nDone. {len(os.listdir(args.outdir))} PDFs in '{args.outdir}/'")


if __name__ == "__main__":
    main()

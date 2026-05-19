import FWCore.ParameterSet.Config as cms

doMLPF = False

from Configuration.Eras.Era_Run3_2025_cff import Run3_2025
if doMLPF:
    from Configuration.ProcessModifiers.mlpf_cff import mlpf
    process = cms.Process('RECO', Run3_2025, mlpf)
    outputname = "nano_mlpf_mc.root"
else:
    process = cms.Process('RECO', Run3_2025)
    outputname = "nano_pf_digi_mc.root"

# --------------------------------------------------------------------------
# Standard sequences (same order as cmsDriver-generated config)
# --------------------------------------------------------------------------
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mix_2025_25ns_Run3pp13p6TeVSpring25_PoissonOOTPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.PAT_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# --------------------------------------------------------------------------
# Input: GEN-SIM
# --------------------------------------------------------------------------
process.maxEvents = cms.untracked.PSet(
    input  = cms.untracked.int32(5),
    output = cms.optional.untracked.allowed(cms.int32, cms.PSet)
)

process.source = cms.Source("PoolSource",
    dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
    fileNames = cms.untracked.vstring(
        'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/GEN-SIM/142X_mcRun3_2025_realistic_v7-v3/2530000/000bf8fc-51cb-4413-a012-d362bac45ca8.root',
    ),
    inputCommands = cms.untracked.vstring(
        'keep *',
        'drop *_genParticles_*_*',
        'drop *_genParticlesForJets_*_*',
        'drop *_kt4GenJets_*_*',
        'drop *_kt6GenJets_*_*',
        'drop *_iterativeCone5GenJets_*_*',
        'drop *_ak4GenJets_*_*',
        'drop *_ak7GenJets_*_*',
        'drop *_ak8GenJets_*_*',
        'drop *_ak4GenJetsNoNu_*_*',
        'drop *_ak8GenJetsNoNu_*_*',
        'drop *_genCandidatesForMET_*_*',
        'drop *_genParticlesForMETAllVisible_*_*',
        'drop *_genMetCalo_*_*',
        'drop *_genMetCaloAndNonPrompt_*_*',
        'drop *_genMetTrue_*_*',
        'drop *_genMetIC5GenJs_*_*'
    ),
    secondaryFileNames = cms.untracked.vstring()
)

# --------------------------------------------------------------------------
# Pileup: flat PU 50-150 with MinBias GEN-SIM
# --------------------------------------------------------------------------
_nPUbins = 101  # 50..150 inclusive
process.mix.input.nbPileupEvents = cms.PSet(
    probFunctionVariable = cms.vint32(list(range(0, 151))),
    probValue            = cms.vdouble([0.0] * 50 + [1.0 / _nPUbins] * _nPUbins),
    # histoFileName is required: BMixingModule checks for its presence to enter the
    # probFunction branch; without it the PileUpConfig is never created (averageNumber=0)
    # and doPileUp() returns false for every event.
    histoFileName        = cms.untracked.string('histProbFunction.root'),
)

process.mix.input.fileNames = cms.untracked.vstring([
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/0027fe16-7942-461d-8aff-48e06c54bd3f.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/0036a6bc-9742-475b-8116-5bc7176cfaea.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/0044eaa5-4a6d-4f22-b612-1d873f978ade.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/0074ab83-d0b2-4147-b56a-030dde9da6b9.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/008d5348-f87b-4761-946f-f9dc74d702e3.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/009fe8fb-6880-4a45-bdad-3e59c2e2f2b5.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/00d78df4-3538-4780-bc6d-5a0c6d5e6661.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/012dc9ac-fac9-4de9-9422-885150e7b123.root',
    'root://eoscms.cern.ch//eos/cms/store/mc/Run3Winter25GS/MinBias_TuneCP5_13p6TeV-pythia8/GEN-SIM/Winter25PU_correctBS_142X_mcRun3_2025_realistic_v4-v1/2550000/014997a2-59a3-4a58-9490-7d66a3d058b7.root',
])

# --------------------------------------------------------------------------
# Global tag & output
# --------------------------------------------------------------------------
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '142X_mcRun3_2025_realistic_v9', '')

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel     = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier   = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName       = cms.untracked.string(f'file:{outputname}'),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# --------------------------------------------------------------------------
# Paths (same names as cmsDriver-generated config)
# --------------------------------------------------------------------------
process.digitisation_step  = cms.Path(process.pdigi)
process.L1simulation_step  = cms.Path(process.SimL1Emulator)
process.digi2raw_step      = cms.Path(process.DigiToRaw)
process.raw2digi_step      = cms.Path(process.RawToDigi)
process.L1Reco_step        = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.nanoAOD_step       = cms.Path(process.nanoSequenceMC)
process.endjob_step        = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

process.schedule = cms.Schedule(
    process.digitisation_step,
    process.L1simulation_step,
    process.digi2raw_step,
    process.raw2digi_step,
    process.L1Reco_step,
    process.reconstruction_step,
    process.nanoAOD_step,
    process.endjob_step,
    process.NANOAODoutput_step,
)

process.schedule.associate(process.patTask)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# --------------------------------------------------------------------------
# Customisations
# --------------------------------------------------------------------------
from PhysicsTools.NanoAOD.custom_btv_cff import addPFCands
process = addPFCands(process, allPF=True)

from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon
process = nanoAOD_customizeCommon(process)

from Configuration.StandardSequences.PAT_cff import miniAOD_customizeAllMC
process = miniAOD_customizeAllMC(process)

from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
process = customiseLogErrorHarvesterUsingOutputCommands(process)

from PhysicsTools.NanoAOD.custom_highpu_cff import addCollectionSizes, addPackedGenParticlesTable
process = addCollectionSizes(process)
process = addPackedGenParticlesTable(process)

# No HLT step: disable the two consumers of the patTrigger chain so it never runs.
process.patMuons.addTriggerMatching = cms.bool(False)
process.nanoSequenceMC.remove(process.nanoSequenceOnlyFullSim)

# displacedRegionalStep generates too many seeds at PU~150
process.iterTracking.remove(process.displacedRegionalStep)

from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)

process.options = cms.untracked.PSet(
    numberOfThreads = cms.untracked.uint32(8),
    numberOfStreams  = cms.untracked.uint32(1),
    wantSummary      = cms.untracked.bool(False),
)

process.MessageLogger.cerr.threshold = 'WARNING'
process.MessageLogger.cerr.default.limit = -1
process.MessageLogger.cerr.TooManyClusters  = cms.untracked.PSet(limit=cms.untracked.int32(-1))
process.MessageLogger.cerr.TooManyPairs     = cms.untracked.PSet(limit=cms.untracked.int32(-1))
process.MessageLogger.cerr.TooManyDoublets  = cms.untracked.PSet(limit=cms.untracked.int32(-1))

# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: reco_to_nano_dump --filein file:0030b745-e184-4391-9515-e8d13847ad45.root --fileout file:nano_with_cands.root --step RAW2DIGI,L1Reco,RECO,PAT,NANO --datatier NANOAOD --eventcontent NANOAOD --conditions auto:run3_data_prompt --era Run3_2025 --customise PhysicsTools/NanoAOD/custom_btv_cff.addPFCands --nThreads 8 --no_exec -n 100
import FWCore.ParameterSet.Config as cms

doMLPF=True

from Configuration.Eras.Era_Run3_2025_cff import Run3_2025
if doMLPF:
    from Configuration.ProcessModifiers.mlpf_cff import mlpf
    process = cms.Process('RECO',Run3_2025,mlpf)
    outputname = "nano_mlpf_2.root"
else:
    process = cms.Process('RECO',Run3_2025)
    outputname = "nano_pf.root"

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load('Configuration.StandardSequences.PAT_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(50),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        #'file:0030b745-e184-4391-9515-e8d13847ad45.root'
        'file:/afs/cern.ch/work/y/yofeng/public/MLPF/raw_08357e72-91de-42c0-b359-30ab4d718a54.root'
    ),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('reco_to_nano_dump nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string(f'file:{outputname}'),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run3_data_prompt', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.Flag_BadChargedCandidateFilter = cms.Path(process.BadChargedCandidateFilter)
process.Flag_BadChargedCandidateSummer16Filter = cms.Path(process.BadChargedCandidateSummer16Filter)
process.Flag_BadPFMuonDzFilter = cms.Path(process.BadPFMuonDzFilter)
process.Flag_BadPFMuonFilter = cms.Path(process.BadPFMuonFilter)
process.Flag_BadPFMuonSummer16Filter = cms.Path(process.BadPFMuonSummer16Filter)
process.Flag_CSCTightHalo2015Filter = cms.Path(process.CSCTightHalo2015Filter)
process.Flag_CSCTightHaloFilter = cms.Path(process.CSCTightHaloFilter)
process.Flag_CSCTightHaloTrkMuUnvetoFilter = cms.Path(process.CSCTightHaloTrkMuUnvetoFilter)
process.Flag_EcalDeadCellBoundaryEnergyFilter = cms.Path(process.EcalDeadCellBoundaryEnergyFilter)
process.Flag_EcalDeadCellTriggerPrimitiveFilter = cms.Path(process.EcalDeadCellTriggerPrimitiveFilter)
process.Flag_HBHENoiseFilter = cms.Path(process.HBHENoiseFilterResultProducer+process.HBHENoiseFilter)
process.Flag_HBHENoiseIsoFilter = cms.Path(process.HBHENoiseFilterResultProducer+process.HBHENoiseIsoFilter)
process.Flag_HcalStripHaloFilter = cms.Path(process.HcalStripHaloFilter)
process.Flag_chargedHadronTrackResolutionFilter = cms.Path(process.chargedHadronTrackResolutionFilter)
process.Flag_ecalBadCalibFilter = cms.Path(process.ecalBadCalibFilter)
process.Flag_ecalLaserCorrFilter = cms.Path(process.ecalLaserCorrFilter)
process.Flag_eeBadScFilter = cms.Path(process.eeBadScFilter)
process.Flag_globalSuperTightHalo2016Filter = cms.Path(process.globalSuperTightHalo2016Filter)
process.Flag_globalTightHalo2016Filter = cms.Path(process.globalTightHalo2016Filter)
process.Flag_goodVertices = cms.Path(process.primaryVertexFilter)
process.Flag_hcalLaserEventFilter = cms.Path(process.hcalLaserEventFilter)
process.Flag_hfNoisyHitsFilter = cms.Path(process.hfNoisyHitsFilter)
process.Flag_muonBadTrackFilter = cms.Path(process.muonBadTrackFilter)
process.Flag_trackingFailureFilter = cms.Path(process.goodVertices+process.trackingFailureFilter)
process.Flag_trkPOGFilters = cms.Path(process.trkPOGFilters)
process.Flag_trkPOG_logErrorTooManyClusters = cms.Path(~process.logErrorTooManyClusters)
process.Flag_trkPOG_manystripclus53X = cms.Path(~process.manystripclus53X)
process.Flag_trkPOG_toomanystripclus53X = cms.Path(~process.toomanystripclus53X)
process.nanoAOD_step = cms.Path(process.nanoSequence)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.Flag_BadChargedCandidateFilter,process.Flag_BadChargedCandidateSummer16Filter,process.Flag_BadPFMuonDzFilter,process.Flag_BadPFMuonFilter,process.Flag_BadPFMuonSummer16Filter,process.Flag_CSCTightHalo2015Filter,process.Flag_CSCTightHaloFilter,process.Flag_CSCTightHaloTrkMuUnvetoFilter,process.Flag_EcalDeadCellBoundaryEnergyFilter,process.Flag_EcalDeadCellTriggerPrimitiveFilter,process.Flag_HBHENoiseFilter,process.Flag_HBHENoiseIsoFilter,process.Flag_HcalStripHaloFilter,process.Flag_chargedHadronTrackResolutionFilter,process.Flag_ecalBadCalibFilter,process.Flag_ecalLaserCorrFilter,process.Flag_eeBadScFilter,process.Flag_globalSuperTightHalo2016Filter,process.Flag_globalTightHalo2016Filter,process.Flag_goodVertices,process.Flag_hcalLaserEventFilter,process.Flag_hfNoisyHitsFilter,process.Flag_muonBadTrackFilter,process.Flag_trackingFailureFilter,process.Flag_trkPOGFilters,process.Flag_trkPOG_logErrorTooManyClusters,process.Flag_trkPOG_manystripclus53X,process.Flag_trkPOG_toomanystripclus53X,process.nanoAOD_step,process.endjob_step,process.NANOAODoutput_step)
process.schedule.associate(process.patTask)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads = 8
process.options.numberOfStreams = 0

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.custom_btv_cff
from PhysicsTools.NanoAOD.custom_btv_cff import addPFCands 

#call to customisation function addPFCands imported from PhysicsTools.NanoAOD.custom_btv_cff
process = addPFCands(process, allPF=True)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# End of customisation functions

# customisation of the process.

# Automatic addition of the customisation function from Configuration.StandardSequences.PAT_cff
from Configuration.StandardSequences.PAT_cff import miniAOD_customizeAllData 

#call to customisation function miniAOD_customizeAllData imported from Configuration.StandardSequences.PAT_cff
process = miniAOD_customizeAllData(process)

# End of customisation functions

# Customisation from command line

#Have logErrorHarvester wait for the same EDProducers to finish as those providing data for the OutputModule
from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
process = customiseLogErrorHarvesterUsingOutputCommands(process)

process.collectionSizes = cms.EDProducer("CollectionSizeProducer")
process.collectionSizesTable = cms.EDProducer("GlobalVariablesTableProducer",
    variables = cms.PSet(
        nGeneralTracks = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nGeneralTracks"),
            doc = cms.string("Total number of generalTracks")
        ),
        nSiPixelClusters = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nSiPixelClusters"),
            doc = cms.string("Total number of siPixelClusters")
        ),
        nSiStripClusters = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nSiStripClusters"),
            doc = cms.string("Total number of siStripClusters")
        ),
        nHighPurityTracks = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nHighPurityTracks"),
            doc = cms.string("Total number of High Purity Tracks")
        ),
        nInitialStepTracks = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nInitialStepTracks"),
            doc = cms.string("Total number of Initial Step Tracks")
        ),
        nLateStepTracks = cms.PSet(
            type = cms.string("int"),
            src = cms.InputTag("collectionSizes", "nLateStepTracks"),
            doc = cms.string("Total number of Late Step Tracks")
        )
    )
)
process.size_step = cms.Path(process.collectionSizes + process.collectionSizesTable)
nano_idx = process.schedule.index(process.nanoAOD_step)
process.schedule.insert(nano_idx, process.size_step)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

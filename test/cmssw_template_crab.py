from PhysicsTools.PatAlgos.tools.coreTools import *

def addScrapingFilter( process ):
    process.scrapingFilter = cms.EDFilter( 'FilterOutScraping',
                                           applyfilter = cms.untracked.bool( True ),
                                           debugOn = cms.untracked.bool( False ),
                                           numtrack = cms.untracked.uint32( 10 ),
                                           thresh = cms.untracked.double( 0.25 )
                                           )

    process.p_scrapingFilter = cms.Path( process.scrapingFilter )
    process.ACSkimAnalysis.filterlist.append( 'p_scrapingFilter' )
    


def addKinematicsFilter( process ):
    process.load( 'GeneratorInterface.GenFilters.TotalKinematicsFilter_cfi' )

    process.p_kinematicsfilter = cms.Path( process.totalKinematicsFilter )
    process.ACSkimAnalysis.filterlist.append( 'p_kinematicsfilter' )

process = cms.Process("ANA")

isData=@ISDATA@
qscalehigh=@QSCALE_LOW@
qscalelow=@QSCALE_HIGH@
tauSwitch=@DOTAU@
calojetSwitch=@DOCALOJETS@
Pythia8Switch=@PYTHIA8@
SherpaSwitch=@SHERPA@
FastJetsSwitch=@FASTJET@
MatchAllSwitch=@MATCHALL@
SusyParSwith=@SUSYPAR@
#~ qscalehigh=200.
#~ qscalelow=50.
#~ isData=False
#~ tauSwitch=False;
# Message logger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.categories.extend(['SusyACSkimAnalysis'])
process.MessageLogger.cerr.default.limit = -1
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

#-- Calibration tag -----------------------------------------------------------
# Should match input file's tag
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('@GLOBALTAG@')
#~ process.GlobalTag.globaltag = cms.string('START44_V5::All')
process.load("Configuration.StandardSequences.MagneticField_cff")

#-- PAT standard config -------------------------------------------------------
process.load("PhysicsTools.PatAlgos.patSequences_cff")
process.load("RecoVertex.Configuration.RecoVertex_cff")

from RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi import *
process.load("RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi")

#-- To get JEC in 4_2 return rho corrections:----------------------------------------------------
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
process.load('RecoJets.Configuration.RecoPFJets_cff')
process.kt6PFJets.doRhoFastjet = True
process.ak5PFJets.doAreaFastjet = True

#--To modify noPU needed for METnoPU -------------------------------------------
process.load('CommonTools.ParticleFlow.pfNoPileUp_cff')

# Output (PAT file only created if
# process.outpath = cms.EndPath(process.out)
# is called at the end
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out2 = cms.OutputModule(
    "PoolOutputModule",
    fileName       = cms.untracked.string('dummy.root'),
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    dropMetaData   = cms.untracked.string('DROPPED'),
    outputCommands = cms.untracked.vstring('keep *')
    )

##dummy out to be modifyed by pf2pat
process.out = cms.OutputModule(
    "PoolOutputModule",
    fileName       = cms.untracked.string('dummy2.root'),
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    dropMetaData   = cms.untracked.string('DROPPED'),
    outputCommands = cms.untracked.vstring('keep *')
    )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string('out.root')
                                   )

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
)

# see https://twiki.cern.ch/twiki/bin/view/CMS/HBHEAnomalousSignals2011         
process.load("CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi")


### Input / output ###

# Input file
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring([
    '/store/mc/Fall11/DYToMuMu_M-10To20_CT10_TuneZ2_7TeV-powheg-pythia/AODSIM/PU_S6-START44_V5-v1/0000/864538D3-E5FB-E011-B5D2-00266CF275E0.root']
    ),
    #duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
)
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)
#PAT Stuff
if not tauSwitch:
	removeSpecificPATObjects(process,['Taus']) #removes Taus and Jets from PAT default sequence. Not needed there.
# switch on PAT trigger
from PhysicsTools.PatAlgos.tools.trigTools import switchOnTrigger
switchOnTrigger(process)
process.patTrigger.processName = "*"
process.patTriggerEvent.processName = "*"

process.patJets.addTagInfos = cms.bool(False)  # AOD only

process.patMuons.embedCombinedMuon = False;
process.patMuons.embedStandAloneMuon = False;

# add iso deposits
#from PhysicsTools.PatAlgos.tools.muonTools import addMuonUserIsolation
#addMuonUserIsolation(process)

#process.load("aachen3a.ACSusyAnalysis.pfIsoForLeptons_cff")




if tauSwitch:
	process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

# PF2PAT
from PhysicsTools.PatAlgos.tools.pfTools import *

postfix = "PFlow"
if isData:
    usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=False, postfix=postfix, jetCorrections=('AK5PFchs',['L1FastJet','L2Relative','L3Absolute','L2L3Residual']))
    removeMCMatching(process, ['All'])
else:
     usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=True, postfix=postfix, jetCorrections=('AK5PFchs',['L1FastJet', 'L2Relative', 'L3Absolute']))
if tauSwitch:
	adaptPFTaus(process,"hpsPFTau",postfix=postfix)


# for PFnoPU
process.pfPileUpPFlow.Enable = True
process.pfPileUpPFlow.checkClosestZVertex = cms.bool(False)
process.pfPileUpPFlow.Vertices = cms.InputTag('goodOfflinePrimaryVertices')
process.pfJetsPFlow.doAreaFastjet = True
process.pfJetsPFlow.doRhoFastjet = False


from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
process.kt6PFJetsPFlow = kt4PFJets.clone(
    rParam = cms.double(0.6),
    #src = cms.InputTag('pfNoElectron'+postfix),
    doAreaFastjet = cms.bool(True),
    doRhoFastjet = cms.bool(True)
    )

process.patJetCorrFactorsPFlow.rho = cms.InputTag("kt6PFJetsPFlow", "rho")
if isData:
    process.patJetCorrFactorsPFlow.levels = cms.vstring('L1FastJet', 'L2Relative', 'L3Absolute','L2L3Residual')
else:
    process.patJetCorrFactorsPFlow.levels = cms.vstring('L1FastJet', 'L2Relative', 'L3Absolute') # MC


if isData:
    process.patJetCorrFactors.levels = cms.vstring('L1FastJet', 'L2Relative', 'L3Absolute','L2L3Residual') # DATA
else:
    process.patJetCorrFactors.levels = cms.vstring('L1FastJet', 'L2Relative', 'L3Absolute') # MC

process.patJetCorrFactors.useRho = True

# Add anti-kt 5 jets
# this is only for calo met is there an other way?




# Add the PV selector and KT6 producer to the sequence
getattr(process,"patPF2PATSequence"+postfix).replace(
    getattr(process,"pfNoElectron"+postfix),
    getattr(process,"pfNoElectron"+postfix)*process.kt6PFJetsPFlow )


# add TrackCorrected  met
from PhysicsTools.PatAlgos.tools.metTools import *
addTcMET(process, 'TC')

# get the jet corrections
from PhysicsTools.PatAlgos.tools.jetTools import *

# Add met with NoPU to the Collections
from aachen3a.ACSusyAnalysis.pfMET_cfi import *
process.pfMetPFnoPU         = pfMET.clone()
process.pfMetPFnoPU.alias   = 'pfMetNoPileUp'
process.pfMetPFnoPU.src     = 'pfNoPileUpPFlow'
process.pfMetPFnoPU.jets = cms.InputTag("ak5PFJets")



from JetMETCorrections.Configuration.JetCorrectionServices_cff import *
from JetMETCorrections.Type1MET.pfMETCorrections_cff import *

process.pfType1CorrectedMet =   pfType1CorrectedMet.clone()
process.pfCandsNotInJet =       pfCandsNotInJet.clone()
process.pfJetMETcorr =          pfJetMETcorr.clone()
process.pfCandMETcorr =         pfCandMETcorr.clone()

if isData:
    process.pfJetMETcorr.jetCorrLabel = cms.string('ak5PFL1FastL2L3Residual')
else:
    process.pfJetMETcorr.jetCorrLabel = cms.string('ak5PFL1FastL2L3')
    
process.pfType1CorrectedMet.src = cms.InputTag("pfMetPFnoPU")

process.pfType1CorrectedPFMet = pfType1CorrectedMet.clone()
process.pfType1CorrectedPFMet.src     = cms.InputTag("pfMet")



################################
###                          ###
###  Analysis configuration  ###
###                          ###
################################


### Definition of all tags here
elecTag         = cms.InputTag("patElectrons")
pfelecTag      = cms.InputTag("patElectronsPFlow")
photonTag         = cms.InputTag("patPhotons")
calojetTag     = cms.InputTag("patJetsAK5Calo")
pfjetTag        = cms.InputTag("patJetsPFlow")
muonTag      = cms.InputTag("patMuons")
PFmuonTag  = cms.InputTag("selectedPatMuonsPFlow")
tauTag         = cms.InputTag("patTausPFlow")
metTag        = cms.InputTag("patMETs")
metTagTC    = cms.InputTag("patMETsTC")
metTagPF    = cms.InputTag("patMETsPFlow")
metTagPFnoPU=cms.InputTag("pfMetPFnoPU")
metTagJPFnoPUType1 =cms.InputTag("pfType1CorrectedMet")
metTagcorMetGlobalMuons     = cms.InputTag("pfType1CorrectedPFMet")
#these two are ignored for now:
metTagHO    = cms.InputTag("metHO")
metTagNoHF= cms.InputTag("metNoHF")
genTag        = cms.InputTag("genParticles")
genJetTag    = cms.InputTag("ak5GenJets")
vtxTag         = cms.InputTag("offlinePrimaryVertices")
reducedBarrelRecHitCollection = cms.InputTag("reducedEcalRecHitsEB")
reducedEndcapRecHitCollection = cms.InputTag("reducedEcalRecHitsEE")
#ebhitsTag  = cms.InputTag("ecalRecHit", "EcalRecHitsEB");  # RECO
ebhitsTag     = cms.InputTag("reducedEcalRecHitsEB");   # AOD

### Cuts and switches ###
process.ACSkimAnalysis = cms.EDFilter(
    "SusyACSkimAnalysis",

    is_MC      = cms.bool(not isData),  # set to 'False' for real Data !
    is_PYTHIA8 = cms.bool(Pythia8Switch),  # set to 'True' if running on PYTHIA8    
    is_SHERPA  = cms.bool(SherpaSwitch),  # set to 'True' if running on SHERPA
    do_fatjets = cms.bool(FastJetsSwitch),  # set to 'True' for fat jets
    matchAll   = cms.bool(MatchAllSwitch),  # if True all truth leptons are matched else only ele and mu
    susyPar    = cms.bool(SusyParSwith),
    doCaloJet  = cms.bool(calojetSwitch),
    doTaus     = cms.bool(tauSwitch),




    calojetTag = calojetTag,
    pfjetTag   = pfjetTag,
    elecTag    = elecTag,
    photonTag  = photonTag,
    pfelecTag  = pfelecTag,
    muonTag    = muonTag,
    PFmuonTag  = PFmuonTag,
    tauTag     = tauTag,
    metTag     = metTag,
    metTagTC   = metTagTC,
    metTagPF   = metTagPF,
    metTagPFnoPU   =metTagPFnoPU,
    metTagJPFnoPUType1= metTagJPFnoPUType1,
    metTagcorMetGlobalMuons =metTagcorMetGlobalMuons,
    metTagHO = metTagHO,
    metTagNoHF = metTagNoHF,
    genTag     = genTag,
    genJetTag  = genJetTag,
    vtxTag     = vtxTag,
    ebhitsTag  = ebhitsTag,
    reducedBarrelRecHitCollection = reducedBarrelRecHitCollection,
    reducedEndcapRecHitCollection = reducedEndcapRecHitCollection,


    qscale_low  = cms.double(qscalelow),
    qscale_high = cms.double(qscalehigh),
    muoptfirst = cms.double(@MUOPTFIRST@),
    muoptother = cms.double(@MUOPTOTHER@),
    muoeta     = cms.double(@MUOETA@),
    elept      = cms.double(@ELEPT@),
    eleeta     = cms.double(@ELEETA@),
    phopt      = cms.double(@PHOPT@),
    phoeta     = cms.double(@PHOETA@),    
    pfelept    = cms.double(@PFELEPT@),
    pfeleeta   = cms.double(@PFELEETA@),
    calojetpt  = cms.double(@CALOJETPT@),
    calojeteta = cms.double(@CALOJETETA@),
    pfjetpt    = cms.double(@PFJETPT@),
    pfjeteta   = cms.double(@PFJETETA@),
    taupt      = cms.double(@TAUPT@),
    taueta     = cms.double(@TAUETA@),
    metcalo    = cms.double(@METCALO@),
    metpf      = cms.double(@METPF@),
    mettc      = cms.double(@METTC@),
    nele       = cms.int32(@NELE@),
    npho       = cms.int32(@NPHO@),
    npfele     = cms.int32(@NPFELE@),
    nmuo       = cms.int32(@NMUO@),
    ncalojet   = cms.int32(@NCALOJET@),
    npfjet     = cms.int32(@NPFJET@),
    ntau       = cms.int32(@NTAU@),
    htc        = cms.double(@HTC@), 
    PFhtc      = cms.double(@PFHTC@),
    triggerContains=cms.string(@TRIGGERCONTAINS@),
    muoMinv    = cms.double(@MUOMINV@), 
    muoDMinv   = cms.double(@MUODMINV@), 

    btag       = cms.string('trackCountingHighEffBJetTags'),

    # Calo Jet ID
    jetselvers = cms.string("PURE09"),
    jetselqual = cms.string("LOOSE")
    

		
)



### Define the paths
if tauSwitch:
	process.p = cms.Path(
		process.kt6PFJets * 
		process.ak5PFJets *
		process.goodOfflinePrimaryVertices*
		process.HBHENoiseFilterResultProducer*
		process.PFTau*
		process.patDefaultSequence*
		getattr(process,"patPF2PATSequence"+postfix)*
		process.pfMetPFnoPU*
		process.pfJetMETcorr*
		process.pfType1CorrectedMet*
		process.pfType1CorrectedPFMet
		)
else: 
	process.p = cms.Path(
		process.kt6PFJets * 
		process.ak5PFJets *
		process.goodOfflinePrimaryVertices*
		process.HBHENoiseFilterResultProducer*
		process.patDefaultSequence*
		getattr(process,"patPF2PATSequence"+postfix)*
		process.pfMetPFnoPU*
		process.pfJetMETcorr*
		process.pfType1CorrectedMet*
		process.pfType1CorrectedPFMet
		)

    # The skimmer is in the endpath because then the results of all preceding paths
    # are available. This is used to access the outcome of filters that ran.
    #
process.ACSkimAnalysis.filterlist = cms.vstring()
addScrapingFilter( process )


if not isData:
	addKinematicsFilter( process )

process.ACSkimAnalysis.filters.AllFilters.paths = process.ACSkimAnalysis.filterlist
process.ACSkimAnalysis.filters.AllFilters.process = process.name_()    
    
process.e = cms.EndPath( process.ACSkimAnalysis )
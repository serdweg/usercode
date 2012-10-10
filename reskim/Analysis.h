#ifndef analyis_h
#define analyis_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1.h>
#include <TH2.h>
#include <TLorentzVector.h>

#include <algorithm>
#include <iostream>
#include <vector>
#include <set>
#include <map>

#include "TreeContent.h"

using namespace std;

class Analysis : public TreeContent {
protected:
  TTree &   fInputTree;
  TTree &   fOutputTree;

public:
  Analysis(TTree & inputTree, TTree & outputTree);
  void Loop();

protected:
  void SetBranchAddresses();
  Bool_t Notify();
  void CreateHistograms();
  void CreateHisto(const char * name, const char * title, 
		   Int_t nbinsx, Double_t xlow, Double_t xup);
  void CreateHisto(const char * name, const char * title, 
		   Int_t nbinsx, Double_t xlow, Double_t xup, 
		   Int_t nbinsy, Double_t ylow, Double_t yup);
  void Fill(const char * name, double value);
  void Fill(const char * name, double x, double y);

  // histogram store
  TH1F * h_counters;
  map<string, TH1D * > histo;
  map<string, TH2D * > histo2;
};

#endif
######################################################################
# quite generic Makefile for ROOT-based programs with automatic
# dependency scanning
#
# (C) Martin Weber 2011

# Name of the executable
PROGRAM       = RunSusy

# external includes / libraries
#CLHEP_VERSION = 2.0.2.1

CMSSW_RELEASE_BASE_NOPATCH:=$(shell echo $(CMSSW_RELEASE_BASE) | sed -e 's/-patch//' -e 's/_patch.//')
CMSSW_INC:=-I$(CMSSW_RELEASE_BASE)/src -I$(CMSSW_BASE)/src
CMSSW_LIBS:=-L$(CMSSW_BASE)/lib/$(SCRAM_ARCH) -L$(CMSSW_RELEASE_BASE)/lib/$(SCRAM_ARCH) -L$(CMSSW_RELEASE_BASE)/external/$(SCRAM_ARCH)/lib -L$(CMSSW_RELEASE_BASE_NOPATCH)/lib/$(SCRAM_ARCH)
 
 
EXTLIBS     = $(CMSSW_LIBS) -lCondFormatsJetMETObjects 
EXTINCDIR   = $(CMSSW_INC)
#EXTINCDIR     = -I/usr/local/include/ # external header files should be here, leading slash is mandatory!
#EXTLIBS       = -L/usr/local/lib -lCLHEP-Matrix-$(CLHEP_VERSION) -lCLHEP-Vector-$(CLHEP_VERSION)

######################################################################
# You should not modify the lines below here
#

# Setup for ROOT libraries
ROOTCFLAGS   := $(shell root-config --cflags)
ROOTLIBS     := $(shell root-config --libs)
ROOTGLIBS    := $(shell root-config --glibs)
ROOTGLIBS   += -lX3d

# Linux with gcc / g++ / g77
FC            = g77
FCFLAGS       = -I/cern/pro/include -fPIC -fno-automatic -fdollar-ok -fno-backslash \
		-finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz
# -pg for gprof

CXX           = g++
CXXFLAGS      = -O2 -Wall -fPIC -fsignaling-nans -g # -DNDEBUG # -pg for gprof
CXXFLAGS     += $(EXTINCDIR)   # external header files should be here
CXXFLAGS     += $(ROOTCFLAGS)

LD            = g++
LDFLAGS       = -O2 -fsignaling-nans -g 
LDFLAGS      += $(ROOTGLIBS)
LDFLAGS      += $(EXTLIBS)

SOURCES       = $(wildcard *.cpp)
HEADERS       = $(SOURCES:.cpp=.h)
OBJECTS       = $(SOURCES:.cpp=.o)
DEPENDS       = $(SOURCES:.cpp=.d)

DICT	      = Dict
SO	      = lib$(PROGRAM).so

DATE	     := $(shell date "+%F")

######################################################################
# default targets

all:            $(PROGRAM)

clean:
		@rm -f $(OBJECTS) $(PROGRAM) $(DICT).* $(DEPENDS)

distclean:      clean
		@rm -f *~ core *.def *.exp *.root *.ps .def gmon.out

tarball:
		tar cvjf $(PROGRAM)-$(DATE).tar.bz2 Makefile *.h *.cpp

install:	$(PROGRAM)
		cp -a $(SO) $(LIBDIR)

uninstall:
		test -x $(LIBDIR)/$(SO) && rm $(LIBDIR)/$(SO)

######################################################################
# rules

.SUFFIXES: .cpp .$(ExeSrcSuf) .C .f .o .so .d

.cpp.o:
	$(CXX) $(CXXFLAGS) -c $<

.cxx.o:
	$(CXX) $(CXXFLAGS) -c $<

.C.o:
	$(CXX) $(CXXFLAGS) -c $<

.f.o:
	$(FC) $(FCFLAGS) -c $< -o $@

.cpp.d:
	$(SHELL) -ec '$(CXX) -M $(CXXFLAGS) $< > $@'

.cxx.d:
	$(SHELL) -ec '$(CXX) -M $(CXXFLAGS) $< > $@'

include $(DEPENDS)

######################################################################
# ROOT dictionary

$(DICT).C: $(HEADERS) LinkDef.h
	@echo "Generating dictionary $(DICT)..."
	@echo rootcint -f $@ -c $(EXTINCDIR) $+
	@rootcint -f $@ -c $(EXTINCDIR) $+

######################################################################
# targets

$(PROGRAM):  $(OBJECTS) $(DICT).o
	$(LD) $(LDFLAGS) $+ -o $@
		@echo "$@ done"


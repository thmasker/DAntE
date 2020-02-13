ifdef OS
   RM = del /Q /S
   OS_SEP = \\
   CP_SEP = ;
else
   ifeq ($(shell uname), Linux)
      RM = rm -rf
	  OS_SEP = /
	  CP_SEP = :
   endif
endif

ENV = pytfg
OUT_DIR = .$(OS_SEP)out
SRC_DIR = .$(OS_SEP)src
PREPROCESSING = .$(OS_SEP)data-preprocessing
JUPYTER_DIR = .$(OS_SEP)notebook
ERROR_MSG = @echo ERROR: Check you activated the virtual environment

help:
	$(info Please use \`make <target>' where <target> is one of:)
	$(info .	nb				to start jupyter notebooks)
	$(info .	get-data		to retrieve consumptions from the database)

all: help

nb:
	jupyter notebook $(JUPYTER_DIR)

get-data:
	python $(SRC_DIR)$(PREPROCESSING)$(OS_SEP)complete_dataframe.py || $(ERROR_MSG)

output:
	$(RM) $(OUT_DIR)
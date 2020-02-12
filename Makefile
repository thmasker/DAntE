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
JUPYTER_DIR = .$(OS_SEP)notebook
ERROR_MSG = @echo ERROR: Check you activated the virtual environment

help:
	$(info Please use \`make <target>' where <target> is one of:)
	$(info .	nb				to start jupyter notebooks)

all: help

nb:
	jupyter notebook $(JUPYTER_DIR)

collection:
	python $(SRC_DIR)$(OS_SEP)collection_cleaning.py || $(ERROR_MSG)

output:
	$(RM) $(OUT_DIR)
# Makefile for pyota project
#
# Since we distribute the generated C file for simplicity (and so that end users
# won't need to install cython). You can re-create the C file using this
# Makefile.


ifndef PYTHON
    PYTHON=python
endif

%.c: %.pyx
	cython $(<D)/$(<F)

c_files = iota/crypto/kerl/conv.c

all: $(c_files)

clean:
	rm -fv $(c_files)
	rm -fv iota/crypto/kerl/*.so

fresh: clean all

.PHONY: all clean fresh
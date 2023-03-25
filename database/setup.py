# ---------- SETUP ----------
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- IMPORTS ----------
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext




ext_modules = [
    Extension("utils.dtypeFixer",  ["./utils/dtypeFixer.pyx"], language="c++"),
]

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
)
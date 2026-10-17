from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "chronosmatch.matching_engine",
        ["src/chronosmatch/matching_engine.pyx"],
    )
]

setup(
    name="chronosmatch",
    package_dir={"": "src"},
    packages=["chronosmatch"],
    ext_modules=cythonize(extensions, compiler_directives={"language_level": 3}),
)

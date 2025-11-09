from setuptools import setup, find_packages
setup(
    name='crypto',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        "gmpy2",
        "sympy",
        "secrets",
        "multiprocessing",
        "typing",
        "unittest",
    ],
)
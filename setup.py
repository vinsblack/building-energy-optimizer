from setuptools import setup, find_packages

setup(
    name="building_energy_optimizer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.19.2",
        "pandas>=1.2.0",
        "scikit-learn>=0.24.0",
        "joblib>=1.0.0"
    ],
    python_requires=">=3.8",
)
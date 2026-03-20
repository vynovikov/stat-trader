from setuptools import find_packages, setup

setup(
    name="ml_agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "umap-learn",
        "grpcio",
        "grpcio-tools",
        "python-dotenv",
        "joblib",
    ],
)

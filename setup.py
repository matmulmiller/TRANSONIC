from setuptools import setup, find_packages

setup(
    name='TRANSONIC',
    version='0.1.0',
    author='Jacob M. Miller',
    author_email='jmmill41@louisville.edu',
    description='Package for the manipulation and analysis of RTDs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JacobMillerChemE/TRANSONIC',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.2',
        'matplotlib>=3.8',
        'pyyaml>=6.0',
        'numpy>=1.26'
        ],
    entry_points={
        'console_scripts': [
            'generate_Ecurves=src.scripts.E_curves:main',
            'evaluate_model=src.scripts.model_eval:main'
        ],
    },
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',  # Minimum version requirement of the package

)
from setuptools import setup
import py2app.recipes

APP = ['run.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'flask', 'dotenv', '_cffi_backend', 'cryptography', 'pyo3',
        'chardet', 'charset_normalizer', 'requests'
    ],  # Ajoutez ici tous les modules nécessaires
    'packages': ['app'],
    'excludes': [],  # Vous pouvez exclure des modules non nécessaires
    'packages': ['requests', 'app'],  # Inclure les packages
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

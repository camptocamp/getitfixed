import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()
with open(os.path.join(here, "requirements.txt")) as f:
    REQUIRES = f.read()

setup(
    name="getitfixed",
    version=os.environ.get("VERSION", "1.0.14"),
    description="getitfixed",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="",
    author_email="",
    url="",
    keywords="web wsgi bfg pylons pyramid",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="getitfixed",
    install_requires=REQUIRES,
    entry_points="""\
        [paste.app_factory]
            main = getitfixed:main
        [console_scripts]
            initialize_getitfixed_db = getitfixed.scripts.initializedb:main
        [lingua.extractors]
            getitfixed = getitfixed.lingua_extractor:GetItFixedExtractor
        [plaster.loader_factory]
            getitfixed = getitfixed.loader:Loader
            getitfixed+ini = getitfixed.loader:Loader
            getitfixed+egg = getitfixed.loader:Loader
        [plaster.wsgi_loader_factory]
            getitfixed = getitfixed.loader:Loader
            getitfixed+ini = getitfixed.loader:Loader
            getitfixed+egg = getitfixed.loader:Loader
    """,
)

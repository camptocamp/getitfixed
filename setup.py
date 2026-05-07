import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()
with open(os.path.join(here, "requirements.txt")) as f:
    REQUIRES = f.read()

setup(
    name="getitfixed",
    version=os.environ.get("VERSION", "1.0.30"),
    description="getitfixed",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
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
    python_requires=">=3.10",
    install_requires=REQUIRES,
    entry_points="""\
        [paste.app_factory]
            main = getitfixed:main
        [console_scripts]
            getitfixed_setup_test_data = getitfixed.scripts.setup_test_data:main
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

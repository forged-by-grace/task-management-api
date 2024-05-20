import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

 
__version__ = "1.0.0"


REPO_NAME = "task-management-api"
AUTHOR_USER_NAME = "forged_by_grace"
SRC_REPO = "task-management-api"
AUTHOR_EMAIL = "nornubariconfidence@gmail.com"


setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A service that provides endpoints for retrieving data based on model name and other parameters",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "app"},
    packages=setuptools.find_packages(where="app")
)
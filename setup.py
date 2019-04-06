from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="watson_jira",
    version="0.2.0",
    description="Format and upload Watson time logs to Jira as Tempo worklogs",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Office/Business :: Scheduling",
    ],
    url="http://github.com/medwig/watson-jira",
    author="Jonathan Medwig",
    author_email="jonmedwig@gmail.com",
    license="MIT",
    packages=["watson_jira", "watson_jira.src"],
    install_requires=[
        "td-watson",
        "python-dateutil",
        "click",
        "simplejson",
        "colorama",
        "jira",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["watson-jira=watson_jira.cli:main"]},
    zip_safe=False,
    include_package_data=True,
)

"""Setup file for watson-jira distribution"""

from setuptools import setup


def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

def parse_requirements(requirements, ignore=('setuptools',)):
    """Read dependencies from requirements file (with version numbers if any)"""
    with open(requirements) as f:
        packages = set()
        for line in f:
            line = line.strip()
            if line.startswith(('#', '-r', '--')):
                continue
            if '#egg=' in line:
                line = line.split('#egg=')[1]
            pkg = line.strip()
            if pkg not in ignore:
                packages.add(pkg)
        return tuple(packages)

setup(
    name='watson_jira',
    version='0.4.0',
    description='Format and upload Watson time logs to Jira as Tempo worklogs',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Scheduling',
    ],
    url='http://github.com/medwig/watson-jira',
    author="Jonathan Medwig",
    author_email="jonmedwig@gmail.com",
    license='MIT',
    packages=['watson_jira', 'watson_jira.src'],
    python_requires='>=3.6',
    install_requires=parse_requirements('requirements.txt'),
    tests_require=parse_requirements('requirements-dev.txt'),
    entry_points={'console_scripts': ['watson-jira=watson_jira.cli:main']},
    zip_safe=False,
    include_package_data=True,
)

from setuptools import setup, find_packages
with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
TEAM_NAME = "ss_mcts"
setup(
    name=TEAM_NAME,
    version="1.0.0",
    description="MCTS blocks-duo player package",
    author=TEAM_NAME,
    packages=find_packages(),
    install_requires=install_requirements,
    entry_points={
        "console_scripts": [
            f"{TEAM_NAME}=ss_player.main:main",
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ]
)
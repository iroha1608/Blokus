from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = [line.strip() for line in f if line.strip()]

setup(
    name='mcts_client',
    version='1.0.0',
    description='Policy-guided MCTS (UCT) blocks-duo player (extracted from ai_battle_player).',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'mcts_ai=mcts_client.main:main',
        ],
    },
    classifiers=['Programming Language :: Python :: 3.8'],
)

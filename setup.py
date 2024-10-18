from setuptools import setup, find_packages

setup(
    name="wazuh-log-scripts",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here, or leave empty
    ],
    entry_points={
        'console_scripts': [
            'run-alerts=alerts_script:main',
            'run-archives=archives_script:main',
            'run-termination=termination_script:main'
        ]
    }
)


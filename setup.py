from setuptools import setup, find_packages

setup(
    name='logging_setup',
    version='0.1.0',
    description='Simple logging module that logs to console and SQLite',
    author='R. Kyle Norris',
    author_email='r.kyle.norris@gmail.com',
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
    ],
    include_package_data=True,
    zip_safe=False,
)

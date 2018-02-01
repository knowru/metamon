from setuptools import setup

setup(name='metamon',
    version='0.1',
    description='Procuce metadata for your data',
    url='http://github.com/knowru/metamon',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    keywords='metadata,descriptive analytics',
    url='https://github.com/knowru/metamon/',
    author='Ken Park',
    author_email='spark@example.com',
    license='MIT',
    packages=['metamon'],
    install_requires=[
        'numpy'
    ],
    include_package_data=True,
    zip_safe=False
)
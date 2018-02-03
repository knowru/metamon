from setuptools import setup

setup(name='metamon',
    version='0.1.1',
    description='Procuce metadata for your data',
    url='http://github.com/knowru/metamon',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    keywords='metadata, descriptive analytics',
    author='Ken Park',
    author_email='spark@example.com',
    license='MIT',
    packages=['metamon'],
    install_requires=[
        'coverage==4.4.2',
        'nose2==0.7.3',
        'numpy==1.14.0',
        'scipy==1.0.0',
        'six==1.11.0'
    ],
    include_package_data=True,
    zip_safe=False,
    tests_require=['nose2']
)
import os
import sys
from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

tests_require = [
    'pytest',
]


setup(
    name='anticipate',
    packages=['anticipate'],
    package_data={'': ['LICENSE']},
    package_dir={'anticipate': 'anticipate'},
    version=open('VERSION.txt').read().strip(),
    author='Mike Thornton',
    author_email='six8@devdetails.com',
    url='http://github.com/six8/anticipate',
    download_url='http://github.com/six8/anticipate',
    keywords=['packaging'],
    license='BSD',
    description='A type checking and adapting library',
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
    long_description=open('README.rst').read(),
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    setup_requires=['pytest-runner'] if {'pytest', 'test'}.intersection(sys.argv) else [],
    install_requires=[
        'future==0.17.1',
    ],
)

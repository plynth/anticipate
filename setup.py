from subprocess import check_call
import sys
from setuptools import setup

if sys.argv[-1] in ('build', 'publish'):
    check_call(
        # Use `which` because rst_inc does not (in 1.04) have a sh-bang
        # to execute Python automatically.
        'python `which rst_inc.py` include -s ./_README.rst -t ./README.rst', shell=True)
    check_call('python setup.py sdist bdist_wheel', shell=True)
    if sys.argv[-1] == 'publish':
        check_call('twine upload dist/*', shell=True)
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    setup_requires=['pytest-runner'] if {'pytest', 'test'}.intersection(sys.argv) else [],
    install_requires=[
        'future==0.17.1',
    ],
)

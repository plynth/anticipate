from distutils.core import setup

def main():
    setup(
        name = 'anticipate',
        packages=['anticipate'],
        package_dir = {'':'src'},
        version = open('VERSION.txt').read().strip(),
        author='Mike Thornton',
        author_email='six8@devdetails.com',
        url='http://github.com/six8/anticipate',
        download_url='http://github.com/six8/anticipate',
        keywords=['packaging'],
        license='BSD',
        description='A type checking and adapting library',
        classifiers = [
            "Programming Language :: Python",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Topic :: Software Development :: Libraries :: Python Modules",
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: BSD License',
            "Development Status :: 3 - Alpha",
        ],
        long_description=open('README.rst').read(),
    )

if __name__ == '__main__':
    main()
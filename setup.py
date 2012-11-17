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
        license='MIT',
        description='A type checking and adapting library',
        classifiers = [
            "Programming Language :: Python",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        long_description=open('README.rst').read(),
    )

if __name__ == '__main__':
    main()
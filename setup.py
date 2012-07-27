from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar-mongo',
    version=":versiontools:debug_toolbar_mongo:",
    description='MongoDB panel for the Django Debug Toolbar',
    long_description=open('README.rst').read(),
    author='Harry Marr',
    author_email='harry@hmarr.com',
    url='https://github.com/hmarr/django-debug-toolbar-mongo',
    license='MIT',
    packages=find_packages(exclude=('example', )),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'versiontools >= 1.6',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

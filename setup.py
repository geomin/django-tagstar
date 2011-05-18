from setuptools import setup, find_packages

setup(
    name='tagstar',
    version='0.6.1',
    url='http://github.com/geomin/django-tagstar',
    maintainer='Georg Kasmin',
    maintainer_email='georg@aquarianhouse.com',
    description='Fast & easy tagging for Django',
    classifiers=['License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Topic :: Global :: Countries'],
    license='BSD',
    platforms=['any'],
    install_requires=[],#pip
    packages=find_packages(),
)

from setuptools import setup, find_packages


setup(
    name="jaguar",
    version='0.0.1',
    license='MIT',
    url="http://nowhere",
    description="jaguar",
    author='Colin Alston',
    author_email='colin@imcol.in',
    packages=find_packages() + [
        "twisted.plugins",
    ],
    package_data={
        'twisted.plugins': ['twisted/plugins/jaguar_plugin.py']
    },
    include_package_data=True,
    install_requires=[
        'Twisted',
        'PyYaml',
        'RPi.GPIO',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)

from setuptools import find_packages, setup
from setuptools.command.test import test as Test


class PyTest(Test):
    def finalize_options(self):
        Test.finalize_options(self)
        self.test_args = ["tests"]
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


with open("README") as readme:
    setup(
        name = "credit-calculator",
        version = "0.1",

        description = readme.readline().strip(),
        long_description = readme.read().strip() or None,
        url = "http://github.com/KonishchevDmitry/credit-calculator",

        license = "GPL3",
        author = "Dmitry Konishchev",
        author_email = "konishchev@gmail.com",

        classifiers = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python :: 3",
        ],
        platforms = [ "unix", "linux", "osx" ],

        cmdclass = { "test": PyTest },
        tests_require = [ "pytest" ],

        install_requires = [ "object-validator", "pcli", "python-config", ],
        packages = find_packages(),

        entry_points = {
            "console_scripts": [ "credit-calculator = credit_calc.main:main" ],
        },
    )

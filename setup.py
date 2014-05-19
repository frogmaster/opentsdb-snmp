#!/usr/bin/env python
import sys

sys.path.insert(0, "misc")

from distribute_setup import use_setuptools
use_setuptools()
import setuptools

import version

setuptools.setup(
    name="opentsdb.snmp",
    version=version.get_git_version(),
    namespace_packages=["opentsdb"],
    packages=setuptools.find_packages("src"),
    package_dir={
        "": "src",
    },
    package_data={
    },
    install_requires=[
        "netsnmp-python"
    ],
    tests_require=[
        "nose>=1.0",
        "mock>=0.8."
    ],
    entry_points={
        "console_scripts": [
            "opentsdb-snmp=opentsdb.snmp.main:run"
        ],
        "resolvers": [
            "default=opentsdb.snmp.resolvers.default:Default",
            "ifname=opentsdb.snmp.resolvers.ifname:IfName",
            "direction_after_idx=opentsdb.snmp.resolvers.after_idx:AfterIndex",
            "d500_xdsl=opentsdb.snmp.resolvers.d500_xdsl:D500_xdsl",
        ],
        "value_modifiers": [
            "rate=opentsdb.snmp.value_modifiers.rate:Rate",
        ]
    },
    test_suite="nose.collector",

)

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
        ]
    },
    test_suite="nose.collector",

)

#!/usr/bin/env python
# This file is part of opentsdb-snmp.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
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
        "pyyaml"
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
            "after_idx=opentsdb.snmp.resolvers.after_idx:AfterIndex",
            "after_idx_ifname=opentsdb.snmp.resolvers.after_idx_ifname:AfterIndexIfname",
            "huawei_ifname=opentsdb.snmp.resolvers.huawei:HuaweiIfName",
            "huawei_after_idx=opentsdb.snmp.resolvers.huawei:HuaweiAfterIndex",
            "huawei_us_ds=opentsdb.snmp.resolvers.huawei:HuaweiAfterIndexUsDs",
            "huawei_ont_port=opentsdb.snmp.resolvers.huawei:HuaweiOnt",
            "d500_xdsl=opentsdb.snmp.resolvers.d500_xdsl:D500_xdsl",
            "isam_nfxsa_xdsl=opentsdb.snmp.resolvers.isam_xdsl:IsamNFXSA",
            "isam_nfxsa_card=opentsdb.snmp.resolvers.isam_xdsl:NFXSAcard",
            "isam_nfxsb_card=opentsdb.snmp.resolvers.isam_xdsl:NFXSBcard",
            "isam_nfxsa_octets=opentsdb.snmp.resolvers.isam_xdsl:IsamNFXSAOctets",
            "isam_nfxsb_xdsl=opentsdb.snmp.resolvers.isam_xdsl:IsamNFXSB",
            "isam_nfxsb_octets=opentsdb.snmp.resolvers.isam_xdsl:IsamNFXSBOctets",
            "isam_old_xdsl=opentsdb.snmp.resolvers.isam_xdsl:IsamOld",
            "isam_old_octets=opentsdb.snmp.resolvers.isam_xdsl:IsamOldOctets",
            "nec_ipaso_modem=opentsdb.snmp.resolvers.nec_paso:NECIPasoModem",
            "nec_paso_modem=opentsdb.snmp.resolvers.nec_paso:NECPasoNEOModem",
        ],
        "value_modifiers": [
            "rate=opentsdb.snmp.value_modifiers.rate:Rate",
        ]
    },
    test_suite="nose.collector",

)

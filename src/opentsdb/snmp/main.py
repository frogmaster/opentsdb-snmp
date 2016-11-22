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
import time
import multiprocessing
from pkg_resources import iter_entry_points
from opentsdb.snmp.device import Device
from opentsdb.snmp.worker import WorkerManager
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
import argparse
import logging
import traceback
import os
# DEFAULT_LOG = '/var/log/tcollector.log'
# LOG = logging.getLogger('tcollector')
parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--config", dest="conffile",
    help="Location of configuration file"
)
parser.add_argument(
    "-i", "--interval", dest="interval", default=300,
    help="One run takes at least this much seconds, default 300"
)
parser.add_argument(
    "-r", "--readers", dest="readers", default=5,
    help="Number of reader threads, default 5"
)
parser.add_argument(
    "-t", "--times", dest="times", default=-1,
    help="Number of times to loop"
)
parser.add_argument(
    "-l", "--loglevel", dest="loglevel", default="info",
    help="Log level, defaults to 'info'"
)
parser.add_argument(
    "-f", "--hostlist", dest="hostlist", default=False,
    help="Hostlist file (overrides one defined in configfile)"
)


def run():
    args = parser.parse_args()
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=numeric_level)

    if not args.conffile:
        raise SystemExit("Must specify configuration file with --config")

    app = Main(
        readers=int(args.readers),
        conf=args.conffile,
        interval=int(args.interval),
        hostlist=args.hostlist,
    )
    app.run(times=int(args.times))


class Main:
    def __init__(self, readers=5, conf=None, interval=300, hostlist=None):
        manager = multiprocessing.Manager()
        self.dev_queue = manager.Queue()
        self.cache = manager.dict()
        self.readers = readers
        self.interval = interval
        if conf:
            self.conf = ConfigReader(conf, hostlist=hostlist)
        self.resolvers = self.load_resolvers()
        self.value_modifiers = self.load_value_modifiers()

    def load_resolvers(self):
        resolvers = {}
        for entry in iter_entry_points(group="resolvers"):
            resolvers[entry.name] = entry.load()(cache=self.cache)
        return resolvers

    def load_value_modifiers(self):
        mods = {}
        for entry in iter_entry_points(group="value_modifiers"):
            mods[entry.name] = entry.load()(cache=self.cache)
        return mods

    def load_devices(self):
        self.devices = []
        metrics = self.conf.metrics()
        for d in self.conf.devicelist():
            d = Device(d, self.resolvers,
                       self.value_modifiers, metrics)
            self.devices.append(d)
        return self.devices

    def run(self, times=-1):
        wm = WorkerManager(
            self.dev_queue,
            self.resolvers,
            self.value_modifiers,
            self.cache,
            self.conf.metrics(),
            self.conf.tsd_list(),
            workers=self.readers
        )
        try:
            while(True):
                dev_list = self.conf.devicelist()
                for d in dev_list:
                    self.dev_queue.put(d)
                if (times == 0):
                    break
                start_time = time.time()
                #start workers
                wm.start()
                wm.join()
                delta = time.time() - start_time
                logging.info("Iteration took %d seconds", delta)
                if delta < self.interval:
                    time.sleep(self.interval - delta)
                if (times > 0):
                    times -= 1

        except (KeyboardInterrupt, SystemExit):
            wm.terminate()


class ConfigReader:
    def __init__(self, path, hostlist=None):
        self.path = path
        self.data = self.load_file(path)
        if hostlist:
            self.hostlist = self.load_file(hostlist)
        else:
            self.hostlist = self.load_file(self.data["hosts_file"])

    def load_file(self, path):
        with open(path) as fp:
            return load(fp, Loader=Loader)

    def devicelist(self):
        return self.hostlist

    def metrics(self):
        m = dict()
        if "metrics_dir" in self.data:
            path = self.data["metrics_dir"]
            m.update(self.load_metrics_from_dir(path))
        if "metrics" in self.data:
            m.update(self.data["metrics"])
        return m

    def load_metrics_from_dir(self, path):
        metrics = dict()
        files = [
            os.path.join(path, f) for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
            and f.endswith(".yml")
        ]
        for f in files:
            metrics.update(self.load_file(f).items())
        return metrics

    def tsd_list(self):
        tsd_list = []
        for tsd in self.data["tsd"]:
            port = 4242
            if "port" in tsd:
                port = tsd["port"]
            tsd_list.append((tsd["host"], port))
        return tsd_list




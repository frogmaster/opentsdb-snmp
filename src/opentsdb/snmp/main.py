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
from opentsdb.snmp.sender import SenderManager
import yaml
import argparse
import logging
import yappi
#DEFAULT_LOG = '/var/log/tcollector.log'
#LOG = logging.getLogger('tcollector')
logging.basicConfig(level=logging.DEBUG)
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


def run():
    args = parser.parse_args()

    if not args.conffile:
        raise SystemExit("Must specify configuration file with --config")

    app = Main(
        readers=int(args.readers),
        conf=args.conffile,
        interval=int(args.interval)
    )
    app.run(times=int(args.times))


class Main:
    def __init__(self, readers=5, conf=None, interval=300):
        manager = multiprocessing.Manager()
        self.senderq = manager.Queue()
        self.cache = manager.dict()
        self.readers = readers
        self.interval = interval
        if conf:
            self.conf = ConfigReader(conf)
        self.resolvers = self.load_resolvers()
        self.value_modifiers = self.load_value_modifiers()

    def init_senders(self):
        self.sender_manager = SenderManager(
            squeue=self.senderq,
            tsd_list=self.conf.tsd_list()
        )
        self.sender_manager.run()

    def stop_senders(self):
        self.sender_manager.stop()

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
        for d in self.conf.devicelist():
            d = Device(d, self.resolvers,
                       self.value_modifiers, self.conf.metrics())
            self.devices.append(d)
        return self.devices

    def run(self, times=-1):
        yappi.start()
        self.load_devices()
        self.init_senders()
        try:
            while(True):
                if (times == 0):
                    break
                start_time = time.time()
                pool = multiprocessing.Pool(self.readers)
                """fill reader queue"""
                pool.map(
                    r_worker,
                    [(dev, self.senderq) for dev in self.devices]
                )
                pool.close()
                pool.join()
                delta = time.time() - start_time
                if delta < self.interval:
                    time.sleep(self.interval - delta)
                if (times > 0):
                    times -= 1
        except (KeyboardInterrupt, SystemExit):
            self.stop_senders()
        self.stop_senders()
        yappi.get_func_stats().save("/home/master/netsnmp.pstat", type="pstat")


class ConfigReader:
    def __init__(self, path):
        self.path = path
        self.data = self.load_file(path)
        self.hostlist = self.load_file(self.data["hosts_file"])

    def load_file(self, path):
        with open(path) as fp:
            return yaml.load(fp)

    def devicelist(self):
        return self.hostlist

    def metrics(self):
        return self.data["metrics"]

    def tsd_list(self):
        tsd_list = []
        for tsd in self.data["tsd"]:
            port = 4242
            if "port" in tsd:
                port = tsd["port"]
            tsd_list.append((tsd["host"], port))
        return tsd_list


def r_worker(args):
    device = args[0]
    send_queue = args[1]
    data = device.poll()
    for row in data:
        send_queue.put(row)

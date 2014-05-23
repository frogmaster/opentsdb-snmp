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
from Queue import Queue, Empty
import time
import threading
from pkg_resources import iter_entry_points
from opentsdb.snmp.device import Device
from opentsdb.snmp.sender import SenderManager
import yaml
import sys
import argparse

#DEFAULT_LOG = '/var/log/tcollector.log'
#LOG = logging.getLogger('tcollector')

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


def run():
    args = parser.parse_args()

    if not args.conffile:
        raise SystemExit("Must specify configuration file with --config")

    app = Main(
        readers=args.readers,
        conf=args.conffile,
        interval=args.interval
    )
    app.run()


class Main:
    def __init__(self, readers=5, conf=None, interval=300):
        self.readerq = Queue()
        self.pool = []
        self.senderq = Queue()
        self.readers = readers
        self.interval = interval
        if conf:
            self.conf = ConfigReader(conf)
        self.resolvers = self.load_resolvers()
        self.value_modifiers = self.load_value_modifiers()

    def init_readers(self):
        for i in range(0, self.readers):
            readth = ReaderThread(self.readerq, self.senderq)
            readth.start()
            self.pool.append(readth)

    def init_senders(self):
        self.sender_manger = SenderManager(
            squeue=self.senderq,
            tsd_list=self.conf.tsd_list
        )

    def load_resolvers(self):
        resolvers = {}
        for entry in iter_entry_points(group="resolvers"):
            resolvers[entry.name] = entry.load()()
        return resolvers

    def load_value_modifiers(self):
        mods = {}
        for entry in iter_entry_points(group="value_modifiers"):
            mods[entry.name] = entry.load()()
        return mods

    def load_devices(self):
        self.devices = []
        for d in self.conf.devicelist():
            d = Device(d, self.resolvers,
                       self.value_modifiers, self.conf.metrics())
            self.devices.append(d)
        return self.devices

    def run(self, once=False):
        self.init_senders()
        self.init_readers()
        self.load_devices()
        while(True):
            start_time = time.time()
            """fill reader queue"""
            for d in self.devices:
                self.readerq.put(d)
            self.readerq.join()
            delta = time.time() - start_time
            if delta < self.interval:
                time.sleep(self.interval - delta)
            if (once):
                break


class ConfigReader:
    def __init__(self, path):
        self.path = path
        self.data = self.load_file(path)
        self.hostlist = self.load_file(self.data["hosts_file"])
        self.load_tsd_list()

    def load_file(self, path):
        with open(path) as fp:
            return yaml.load(fp)

    def devicelist(self):
        return self.hostlist

    def metrics(self):
        return self.data["metrics"]

    def load_tsd_list(self):
        self.tsd_list = []
        for tsd in self.data["tsd"]:
            port = 4242
            if "port" in tsd:
                port = tsd["port"]
            self.tsd_list.append((tsd["host"], port))
        return self.tsd_list


class ReaderThread(threading.Thread):
    def __init__(self, rqueue, squeue):
        super(ReaderThread, self).__init__()
        self.rqueue = rqueue
        self.squeue = squeue
        self._stop = False

    def run(self):
        while self._stop is False:
            try:
                device = self.rqueue.get_nowait()
                if device:
                    self.rqueue.task_done()
                data = device.poll()
                for row in data:
                    self.squeue.put(row)
            except Empty:
                time.sleep(0.3)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            finally:
                next
        return

    def stop(self):
        self._stop = True

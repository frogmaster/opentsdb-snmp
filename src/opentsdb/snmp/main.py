from Queue import Queue, Empty
from time import sleep
import threading
from opentsdb.snmp.device import Device
from opentsdb.snmp.sender import SenderManager
import json
import sys

#DEFAULT_LOG = '/var/log/tcollector.log'
#LOG = logging.getLogger('tcollector')


class Main:
    def __init__(self, readers=5, host_list="hosts.json"):
        self.readerq = Queue()
        self.senderq = Queue()
        self.readers = readers
        self.conf = ConfigReader(host_list)
        self.sender_manger = SenderManager(squeue=self.senderq, tsd_list=self.conf.tsd_list)

    def init_readers(self):
        self.pool = []
        for i in range(0, self.readers):
            readth = ReaderThread(self.readerq, self.senderq)
            readth.start()
            self.pool.append(readth)

    def run(self, once):
        self.init_readers()
        devices = self.conf.devices
        while(True):
            """fill reader queue"""
            for d in devices:
                self.readerq.put(d)
            self.readerq.join()
            if (once):
                break


class ConfigReader:
    def __init__(self, path):
        self.path = path
        self.data = self.load_file(path)
        self.load_devices()
        self.load_tsd_list()

    def load_file(self, path):
        with open(path) as fp:
            return json.load(fp)

    def load_devices(self):
        self.devices = []
        for d in self.data["devices"]:
            self.devices.append(Device(d))
        return self.devices

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
                sleep(0.3)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            finally:
                next
        return

    def stop(self):
        self._stop = True

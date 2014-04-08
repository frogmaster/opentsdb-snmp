from Queue import Queue, Empty
from time import sleep
import threading
from opentsdb.snmp.device import Device
from opentsdb.snmp.sender import SenderThread
import json
import sys

#DEFAULT_LOG = '/var/log/tcollector.log'
#LOG = logging.getLogger('tcollector')


class Main:
    def __init__(self, readers=5, host_list="hosts.json"):
        self.readerq = Queue()
        self.senderq = Queue()
        self.readers = readers
        self.host_list = host_list
        self.pool = []
        self.sender = SenderThread(self.senderq)

    def init_readers(self):
        for i in range(1, self.readers):
            readq = ReaderThread(self.readerq, self.senderq)
            readq.start()
            self.pool.append(readq)

    def run(self):
        self.init_readers()
        hlr = ConfigReader(self.host_list)
        devices = hlr.load_devices()
        while(True):
            """fill reader queue"""
            for d in devices:
                self.readerq.put(d)
            self.readerq.join()


class ConfigReader:
    def __init__(self, path):
        self.path = path
        self.devices = []

    def load_file(self):
        with open(self.path) as fp:
            return json.load(fp)

    def load_devices(self):
        data = self.load_devices()
        for d in data["devices"]:
            self.devices.append(Device(d))
        return self.devices


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

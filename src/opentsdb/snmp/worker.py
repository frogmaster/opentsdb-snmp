from multiprocessing import Process
from opentsdb.snmp.device import Device
from opentsdb.snmp.sender import Sender


class WorkerManager(object):
    def __init__(self,
                 dev_queue, resolvers,
                 value_modifiers, cache,
                 metrics, tsd_list, workers=5
                 ):
        self.queue = dev_queue
        self.resolvers = resolvers
        self.value_modifiers = value_modifiers
        self.cache = cache
        self.metrics = metrics
        self.tsd_list = tsd_list
        self.wks = []
        self.wcount = workers

    def init_workers(self):
        self.wks = []
        for i in range(0, self.wcount):
            w = Worker(
                self.queue,
                self.resolvers,
                self.value_modifiers,
                self.cache,
                self.metrics,
                self.tsd_list,
            )
            self.wks.append(w)

    def start(self):
        self.init_workers()
        for w in self.wks:
            w.start()

    def join(self):
        for w in self.wks:
            w.join()

    def terminate(self):
        for w in self.wks:
            w.terminate()


class Worker(Process):
    def __init__(self,
                 dev_queue, resolvers,
                 value_modifiers, cache,
                 metrics, tsd_list
                 ):
        super(Worker, self).__init__()
        self.dev_queue = dev_queue
        self.resolvers = resolvers
        self.value_modifiers = value_modifiers
        self.cache = cache
        self.metrics = metrics
        self.sender = Sender(tsd_list)

    def init_device(self, data):
        device = Device(data,
                        self.resolvers,
                        self.value_modifiers,
                        self.metrics)
        return device

    def work(self, data):
        device = self.init_device(data)
        lines = device.poll()
        self.sender.send(lines)

    def readq(self):
        while True:
            try:
                data = self.dev_queue.get(True, 1)
                self.work(data)
            except Exception:
                break

    def run(self):
        self.readq()

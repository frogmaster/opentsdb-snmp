from Queue import Queue
from opentsdb.snmp.main import Main
from opentsdb.snmp.worker import WorkerManager
from nose.tools import eq_
from mock import Mock, patch


class TestWorkers(object):
    def setup(self):
        self.deviceelem = {
            'hostname': 'foobar',
            'community': 'public',
            'snmp_version': 2,
            'metrics': ["ifInUcastPkts"]
        }
        main = Main(conf="misc/sample_conf.yml")
        main.load_resolvers()
        self.dev_queue = Queue()
        self.wm = WorkerManager(
            self.dev_queue,
            main.resolvers,
            main.value_modifiers,
            main.cache,
            main.conf.metrics(),
            main.conf.tsd_list(),
            workers=1
        )
        self.wm.init_workers()

    def test_init_workers(self):
        eq_(1, len(self.wm.wks))

    def test_worker_init_device(self):
        w = self.wm.wks[0]
        dev = w.init_device(self.deviceelem)
        eq_("foobar", dev.hostname)

    @patch('opentsdb.snmp.worker.Device')
    def test_worker_readq(self, mockdevice):
        self.dev_queue.put(self.deviceelem)
        mockdevice.return_value = MockDevice(['foo', 'bar'])
        w = self.wm.wks[0]
        w.sender = Mock()
        w.sender.send = Mock()
        w.readq()
        w.sender.send.assert_called_with(['foo', 'bar'])


class MockDevice(object):
    def __init__(self, arr):
        self.arr = arr

    def poll(self):
        return self.arr

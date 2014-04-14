from nose.tools import eq_, ok_
import opentsdb.snmp.main as app
from mock import Mock
from Queue import Queue


class TestConfigReader(object):
    def setup(self):
        self.hlr = app.ConfigReader("misc/sample_data.json")

    def test_load_file(self):
        loaded_data = self.hlr.load_file(self.hlr.path)
        ok_("devices" in loaded_data)

    def test_load_devices(self):
        devices = self.hlr.load_devices()
        eq_("foobar", devices[0].hostname)

    def test_load_tsd_list(self):
        tsd_list = self.hlr.load_tsd_list()
        ok_(tsd_list[0], ('localhost', 5431))
        ok_(tsd_list[1], ('localhost', 4242))


class TestReaderThread(object):
    def setup(self):
        self.rq = Queue()
        self.sq = Queue()
        self.rthread = app.ReaderThread(rqueue=self.rq, squeue=self.sq)
        self.rthread.start()
        self.mockdevice = Mock()
        self.mockdevice.poll = Mock(return_value=["foo bar"])

    def test_readerthread(self):
        """put stuff in rqueue"""
        self.rq.put(self.mockdevice)
        """wait for queue to join:"""
        self.rq.join()
        data = self.sq.get()
        eq_(data, "foo bar")
        self.rthread.stop()
        self.rthread.join()

class TestMain(object):
    def setup(self):
        self.mainobj = app.Main(readers=1, host_list="misc/sample_data.json")

    def test_init_readers(self):
        self.mainobj.init_readers()
        eq_(1, len(self.mainobj.pool))
        self.mainobj.pool[0].stop()
        self.mainobj.pool = []

    def test_run(self):
        self.mainobj.conf.devices[0] = Mock()
        self.mainobj.conf.devices[0].poll = Mock(return_value=[])
        self.mainobj.run(True)

    def teardown(self):
        for i in self.mainobj.pool:
            i.stop()
        self.mainobj.sender_manger.stop()


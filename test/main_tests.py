from nose.tools import eq_, ok_
import opentsdb.snmp.main as app
from mock import Mock
from Queue import Queue


class TestConfigReader(object):
    def setup(self):
        self.hlr = app.ConfigReader("misc/sample_conf.json")

    def test_load_file(self):
        loaded_data = self.hlr.load_file(self.hlr.path)
        ok_("metrics" in loaded_data)
        ok_("hosts_file" in loaded_data)

    def test_devicelist(self):
        devices = self.hlr.devicelist()
        eq_("foobar", devices[0]["hostname"])

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
        self.mainobj = app.Main(readers=1, host_list="misc/sample_conf.json")

    def test_init_readers(self):
        self.mainobj.init_readers()
        eq_(1, len(self.mainobj.pool))
        self.mainobj.pool[0].stop()
        self.mainobj.pool = []

    def test_run(self):
        self.mainobj.load_devices()
        # load_devices is called in run method,
        # so devices get's overwritten unless mocked
        self.mainobj.load_devices = Mock()

        self.mainobj.devices[0] = Mock()
        self.mainobj.devices[0].poll = Mock(return_value=[])
        self.mainobj.run(True)
        for i in self.mainobj.pool:
            i.stop()

    def test_init_senders(self):
        self.mainobj.init_senders()
        self.mainobj.sender_manger.stop()

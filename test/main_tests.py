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
from nose.tools import eq_, ok_
import opentsdb.snmp.main as app
import time
from mock import Mock, patch
from Queue import Queue


class TestConfigReader(object):
    def setup(self):
        self.hlr = app.ConfigReader("misc/sample_conf.yml")

    def test_load_file(self):
        loaded_data = self.hlr.load_file(self.hlr.path)
        ok_("metrics" in loaded_data)
        ok_("hosts_file" in loaded_data)

    def test_devicelist(self):
        devices = self.hlr.devicelist()
        eq_("foobar", devices[0]["hostname"])

    def test_tsd_list(self):
        tsd_list = self.hlr.tsd_list()
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
        self.mainobj = app.Main(
            readers=1,
            conf="misc/sample_conf.yml",
            interval=2
        )

    def test_init_readers(self):
        self.mainobj.init_readers()
        eq_(1, len(self.mainobj.pool))
        self.mainobj.pool[0].stop()
        self.mainobj.pool = []

    @patch('opentsdb.snmp.sender.SenderManager.run')
    @patch('opentsdb.snmp.sender.SenderThread.connect')
    def test_run(self, mock1, mock2):
        self.mainobj.load_devices()
        # load_devices is called in run method,
        # so devices get's overwritten unless mocked
        self.mainobj.load_devices = Mock()
        self.mainobj.devices[0] = Mock()
        self.mainobj.devices[0].poll = Mock(return_value=[])

        cur_time = time.time()
        self.mainobj.run(True)
        delta = time.time() - cur_time
        ok_(delta >= 2, "Sleep if we took less than interval")
        self.mainobj.sender_manager.stop()

    def test_init_senders(self):
        self.mainobj.init_senders()
        self.mainobj.sender_manager.stop()

#!/usr/bin/python3

import visa
import time


class VisaConnection(object):
    def __init__(self, resource_name, tmo=20000):

        self._rm = None
        self._conn = None

        # try default backend
        if self.resource_manager() or self.resource_manager('/usr/lib/librsvisa.so') or self.resource_manager('@py'):
            self.open_resource(resource_name, tmo)
        else:
            raise Exception('Can not Open resource, please check py-visa backend')

    def resource_manager(self, backend=""):
        try:
            self._rm = visa.ResourceManager(backend)
            return self._rm

        except OSError:
            return None
        except ValueError:
            return None

    def open_resource(self, name, tmo):
        if self._rm:
            self._conn = self._rm.open_resource(name)
            self._conn.timeout = tmo

    def write(self, msg, termination=None):
        self._conn.write(msg, termination)

    def read(self):
        return self._conn.read()

    def query(self, msg):
        return self._conn.query(msg)

    def error(self):
        err = self.query('SYST:ERR?')
        if err.lower().find('no error') == -1:
            print(err)
            raise Exception(err)


def bb_wlnn_gen_file(_conn, _file):
    _conn.write(':SOURce1:BB:WLNN:STATe 1')
    _conn.error()
    _conn.query('*OPC?')
    _conn.write(':SOURce1:BB:WLNN:WAVeform:CREate "D:/%s.wv"' % _file)
    _conn.write('*WAI')
    _conn.query('*OPC?')
    _conn.write(':SOURce1:BB:WLNN:STATe 0')


def wlan_n_waveform(_conn):
    _conn.write(':SOURce1:BB:WLNN:PRESet')
    for bw in ['BW20', 'BW40']:
        _conn.write(':SOURce1:BB:WLNN:BWidth %s' % bw)
        _conn.write(':SOURce1:BB:WLNN:FBLock1:STANdard WN')

        for phy_mode in ['MIX', 'GFI']:
            _conn.write(':SOURce1:BB:WLNN:FBLock1:PMODe %s' % phy_mode)

            for mcs in range(0, 7+1):
                _conn.write(':SOURce1:BB:WLNN:FBLock1:MCS MCS%d' % mcs)
                bb_wlnn_gen_file(_conn, 'WLAN_N_%s_%s_MCS%d' % (bw, phy_mode, mcs))


def wlan_ac_waveform(_conn):
    _conn.write(':SOURce1:BB:WLNN:PRESet')
    for bw in ['BW20', 'BW40', 'BW80', 'BW160']:

        _conn.write(':SOURce1:BB:WLNN:BWidth %s' % bw)
        _conn.write(':SOURce1:BB:WLNN:FBLock1:STANdard WAC')

        for mcs in range(0, 11 + 1):
            _conn.write(':SOURce1:BB:WLNN:FBLock1:MCS MCS%d' % mcs)
            bb_wlnn_gen_file(_conn, 'WLAN_AC_%s_MCS%d' % (bw, mcs))


def wlan_ax_waveform(_conn):
    _conn.write(':SOURce1:BB:WLNN:PRESet')
    for bw in [20, 40, 80, 160]:

        _conn.write(':SOURce1:BB:WLNN:BWidth BW%d' % bw)
        _conn.write(':SOURce1:BB:WLNN:FBLock1:STANdard WAX')
        _conn.write(':SOURce1:BB:WLNN:FBLock1:TMODe HE%d' % bw)
        _conn.write(':SOURce1:BB:WLNN:FBLock1:LINK UP')

        for mcs in range(0, 11 + 1):
            _conn.write(':SOURce1:BB:WLNN:FBLock1:USER1:MCS MCS%d' % mcs)
            bb_wlnn_gen_file(_conn, 'WLAN_AX_%s_HESU_MCS%d' % (bw, mcs))


def bb_wlan_gen_file(_conn, _name):
    _conn.write(':SOURce1:BB:WLAN:STATe 1')
    while True:
        time.sleep(1)
        if int(_conn.query(':SOURce1:BB:WLAN:STATe?')) != 1:
            time.sleep(1)
        else:
            break
    conn.error()
    _conn.write(':SOURce1:BB:WLAN:WAVeform:CREate "D:/%s.wv"' % _name)
    _conn.write('*WAI')
    _conn.query('*OPC?')
    _conn.write(':SOURce1:BB:WLAN:STATe 0')
    _conn.query('*OPC?')


def wlan_g_waveform(_conn):
    _conn.write(':SOURce1:BB:WLAN:PRESet')
    _conn.write(':SOURce1:BB:WLAN:STANdard STAN80211G')

    # CCK
    _conn.write(':SOURce1:BB:WLAN:MODE CCK')
    _conn.write(':SOURce1:BB:WLAN:PLCP:FORMat SHOR')
    for rate in ['2MBPS', '5.5MBPS', '11MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 256')
        bb_wlan_gen_file(_conn, 'WLAN_G_CCK_SHORT_%s' % rate)

    _conn.write(':SOURce1:BB:WLAN:PLCP:FORMat LONG')
    for rate in ['1MBPS', '2MBPS', '5.5MBPS', '11MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 256')
        bb_wlan_gen_file(_conn, 'WLAN_G_CCK_LONG_%s' % rate)

    # PBCC
    _conn.write(':SOURce1:BB:WLAN:MODE PBCC')
    _conn.write(':SOURce1:BB:WLAN:PLCP:FORMat SHOR')
    for rate in ['2MBPS', '5.5MBPS', '11MBPS', '22MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 256')
        bb_wlan_gen_file(_conn, 'WLAN_G_PBCC_SHORT_%s' % rate)

    _conn.write(':SOURce1:BB:WLAN:PLCP:FORMat LONG')
    for rate in ['1MBPS', '2MBPS', '5.5MBPS', '11MBPS', '22MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 256')
        bb_wlan_gen_file(_conn, 'WLAN_G_PBCC_LONG_%s' % rate)

    # OFDM
    _conn.write(':SOURce1:BB:WLAN:MODE OFDM')
    for rate in ['6MBPS', '9MBPS', '12MBPS', '18MBPS', '24MBPS', '36MBPS', '48MBPS', '54MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 512')
        bb_wlan_gen_file(_conn, 'WLAN_G_OFDM_%s' % rate)


def wlan_a_waveform(_conn):
    _conn.write(':SOURce1:BB:WLAN:PRESet')
    _conn.write(':SOURce1:BB:WLAN:STANdard STAN80211A')

    for rate in ['6MBPS', '9MBPS', '12MBPS', '18MBPS', '24MBPS', '36MBPS', '48MBPS', '54MBPS']:
        _conn.write(':SOURce1:BB:WLAN:PSDU:BRATe %s' % rate)
        _conn.write(':SOURce1:BB:WLAN:PSDU:DLENgth 1024')
        bb_wlan_gen_file(_conn, 'WLAN_A_OFDM_%s' % rate)


if __name__ == '__main__':
    conn = VisaConnection('tcpip::localhost::inst')
    idn = conn.query('*IDN?')
    if idn.find('WinIQSIM2') == -1:
        print(idn)
        raise Exception('Unspported')

    conn.write('*RST;*CLS')
    conn.query('*OPC?')

    conn.write(':INSTruments:CLEar')
    conn.write(':INSTruments:NAME "DummyCMW100"')
    conn.write(':INSTruments:TYPE CMW100K06')
    conn.write(':INSTruments:SELect:ARB 1')
    conn.error()

    wlan_n_waveform(conn)
    wlan_ac_waveform(conn)
    wlan_ax_waveform(conn)
    wlan_g_waveform(conn)
    wlan_a_waveform(conn)

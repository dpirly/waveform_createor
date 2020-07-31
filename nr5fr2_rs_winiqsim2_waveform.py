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


def ul_waveforms(_conn):
    _conn.write(':SOURce1:BB:NR5G:PRESet')
    _conn.write(':SOURce1:BB:NR5G:LINK UP')
    _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:CARDeply GT6')
    for PhaseCompensation in ['OFF', 'ON']:
        _conn.write(':SOURce1:BB:NR5G:NODE:RFPHase:STATe %s' % PhaseCompensation)
        for DmrsTypeAPos in [2, 3]:
            _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:TAPos %d' % DmrsTypeAPos)
            for CellID in [0, 1, 2, 3, 1006, 1007]:
                _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:CELLid %d' % CellID)
                for Bandwidth in [50, 100, 200, 400]:
                    _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:CBW BW%d' % Bandwidth)
                    for SCS in [60, 120]:
                        RbMaxTable = {
                            'SCS60': {'BW50': 66, 'BW100': 132, 'BW200': 264, 'BW400': -1},
                            'SCS120': {'BW50': 32, 'BW100': 66, 'BW200': 132, 'BW400': 264}
                        }
                        RbMax = RbMaxTable['SCS%d' % SCS]['BW%d' % Bandwidth]
                        if RbMax > 0:
                            _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:TXBW:S%dK:USE 1' % SCS)

                            if SCS == 60:
                                _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:TXBW:S120K:USE 0')
                            elif SCS == 120:
                                _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:TXBW:S60K:USE 0')

                            _conn.write(':SOURce1:BB:NR5G:NODE:CELL0:TXBW:RESolve')

                            _conn.write(':SOURce1:BB:NR5G:UBWP:USER0:CELL0:UL:BWP0:RBNumber %d' % RbMax)
                            for RbNum in range(1, RbMax+1):
                                _conn.write(':SOURce1:BB:NR5G:SCHed:CELL0:SUBF0:USER0:BWPart0:NALLoc 1')
                                _conn.write(':SOURce1:BB:NR5G:SCHed:CELL0:SUBF0:USER0:BWPart0:ALLoc0:REPetitions OFF')
                                for Modulation in ['QPSK', 'QAM16', 'QAM64']:
                                    _conn.write(':SOURce1:BB:NR5G:SCHed:CELL0:SUBF0:USER0:BWPart0:ALLoc0:MOD %s' % Modulation)

                                    _conn.write(':SOURce1:BB:NR5G:SCHed:CELL0:SUBF0:USER0:BWPart0:ALLoc0:RBOFfset 0')
                                    _conn.write(':SOURce1:BB:NR5G:SCHed:CELL0:SUBF0:USER0:BWPart0:ALLoc0:RBNumber %d' % RbNum)
                                    file = 'NR5FR2_UL_BW%d_PC%s_TAP%d_CID%d_SCS%dK_RB%d_%s' % \
                                           (Bandwidth, PhaseCompensation, DmrsTypeAPos, CellID, SCS, RbNum, Modulation)
                                    print(file)
                                    _conn.error()


if __name__ == '__main__':
    conn = VisaConnection('tcpip::localhost::inst')
    idn = conn.query('*IDN?')
    if idn.find('WinIQSIM2') == -1:
        print(idn)
        raise Exception('Unspported')

    conn.write('*RST;*CLS')
    conn.query('*OPC?')

    conn.write(':INSTruments:CLEar')
    conn.write(':INSTruments:SELect:ARB 0')
    conn.error()

    ul_waveforms(conn)

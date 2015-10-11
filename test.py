#!/usr/bin/env python3

import serial
import io;

###############################################################################

class Channel:
    def __init__(self, device, setChar, getChar):
        self._device = device
        self._setChar = setChar
        self._getChar = getChar
    
    ###########################################################################
    
    def _get_cmd(self, char):
        return self._getChar + char
    
    def _set_cmd(self, char):
        return self._setChar + char
    
    ###########################################################################
    
    def set_frequency(self, freqInHz):
        self._device.writeCmd('%s%09d' % (self._set_cmd('f'), freqInHz * 100))
    
    def set_amplitude(self, ampl):
        self._device.writeCmd('%s%02.2f' % (self._set_cmd('a'), ampl))
    
    def set_offset(self, offset):
        self._device.writeCmd('%s%02.1f' % (self._set_cmd('o'), offset))

###############################################################################

class FY3200S:
    _debug_mode = False
    
    def __init__(self, device = '/dev/ttyUSB0'):
        self._serial = serial.Serial(device, 9600, timeout=1)
        self._serialIO = io.TextIOWrapper(io.BufferedRWPair(self._serial, self._serial), newline='')
        
        self._channels = [
            Channel(self, 'b', 'c'),
            Channel(self, 'd', '')
        ]
    
    def __del__(self):
        if self.is_open():
            self.close()
    
    def __getitem__(self, key):
        return self._channels[key]
    
    @property
    def channels(self):
        return self._channels;
    
    def close(self):
        self._serial.close()
        del self._serialIO
        del self._serial
    
    def set_debug_mode(self, enable):
        self._debug_mode = enable
    
    def is_open(self):
        return hasattr(self, '_serial') and self._serial is not None
    
    def write(self, data):
        if self._debug_mode:
            print('[send] ' + data.rstrip())
        self._serialIO.write(data)
        self._serialIO.flush()
    
    def writeCmd(self, cmd):
        self.write(cmd + '\n')
    
    def readResult(self):
        result = self._serialIO.readline().rstrip()
        
        if self._debug_mode:
            print('[recv] ' + result)
        
        return result
    
    ###########################################################################
    
    def get_device_id(self):
        self.writeCmd('a')
        return self.readResult()

###############################################################################

funcGen = FY3200S()
funcGen.set_debug_mode(True)

print(funcGen.get_device_id())
funcGen[0].set_frequency(5000)
funcGen.channels[0].set_amplitude(2.5)
funcGen[0].set_offset(0)

funcGen.close()

#!/usr/bin/env python3

import serial
import io
from enum import IntEnum

###############################################################################

class Waveform(IntEnum):
    sine = 0
    square = 1
    triangle = 2
    arb1 = 3
    arb2 = 4
    arb3 = 5
    arb4 = 6
    lorentz_pulse = 7
    multi_tone = 8
    random_noise = 9
    ecg = 10
    trapezoidal_pulse = 11
    sinc_pulse = 12
    narrow_pulse = 13
    white_noise = 14
    am = 15
    fm = 16

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
    
    def set_waveform(self, waveform):
        self._device.writeCmd('%s%d' %  (self._set_cmd('w'), int(waveform)))
    
    def set_duty_cycle(self, duty):
        self._device.writeCmd('%s%03d' % (self._set_cmd('d'), int(duty * 10)))

###############################################################################

class FY3200S:
    def __init__(self, device = '/dev/ttyUSB0'):
        self._debug_mode = False
        
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
    
    @property
    def debug_mode(self):
        return self._debug_mode
    
    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value
    
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

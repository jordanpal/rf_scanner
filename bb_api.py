# -*- coding: utf-8 -*-

from ctypes import *
import numpy
from scipy.signal import get_window
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#import seaborn as sns; sns.set() # styling

#Windows
#bblib = cdll.bb_api

#Linux?
#bblib = CDLL("/ligo/home/jordan.palamos/bb60c/libbb_api.so.3.0.16")
bblib = CDLL("libbb_api.so")

BB_TRUE = 1
BB_FALSE = 0

BB_MIN_AND_MAX = 0  
BB_AVERAGE = 1

BB_NO_SPUR_REJECT = 0     
BB_SPUR_REJECT = 1     

BB_LOG_SCALE = 0
BB_LIN_SCALE = 1
BB_LOG_FULL_SCALE = 2
BB_LIN_FULL_SCALE = 3

BB_RBW_SHAPE_NUTTALL = 0
BB_RBW_SHAPE_FLATTOP = 1
BB_RBW_SHAPE_CISPR = 2

BB_AUTO_ATTEN = c_double(-1.0)
BB_AUTO_GAIN = -1

BB_LOG = 0 
BB_VOLTAGE = 1
BB_POWER = 2
BB_SAMPLE = 3

BB_IDLE = -1
BB_SWEEPING = 0      
BB_STREAMING = 4

BB_STREAM_IQ = 0
BB_STREAM_IF = 1
BB_DIRECT_RF = 2 # BB60C only
BB_TIME_STAMP = 10


# ----------------------- Internal Mappings to C API ----------------------- #
bbOpenDeviceBySerialNumber = bblib.bbOpenDeviceBySerialNumber
bbOpenDevice = bblib.bbOpenDevice
bbCloseDevice = bblib.bbCloseDevice
bbConfigureAcquisition = bblib.bbConfigureAcquisition
bbConfigureCenterSpan = bblib.bbConfigureCenterSpan
bbConfigureLevel = bblib.bbConfigureLevel
bbConfigureGain = bblib.bbConfigureGain
bbConfigureSweepCoupling = bblib.bbConfigureSweepCoupling
bbConfigureProcUnits = bblib.bbConfigureProcUnits
bbConfigureIO = bblib.bbConfigureIO
bbConfigureDemod = bblib.bbConfigureDemod
bbConfigureIQ = bblib.bbConfigureIQ
bbConfigureRealTime = bblib.bbConfigureRealTime
bbInitiate = bblib.bbInitiate
bbFetchTrace_32f = bblib.bbFetchTrace_32f
bbFetchTrace_32f.argtypes = [c_int, c_int, 
                             numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'), 
                             numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C')]
bbFetchTrace = bblib.bbFetchTrace
bbFetchTrace.argtypes = [c_int, c_int, 
                         numpy.ctypeslib.ndpointer(numpy.float64, ndim=1, flags='C'), 
                         numpy.ctypeslib.ndpointer(numpy.float64, ndim=1, flags='C')]
#bbGetIQUnpacked = bblib.bbGetIQUnpacked
#bbGetIQUnpacked.argtypes = [c_int, numpy.ctypeslib.ndpointer(numpy.complex64, ndim=1, flags='C'), 
#                            c_int, POINTER(c_int), c_int, c_int, POINTER(c_int), 
#                            POINTER(c_int), POINTER(c_int), POINTER(c_int)]
bbQueryTraceInfo = bblib.bbQueryTraceInfo
bbQueryStreamInfo = bblib.bbQueryStreamInfo
bbAbort = bblib.bbAbort
bbPreset = bblib.bbPreset
bbSelfCal = bblib.bbSelfCal
bbSyncCPUtoGPS = bblib.bbSyncCPUtoGPS
bbGetDeviceType = bblib.bbGetDeviceType
bbGetSerialNumber = bblib.bbGetSerialNumber
bbGetFirmwareVersion = bblib.bbGetFirmwareVersion
bbGetDeviceDiagnostics = bblib.bbGetDeviceDiagnostics
bbGetAPIVersion = bblib.bbGetAPIVersion
bbGetAPIVersion.restype = c_char_p
bbGetProductID = bblib.bbGetProductID
bbGetProductID.restype = c_char_p
bbGetErrorString = bblib.bbGetErrorString
bbGetErrorString.restype = c_char_p


# --------------------------------- Utility --------------------------------- #  
def print_status(handle, status):
    error_string = bbGetErrorString(status)
    print("id:\t", handle)
    print("status:\t", status)
    print(error_string)
    
def print_status_if_error(handle, status, function):
    if(status != 0):
        print ("\n", function)
        print_status(handle, status)        


# --------------------------------- Public --------------------------------- #  
def bb_open_device_by_serial_number(serial_number):
    handle = c_int(-1)    
    status = bbOpenDeviceBySerialNumber(byref(handle), serial_number)
    print_status_if_error(handle, status, "bbOpenDeviceBySerialNumber")
    return handle.value, status

def bb_open_device():
    handle = c_int(-1)    
    status = bbOpenDevice(byref(handle))
    print_status_if_error(handle, status, "bbOpenDevice")
    return handle.value, status

def bb_close_device(handle):
    status = bbCloseDevice(handle)
    print_status_if_error(handle, status, "bbCloseDevice")
    return status

def bb_configure_acquisition(handle, detector, scale):
    status = bbConfigureAcquisition(handle, detector, scale)
    print_status_if_error(handle, status, "bbConfigureAcquisition")
    return status

def bb_configure_center_span(handle, center, span):
    status = bbConfigureCenterSpan(handle, c_double(center), c_double(span))
    print_status_if_error(handle, status, "bbConfigureCenterSpan")
    return status

def bb_configure_level(handle, ref, atten):
    status = bbConfigureLevel(handle, c_double(ref), atten)
    print_status_if_error(handle, status, "bbConfigureLevel")
    return status

def bb_configure_gain(handle, gain):
    status = bbConfigureGain(handle, gain)
    print_status_if_error(handle, status, "bbConfigureGain")
    return status

def bb_configure_sweep_coupling(handle, rbw, vbw, sweep_time, rbw_shape, rejection):
    status = bbConfigureSweepCoupling(handle, c_double(rbw), c_double(vbw), 
                                      c_double(sweep_time), rbw_shape, rejection)
    print_status_if_error(handle, status, "bbConfigureSweepCoupling")
    return status

def bb_configure_proc_units(handle, units):
    status = bbConfigureProcUnits(handle, units)
    print_status_if_error(handle, status, "bbConfigureProcUnits")
    return status

def bb_configure_IO(handle, port1, port2):
    status = bbConfigureIO(handle, port1, port2)
    print_status_if_error(handle, status, "bbConfigureIO")
    return status

def bb_configure_demod(handle, modulation_type, freq, IFBW, audio_low_pass_freq, 
                       audio_high_pass_freq, FM_deemphasis):
    status = bbConfigureDemod(handle, modulation_type, c_double(freq), 
                              c_float(IFBW), c_float(audio_low_pass_freq), 
                              c_float(audio_high_pass_freq), c_float(FM_deemphasis))    
    print_status_if_error(handle, status, "bbConfigureDemod")
    return status

def bb_configure_IQ(handle, downsample_factor, bandwidth):
    status = bbConfigureIQ(handle, downsample_factor, c_double(bandwidth))   
    print_status_if_error(handle, status, "bbConfigureIQ")
    return status

def bb_initiate(handle, mode, flag):
    status = bbInitiate(handle, mode, flag)
    print_status_if_error(handle, status, "bbInitiate")
    return status
    
def bb_fetch_trace_32f(handle, sweep_size):
    min_vals = numpy.zeros(sweep_size).astype(numpy.float32) 
    max_vals = numpy.zeros(sweep_size).astype(numpy.float32)     
    status = bbFetchTrace_32f(handle, sweep_size, min_vals, max_vals)
    print_status_if_error(handle, status, "bbFetchTrace_32f")
    return min_vals, max_vals, status  

def bb_fetch_trace(handle, sweep_size):
    min_vals = numpy.zeros(sweep_size).astype(numpy.float64) 
    max_vals = numpy.zeros(sweep_size).astype(numpy.float64)     
    status = bbFetchTrace(handle, sweep_size, min_vals, max_vals)
    print_status_if_error(handle, status, "bbFetchTrace")
    return min_vals, max_vals, status    

'''
def bb_get_IQ(handle, iq_count, purge):        
    iq_data = numpy.zeros(iq_count).astype(numpy.complex64)   
    triggers = c_int(0)         
    trigger_count = c_int(0)
    data_remaining = c_int(0) 
    sample_loss = c_int(0) 
    sec = c_int(0) 
    nano = c_int(0) 
    status = bbGetIQUnpacked(handle, iq_data, iq_count, 
                             byref(triggers), trigger_count, purge, 
                             byref(data_remaining), byref(sample_loss), 
                             byref(sec), byref(nano));
    print_status_if_error(handle, status, "bbGetIQUnpacked")
    return iq_data, data_remaining, sample_loss, sec, nano, status
'''

def bb_query_trace_info(handle):    
    sweep_size = c_int(0)
    bin_size = c_double(0)
    start_freq = c_double(0)
    status = bbQueryTraceInfo(handle, byref(sweep_size), 
                              byref(bin_size), byref(start_freq))
    print_status_if_error(handle, status, "bbQueryTraceInfo")
    return sweep_size.value, bin_size.value, start_freq.value, status

def bb_query_stream_info(handle):    
    return_len = c_int(0)
    bandwidth = c_double(0)
    samples_per_sec = c_int(0)
    status = bbQueryStreamInfo(handle, byref(return_len), 
                               byref(bandwidth), byref(samples_per_sec))
    print_status_if_error(handle, status, "bbQueryStreamInfo")
    return return_len.value, bandwidth.value, samples_per_sec.value, status

def bb_abort(handle):
    status = bbAbort(handle)
    print_status_if_error(handle, status, "bbAbort")
    return status

def bb_preset(handle):
    status = bbPreset()
    print_status_if_error(handle, status, "bbPreset")
    return status

def bb_self_cal(handle):
    status = bbSelfCal()
    print_status_if_error(handle, status, "bbSelfCal")
    return status

def bb_sync_CPU_to_GPS(handle, com_port, baud_rate):
    status = bbSyncCPUtoGPS(com_port, baud_rate)
    print_status_if_error(handle, status, "bbSyncCPUtoGPS")
    return status

def bb_get_device_type(handle):
    dev_type = c_int(0)
    status = bbGetDeviceType(handle, byref(dev_type))
    print_status_if_error(handle, status, "bbGetDeviceType")
    return dev_type.value, status

def bb_get_serial_number(handle):
    sid = c_int(0)
    status = bbGetSerialNumber(handle, byref(sid))
    print_status_if_error(handle, status, "bbGetSerialNumber")
    return sid.value, status

def bb_get_firmware_version(handle):
    version = c_int(0)
    status = bbGetFirmwareVersion(handle, byref(version))
    print_status_if_error(handle, status, "bbGetFirmwareVersion")
    return version.value, status

def bb_get_device_diagnostics(handle):
    temperature = c_float(0)
    usb_voltage = c_float(0)
    usb_current = c_float(0)
    status = bbGetDeviceDiagnostics(handle, byref(temperature), 
                                    byref(usb_voltage), byref(usb_current))
    print_status_if_error(handle, status, "bbGetDeviceDiagnostics")
    return temperature.value, usb_voltage.value, usb_current.value, status

def bb_get_API_version():
    return bbGetAPIVersion()

def bb_get_product_ID():
    return bbGetProductID()

def bb_get_error_string(status):
    return bbGetErrorString(status)

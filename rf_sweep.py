#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script saves continous RF scans

from bb_api import *
import time
import datetime
import thread
import sys

def configureDevice():
    # Open device
    handle, status = bb_open_device()

    # Configure device
    bb_configure_acquisition(handle, BB_MIN_AND_MAX, BB_LOG_SCALE)
#   bb_configure_center_span(handle, 1.0e9, 100.0e6)
    bb_configure_center_span(handle, 5.000045e8, 9.99991e8)
#   bb_configure_center_span(handle, 5.135e5, 1.009e6)
    bb_configure_level(handle, -30.0, BB_AUTO_ATTEN)
    bb_configure_gain(handle, BB_AUTO_GAIN)
#   bb_configure_sweep_coupling(handle, 10.0e3, 10.0e3, 0.001, BB_RBW_SHAPE_FLATTOP, BB_NO_SPUR_REJECT)
    bb_configure_sweep_coupling(handle, 100.0e3, 100.0e3, 0.1, BB_RBW_SHAPE_FLATTOP, BB_NO_SPUR_REJECT)
#   bb_configure_sweep_coupling(handle, 10.0e3, 10.0e3, 0.01, BB_RBW_SHAPE_FLATTOP, BB_NO_SPUR_REJECT)
    bb_configure_proc_units(handle, BB_POWER)

    # Initialize
    bb_initiate(handle, BB_SWEEPING, 0)
    return handle

def getSweep(handle,sweep_size):
    # Get sweep
    t0 = time.time()
    #min_vals, max_vals, status = bb_fetch_trace(handle, sweep_size)
    min_vals, max_vals, status = bb_fetch_trace_32f(handle, sweep_size)
    t1 = time.time()
    unix_time = (t1+t0)/2
    gps_time = unixToGPS(unix_time)
    #Device no longer needed, close it
    #bb_close_device(handle)
    return gps_time, max_vals

def initalizeSweep(handle):
    sweep_size, bin_size, start_freq, status = bb_query_trace_info(handle)
    return sweep_size, bin_size, start_freq, status

def timedSweep10m(device_handle):
    #this function saves rf sweeps from when it is called
    #until the next minute divisible by 10
    #for example, if called at 13:00:00 will record sweeps until 13:10:00
    #sweeps are saved in a numpy array and the sweeps are saved along with
    #time and device info in a .npz file named after the start time in utc.
    sweep_size, bin_size, start_freq, status = bb_query_trace_info(device_handle)
    #if status != 0:
    device_info = [sweep_size,bin_size,start_freq]
    start_time = datetime.datetime.utcnow()
    current_time = start_time
    #hardcoded arrary size approx 10 mins of data.
    arr_size = 5000
    rf_data = numpy.zeros((arr_size,sweep_size))
    time = numpy.zeros(arr_size)
    i=0
    while start_time.minute/10 == current_time.minute/10:
        try:
            time[i], rf_data[i,:] = getSweep(handle,sweep_size)
            i=i+1
            time.sleep(0.01)
            if i%100 == 0:
                print "recieved 100 sweeps"
        except:
            if rf_data[-1,0] != 0:
                print "error getting sweep possibly due to exceeding array size"
                print "adding 1000 rows"
                new_rows = numpy.zeros(1000,sweep_size)
                time = numpy.append(time,numpy.zeros(1000))
                rf_data = numpy.append(rf_data,new_rows)
            elif bb_query_trace_info(device_handle)[2] != 0:
                print "error receiving sweep...reinitializing device"
                device_handle = configureDevice()
                sweep_size, bin_size, start_freq, status = bb_query_trace_info(device_handle)
        current_time = datetime.datetime.utcnow()
    bb_close_device(device_handle)
    print "saving data..."
    #get rid of zeros in array
    nodata = numpy.nonzero(time==0)
    time = numpy.delete(time,nodata)
    rf_data = numpy.delete(rf_data,nodata,axis=0)
    print rf_data.shape
    file_name = "/opt/signalhound/data/%s%02d%02d_%02d%02d.npz" % (start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute)
    #numpy.savez(file_name,device_info,time,rf_data)
    numpy.savez_compressed(file_name,device_info,time,rf_data)
    print "saved rf_data: %s" % file_name
    return device_info, time, rf_data, file_name

def loadRFDataFromNPZ(filehandle):
    #this function loads rf sweep data from .npz files
    #as saved in the timedsweep10m function
    with open(filehandle,'r') as f:
    #load the saved numpy array
    #should be dict with arr_0::sweepparams arr_1::time arr_2::vals
        rf_data = np.load(f)
        #separate time and amplitude data
        #and delete all rows of zeros
        device_info = rf_data['arr_0']
        time = rf_data['arr_1']
        vals = rf_data['arr_2']
        nodata = np.nonzero(time == 0)
        time = np.delete(time,nodata)
        vals = np.delete(vals,nodata,axis=0)
    return device_info, time, vals

def plotRFSpectrogram(sweep_size,start_freq,bin_size,filename,time,amplitudes):
    #this function plots a spectrogram of the rf sweep data
    print "plotting spectrogram..."
    freqs = [start_freq + i * bin_size for i in range(sweep_size)]
    plt.pcolormesh(freqs,time,amplitudes)
    plt.ylabel('time')
    plt.xlabel('frequency')
    plt.savefig(filename)
    print "saved spectrogram: %s"%filename
    return

def continuous_sweep_write(device_handle):
    #this function continuously writes sweeps to an open file
    #instead of saving sweeps in a large 2d array and writing
    #to disk all at once
    sweep_size, bin_size, start_freq, status = bb_query_trace_info(device_handle)
    start_time = datetime.datetime.now()
    file_name = "%s%s%s_%s.txt" % (start_time.year, start_time.month, start_time.day, start_time.hour)
    file_path = "/opt/signalhound/data/"
    current_time = start_time
    with open(file_path+file_name, 'w') as outfile:
        while current_time.hour == start_time.hour:
            time,rf_data = getSweep(device_handle,sweep_size)
            outfile.write('%s %s\n' % (time, ' '.join(str(x) for x in rf_data)))
            current_time = datetime.datetime.now()
    return

def unixToGPS(unix_time):
    return unix_time-315964800

if __name__ == "__main__":
    try:
        sys.argv[1]
    except:
        handle = configureDevice()
    else:
        handle = int(sys.argv[1])
    #arg2 = sys.argv[2]
    #handle = configureDevice()
    #while True:
        #handle = configureDevice()
        #continuous_sweep_write(handle)
        #timedSweep10m(handle)
    print 'Using device %s' % handle
    device_info, time, vals, file_name = timedSweep10m(handle)
    file_name_png = file_name.replace(".npz",".png")
    plotRFSpectrogram(device_info[0],device_info[2],device_info[1],file_name_png,time,vals)



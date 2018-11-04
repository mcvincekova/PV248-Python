from numpy import fft, abs
import wave
import sys
import struct


def unpack_data(parameter, current_frame):

	frame = struct.unpack(parameter*"h", current_frame)
	# decide if stereo or mono
	if parameter == 2:
		return float((frame[0] + frame[1]) / 2)
	else:
		return float(frame[0])


def read_data(filename, channels_num):

	current_frame = filename.readframes(1)

	unpacked_data = []
	# Read all frames (reads frames while possible, no None value)
	while current_frame:
		unpacked = unpack_data(channels_num, current_frame)
		unpacked_data.append(unpacked)
		current_frame = filename.readframes(1)

	return unpacked_data


def get_fourier(data, window, position):
	# select interval
	pos_from = position * window
	pos_to = (position + 1) * window
	data_to_transform = data[pos_from:pos_to]

	return fft.rfft(data_to_transform)


def get_peaks(peaks):

	if len(peaks) != 0:
		return min(peaks), max(peaks)
	return None, None


def run():
	f = wave.open(sys.argv[1], "rb")
	# get channels -> 1 for mono 2 for stereo
	channels = f.getnchannels()

	data = read_data(f, channels)

	# get number of frames
	frames_num = f.getnframes()
	# get sampling frequency
	window = f.getframerate()

	peak_min = None
	peak_max = None

	for i in range(frames_num // window):
		transform = get_fourier(data, window, i)

		amplitudes = []
		for item in transform:
			amplitudes.append(abs(item))

		avg_amplitude = sum(amplitudes) / len(amplitudes)

		peaks = []
		for j, amplitude in enumerate(amplitudes):
			if amplitude >= 20 * avg_amplitude:
				peaks.append(j)

		current_peaks = get_peaks(peaks)
		if peak_min is None or peak_min > current_peaks[0]:
			peak_min = current_peaks[0]
		if peak_max is None or peak_max < current_peaks[1]:
			peak_max = current_peaks[1]

	if peak_min is not None and peak_max is not None:
		print("low = " + str(peak_min) + ", high = " + str(peak_max))
	else:
		print("no peaks")


run()

#!/usrbin/env python3
import os
os.chdir('/home/pi/Shazam4Nature-master-3/pi_main')
import json
import requests
import webrtcvad
import numpy as np
from queue import Queue
from math import asin, pi
from threading import Thread
from datetime import datetime
from mic_array import MicArray
from scipy.stats import pearsonr
from deltasigma import calculateSNR
from recognition.bird_recognition import recognition, loadModel
import adafruit_ina219
import board
import busio
import time

RATE = 16000
CHANNELS = 4
WINDOW_DURATION = 200  # ms
FRAME_DURATION = 20  # ms
AUDIO_DURATION = 10000  # ms / 10 seconds
AUDIO_LENGTH = int(AUDIO_DURATION / FRAME_DURATION)
WINDOW_LENGTH = int(WINDOW_DURATION / FRAME_DURATION)
FRAME_SIZE = int(RATE * (FRAME_DURATION / 1000))
SOUND_SPEED = 343.2
MIC_DISTANCE_4 = 0.08127
MAX_TDOA_4 = MIC_DISTANCE_4 / float(SOUND_SPEED)
MIC_GROUP_N = 2
MIC_GROUP = [[0, 2], [1, 3]]
SD = 15  # degrees
POSITION = np.array([50.6788, 7.1619])  # position [Latitude (N), Longitude(E)]. maybe nneds more places after decimal?
FILENAME = '/home/pi/Shazam4Nature-master-3/pi_main/bird_data/data_'
URL = 'http://rest-s4n.azurewebsites.net'
VAD = webrtcvad.Vad(3)
INTERVAL = 3  # *10 seconds, interval between server requests
i2c = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c)
global count


def classify(audio, model):
    audio_new = audio.astype('float')
    audio_new = audio_new / 32768.
    temp = recognition(audio_new, model)
    classification = []
    for i in range(len(temp)):
        classification.append({"bird_id": i, "probability": temp[i]})
    print(classification)
    return classification


def detect(audio):
    """
    Detect if there are sounds that resemble bird activity
    :param audio: 1xN mono audio data
    :return: true if there is some activity, false otherwise
    """
    frame_counter = 0
    voice_counter = 0
    for i in range(AUDIO_LENGTH):
        frame_counter += 1
        if is_bird_present(audio[i * FRAME_SIZE: (i + 1) * FRAME_SIZE]):
            voice_counter += 1
        if frame_counter == WINDOW_LENGTH:
            if voice_counter > int(WINDOW_LENGTH / 2):
                return True  # return true after 1 detection
            frame_counter = 0
            voice_counter = 0
    return False


def is_bird_present(frame):
    """
    Determine if there is some voice activity in the sound frame
    :param frame: 1xM mono audio data of the sound frame
    :return: true if there is some activity, false otherwise
    """
    if VAD.is_speech(frame.tobytes(), RATE):
        return True
    return False


def direction_for_window(audio):
    tau = [0] * MIC_GROUP_N
    theta = [0] * MIC_GROUP_N
    for i, v in enumerate(MIC_GROUP):
        tau[i] = pearson_corr(audio[v[0], :], audio[v[1], :])
        if tau[i] > MAX_TDOA_4:
            tau[i] = MAX_TDOA_4
        if tau[i] < -MAX_TDOA_4:
            tau[i] = -MAX_TDOA_4
        theta[i] = asin(tau[i] / MAX_TDOA_4) * 180 / pi
    angle = get_angle(theta)
    return angle


def estimate_direction(audio):
    """
    Determine the TDoA for each microphone pair(tau) and determine the DoA
    :param audio: 4xN numpy array with audio data
    :return: DoA estimate for the given audio
    """
    frame_counter = 0
    voice_counter = 0
    directions = dict()
    result = ""
    for i in range(AUDIO_LENGTH):
        frame_counter += 1
        if is_bird_present(audio[0, i * FRAME_SIZE: (i + 1) * FRAME_SIZE]):
            voice_counter += 1
            result += "1"
        else:
            result += "0"
        if frame_counter == WINDOW_LENGTH:
            if voice_counter > int(WINDOW_LENGTH / 2):
                doa = direction_for_window(audio[:, (i - WINDOW_LENGTH + 1) * FRAME_SIZE: (i + 1) * FRAME_SIZE])
                result = result + "    Direction: " + str(doa)
                directions[doa] = directions.get(doa, 0) + 1
            frame_counter = 0
            voice_counter = 0
            print(result)
            result = ""
    # return the most frequent DoA
    try:
        res = sorted(directions.items(), key=lambda kv: kv[1]).pop()
        print(res)
        return res[0]
    except IndexError as e:
            x = open('/home/pi/Desktop/errors.txt', 'a')
            x.write(str(e))
            x.write("\n")
            x.close() 	


def pearson_corr(sig1, sig2):
    """
    Calculate the shift and subsequently the tau using Pearson correlation
    :param sig1: audio signal from one microphone
    :param sig2: audio signal from the second microphone
    :return: time difference of arrival, tau
    """
    max_corr = -1.
    max_k = None
    for k in range(-4, 5):
        corr, p = pearsonr(sig1, np.roll(sig2, k))
        if corr > max_corr:
            max_corr = corr
            max_k = k

    return max_k / RATE


def get_angle(theta):
    """
    Given theta values, determine direction of arrival of the sound
    :param theta: 2x1 theta array
    :return: direction of arrival estimation
    """
    best_guess = None
    if np.abs(theta[0]) < np.abs(theta[1]):
        if theta[1] > 0:
            best_guess = (theta[0] + 360) % 360
        else:
            best_guess = (180 - theta[0])
    else:
        if theta[0] < 0:
            best_guess = (theta[1] + 360) % 360
        else:
            best_guess = (180 - theta[1])
        best_guess = (best_guess + 90 + 180) % 360
    best_guess = (-best_guess + 120) % 360

    return best_guess


def jsonify(doa, power, snr, classification):
    """
    Write the DoA, signal power, SNR and Classification result to a json file
    that sends the information to the cloud
    :param doa: DoA in degrees
    :param power: intensity of signal
    :param snr: list of SNR values for four Channels
    :param classification: class of the species and probabilities of classification
    :return:
    """
    global count
    current_array = np.array([])
    voltage_array = np.array([])
    for i in range(100):
        current_array = np.append(current_array ,[ina219.current])
        voltage_array = np.append(voltage_array, [ina219.bus_voltage])
    solar_current = np.mean(current_array)
    solar_voltage = np.mean(voltage_array)
    measurements = [{
        'angle': doa,
        'deviation': SD,
        'sig_pow': power,
        'snr': snr,
    }]

    data = {
        'pi_id': 2,
        'timestamp': str(datetime.utcnow()),
        'position': np.array2string(POSITION, separator=','),
        'solar_current': solar_current,
        'solar_voltage': solar_voltage,
        'measurements': measurements,
        'classifications': classification
    }
    try:
        if os.path.isfile(FILENAME + str(count) + ".json"):
            with open(FILENAME + str(count) + ".json", 'r+') as f:
                data_from_file = json.load(f)
                data_from_file.append(data)
                f.seek(0)
                json.dump(data_from_file, f, indent=4)
        else:
            with open(FILENAME + str(count) + ".json", 'w+') as f:
                json.dump([data], f, indent=4)
    except json.decoder.JSONDecodeError as e:
            x = open('/home/pi/Desktop/errors.txt', 'a')
            x.write(str(e))
            x.write("\n")
            x.close() 	
        

def transform(audio):
    """
    Transform 1-dimensional audio data into 2-dimensional 4xN matrix
    :param audio: 1-dimensional numpy array representing the audio from microphone
    :return: 2-dimensional 4xN numpy matrix
    """
    return np.vstack((audio[0::4], audio[1::4], audio[2::4], audio[3::4]))


def get_signal_snr(audio):
    """
    Calculate SNR of the signal per channel
    :param audio: 2-dimensional 1xN numpy matrix
    :return: SNR as float
    """
    N = audio.shape[1]
    # using a hann window
    win = np.hanning(N)
    audio = audio * win
    c = np.fft.fft(audio)
    return calculateSNR(c, 0)


def dbfft(x, ref=1):
    """
    Calculate spectrum in dB scale
    Args:
    :param x: input signal
    :param s: sampling frequency
    :param ref: reference value used for dBFS scale. 32768 for int16 and 1 for float

    Returns: s_db: power in dB scale
    """
    # Calculate real FFT and frequency vector
    N = x.shape[1]
    # using a hann window
    win = np.hanning(N)
    x = x * win
    sp = np.fft.rfft(x)
    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)
    # Convert to dBFS
    s_dbfs = 20 * np.log10(s_mag / ref)
    return s_dbfs


def get_signal_properties(audio):
    """
    returns the RMS power and SNR of the audio
    :param audio: 2-dimensional 4xN numpy matrix
    :return: RMS power as float and SNR as string
    """
    rms_per_channel = []
    snr = []
    for i in range(CHANNELS):
        rms_per_channel.append(dbfft(audio[i::CHANNELS]))
        snr.append(float('{:.4f}'.format(get_signal_snr(audio[i::CHANNELS]))))
    return np.max(rms_per_channel), ''.join(str(snr))


def record(q):
    """
    Records an audio file of the length specified by AUDIO_DURATION
    :param q: queue to put the recorded audio in
    """
    chunks = []
    with MicArray(RATE, CHANNELS, RATE * FRAME_DURATION / 1000) as mic:
        for chunk in mic.read_chunks():
            chunks.append(chunk)
            if len(chunks) == AUDIO_LENGTH:
                audio = np.concatenate(chunks)
                q.put(audio)
                chunks = []


def send_report():
    """
    Send collected data from json file specified by FILENAME
    :return:
    """
    try:
        # read the file
        with open(FILENAME, 'r') as json_file:
        # load json file into a string
            data = json.dumps(json.load(json_file))	
    except json.decoder.JSONDecodeError as e:
        print("Loading json file into a string")
        data = "Error"
	
    try:
        response = requests.post(url=URL + '/api/v1/data', data=data, headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            print("POST successful")
            os.remove(FILENAME)
        else:
            print("Unexpected response status code: " + str(response.status_code))
            print(response.text)
    except requests.exceptions.Timeout:
        print("Failed to connect to the server (connection timeout)")
    except requests.exceptions.ConnectionError:
        print("Failed to establish connection")


def main():
	print("Bird Voice Detection Started...")
	global count
	count = 0
	model = loadModel()
	audio_queue = Queue()
	# start audio recording in a background thread
	recording_thread = Thread(target=record, args=(audio_queue,))
	recording_thread.setDaemon(True)
	recording_thread.start()
	send_counter = 0
	while True:
		for i in range(500):
			#send_counter += 1
			audio = audio_queue.get()
			audio = transform(audio)
			detection = detect(audio[0, :])
			if detection:
				classification = classify(audio[0, :], model)
				doa = estimate_direction(audio)
				power, snr = get_signal_properties(audio)
				jsonify(doa, power, snr, classification)
            # send reports with 30-second intervals
           # if send_counter > INTERVAL:
               # send_report()
            #    send_counter = 0
			else:
				print("No activity detected")
		#global count
		count += 1

if __name__ == '__main__':
    main()

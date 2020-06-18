# ==================================================
# wave class
import struct
class wave_file:
    def __init__(self, file_path):
        f = open(file_path, "rb")
        self.chunkID        = f.read(4).decode('utf-8')                     #'RIFF'                         4B
        self.chunkSize      = struct.unpack('<i', f.read(4))[0]             #36+subchunk2size               4B
        self.format         = f.read(4).decode('utf-8')                     #'wave'                         4B
        self.subChunkID     = f.read(4).decode('utf-8')                     #'fmt'                          4B
        self.subChunkSize   = struct.unpack('<i', f.read(4))[0]             #16 for PCM                     4B
        self.audioFormat    = struct.unpack('<h', f.read(2))[0]             #PCM=1                          2B
        self.numChannels    = struct.unpack('<h', f.read(2))[0]             #1=Mono, 2=Stereo               2B
        self.sampleRate     = struct.unpack('<i', f.read(4))[0]             #44100 for leopard              4B
        self.ByteRate       = struct.unpack('<i', f.read(4))[0]             #sampleR*channels*(byte/sample) 4B
        self.BlockAlign     = struct.unpack('<h', f.read(2))[0]             # numBytes/sample               2B
        self.BitsPerSample  = struct.unpack('<h', f.read(2))[0]             # 8/16/etc                      2B
        self.subChunk2ID    = f.read(4).decode('utf-8')                     #'data'                         4B
        self.subChunk2Size  = struct.unpack('<i', f.read(4))[0]             #numsamples*channels*byt/sample 4B
        self.data_raw       = struct.unpack(str(int(self.subChunk2Size/self.BlockAlign))+'h', f.read(self.subChunk2Size))     #pretty but we're assuming always 16 BitsPerSample, prob not goood
        self.data_norm      = [float(i)/2**15 for i in self.data_raw]       #normalize data
        f.close()
#==================================================
# UI
import base64                           #to encode plot so we can pass directly to PySimpleGUI
import PySimpleGUI as sg                #to avoid touching tkinter directly
import matplotlib.pyplot as plt         #to actually plot our data
import io                               #to avoid saving graphs to disk
from os import path                     #to verify file exists
sg.theme('DarkAmber')
window = sg.Window('WaveForm Visualizer', 
            [[sg.Input(), sg.FileBrowse()],
            [sg.Button('OK'), sg.Button('Cancel')],
            [sg.Image(r'blank_graph.png', key='_IMAGE_')]
            ])
while True:             
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event == 'OK':   
        wav_path = values[0]
        if (len(wav_path)!=0 and wav_path.endswith('.wav') and path.exists(wav_path)):
            new_wave_file = wave_file(wav_path) 
            plt.plot(new_wave_file.data_norm)
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read())
            window.Element('_IMAGE_').Update(data=string)
            plt.clf()
window.close()
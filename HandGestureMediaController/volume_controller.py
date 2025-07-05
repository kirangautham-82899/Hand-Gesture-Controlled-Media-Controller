from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.minVol, self.maxVol = self.volume.GetVolumeRange()[:2]

    def setVolume(self, vol_percent):
        vol = self.minVol + (vol_percent / 100) * (self.maxVol - self.minVol)
        self.volume.SetMasterVolumeLevel(vol, None)

    def getVolumeRange(self):
        return self.minVol, self.maxVol

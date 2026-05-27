from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        # Support both legacy and current pycaw APIs.
        if hasattr(devices, "Activate"):
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        else:
            self.volume = devices.EndpointVolume
        self.minVol, self.maxVol = self.volume.GetVolumeRange()[:2]
        self._last_percent = None

    def setVolume(self, vol_percent):
        vol_percent = max(0, min(100, int(vol_percent)))
        if self._last_percent == vol_percent:
            return
        vol = self.minVol + (vol_percent / 100) * (self.maxVol - self.minVol)
        self.volume.SetMasterVolumeLevel(vol, None)
        self._last_percent = vol_percent

    def getVolumeRange(self):
        return self.minVol, self.maxVol

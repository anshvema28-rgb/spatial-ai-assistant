try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission, check_permission
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

class AndroidActions:
    def __init__(self):
        self.available = ANDROID_AVAILABLE
        if self.available:
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.Intent = autoclass('android.content.Intent')
            self.Settings = autoclass('android.provider.Settings')
            self.MediaStore = autoclass('android.provider.MediaStore')
            self.AudioManager = autoclass('android.media.AudioManager')
            self.Context = autoclass('android.content.Context')

    def _start_activity(self, intent):
        if not self.available:
            return "Android APIs not available (running on desktop)"
        try:
            current_activity = self.PythonActivity.mActivity
            if current_activity:
                current_activity.startActivity(intent)
                return "Opened successfully"
            return "No activity context available"
        except Exception as e:
            return f"Failed to open: {str(e)[:50]}"

    def open_settings(self):
        if not self.available:
            return "Settings: Android only (test on device)"
        intent = self.Intent(self.Settings.ACTION_SETTINGS)
        intent.addFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
        return self._start_activity(intent)

    def open_calculator(self):
        if not self.available:
            return "Calculator: Android only (test on device)"
        intent = self.Intent(self.Intent.ACTION_MAIN)
        intent.addCategory(self.Intent.CATEGORY_APP_CALCULATOR)
        intent.addFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
        return self._start_activity(intent)

    def open_camera(self):
        if not self.available:
            return "Camera: Android only (test on device)"
        if not check_permission(Permission.CAMERA):
            request_permissions([Permission.CAMERA])
            return "Camera permission required. Please grant and try again."
        intent = self.Intent(self.MediaStore.ACTION_IMAGE_CAPTURE)
        intent.addFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
        return self._start_activity(intent)

    def open_wifi_settings(self):
        if not self.available:
            return "Wi-Fi Settings: Android only (test on device)"
        intent = self.Intent(self.Settings.ACTION_WIFI_SETTINGS)
        intent.addFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
        return self._start_activity(intent)

    def open_bluetooth_settings(self):
        if not self.available:
            return "Bluetooth Settings: Android only (test on device)"
        intent = self.Intent(self.Settings.ACTION_BLUETOOTH_SETTINGS)
        intent.addFlags(self.Intent.FLAG_ACTIVITY_NEW_TASK)
        return self._start_activity(intent)

    def volume_up(self):
        if not self.available:
            return "Volume Up: Android only (test on device)"
        try:
            activity = self.PythonActivity.mActivity
            audio_manager = activity.getSystemService(self.Context.AUDIO_SERVICE)
            audio_manager.adjustStreamVolume(
                self.AudioManager.STREAM_MUSIC,
                self.AudioManager.ADJUST_RAISE,
                self.AudioManager.FLAG_SHOW_UI
            )
            return "Volume increased"
        except Exception as e:
            return f"Volume control failed: {str(e)[:50]}"

    def volume_down(self):
        if not self.available:
            return "Volume Down: Android only (test on device)"
        try:
            activity = self.PythonActivity.mActivity
            audio_manager = activity.getSystemService(self.Context.AUDIO_SERVICE)
            audio_manager.adjustStreamVolume(
                self.AudioManager.STREAM_MUSIC,
                self.AudioManager.ADJUST_LOWER,
                self.AudioManager.FLAG_SHOW_UI
            )
            return "Volume decreased"
        except Exception as e:
            return f"Volume control failed: {str(e)[:50]}"
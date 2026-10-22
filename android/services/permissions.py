try:
    from android.permissions import request_permissions, Permission, check_permission
    ANDROID_PERMISSIONS_AVAILABLE = True
except ImportError:
    ANDROID_PERMISSIONS_AVAILABLE = False

REQUIRED_PERMISSIONS = [
    Permission.RECORD_AUDIO,
    Permission.INTERNET,
    Permission.ACCESS_NETWORK_STATE,
    Permission.CAMERA,
    Permission.MODIFY_AUDIO_SETTINGS,
    Permission.BLUETOOTH,
    Permission.BLUETOOTH_ADMIN,
]

OPTIONAL_PERMISSIONS = [
    Permission.ACCESS_FINE_LOCATION,
    Permission.ACCESS_COARSE_LOCATION,
]

def request_required_permissions(callback=None):
    if not ANDROID_PERMISSIONS_AVAILABLE:
        if callback:
            callback(True, "Not on Android")
        return True

    def _on_result(permissions, grants):
        all_granted = all(grants)
        if callback:
            callback(all_granted, "Permissions granted" if all_granted else "Some permissions denied")

    request_permissions(REQUIRED_PERMISSIONS, _on_result)
    return False

def check_required_permissions():
    if not ANDROID_PERMISSIONS_AVAILABLE:
        return True

    return all(check_permission(p) for p in REQUIRED_PERMISSIONS)

def request_camera_permission(callback=None):
    if not ANDROID_PERMISSIONS_AVAILABLE:
        if callback:
            callback(True)
        return

    def _on_result(permissions, grants):
        if callback:
            callback(grants[0] if grants else False)

    request_permissions([Permission.CAMERA], _on_result)

def request_audio_permission(callback=None):
    if not ANDROID_PERMISSIONS_AVAILABLE:
        if callback:
            callback(True)
        return

    def _on_result(permissions, grants):
        if callback:
            callback(grants[0] if grants else False)

    request_permissions([Permission.RECORD_AUDIO], _on_result)
class DomoticsService:
    """
    Service class to handle domotics data.
    """
    def __init__(self, domotic_data):
        self.domotic_data = domotic_data

    def list_available_zones(self):
        """
        Return the list of available zones.
        """
        return [info['zone'] for info in self.domotic_data.values()]
    
    def list_device_status_by_zone(self, target_zone):
        """
        Return the list of devices in a specific zone.
        """
        for zone_id, info in self.domotic_data.items():
            if info['zone'] == target_zone:
                return info['devices']
        return None

    def update_zone_status(self, target_zone, device):
        """
        Update the status of a device in a specific zone.
        """
        for zone_id, info in self.domotic_data.items():
            if info['zone'] == target_zone:
                if device in info['devices']:
                    info['devices'][device] = not info['devices'][device]
                    return info['devices']
        return None
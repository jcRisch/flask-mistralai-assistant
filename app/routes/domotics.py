from flask import render_template, Blueprint, current_app

domotics_bp = Blueprint('permissions', __name__)

@domotics_bp.route('/')
def home():
    title = "Hi there!"
    items = ['Hello', 'my', 'good', 'friends']
    return render_template('home.html', title=title, items=items)

@domotics_bp.route('/zones/<string:zone>/devices')
def get_devices_by_zone(zone):
    devices_by_zone = current_app.domotics_service.list_device_status_by_zone(zone)
    if devices_by_zone:
        return render_template('json.html', json_response=devices_by_zone)
    else:
        return render_template('json.html', json_response="No device found")

@domotics_bp.route('/zones', methods=['GET'])
def get_available_zones():
    """
    Endpoint to list available zones.
    """
    zones = current_app.domotics_service.list_available_zones()
    if zones:
        return render_template('json.html', json_response=zones)
    else:
        return render_template('json.html', json_response="No available zone found")

@domotics_bp.route('/zones/<string:zone>/devices/<string:device>/update', methods=['PATCH'])
def update_device_status(zone, device):
    """
    Endpoint to update the status of a device in a specific zone.
    """
    updated_status = current_app.domotics_service.update_zone_status(zone, device)
    if updated_status:
        return render_template('json.html', json_response=updated_status)
    else:
        return render_template('json.html', json_response="No device found")
    
#
# This plugin can be used in your projects to add functionality related to Find My Plane
# It is a simple wrapper for the Find My Plane API, the full docs of which are available at http://findmyplane.live/api
#
# Example workflow is available in example.py
#


import requests
from datetime import datetime

server_url = "https://findmyplane.live/"
api_url = server_url + "api"

connected_to_instance = False
ident_public_key = None
ident_private_key = None

last_data_sent_timestamp = 0
threshold_for_how_often_to_send_data = 1

first_datapoint = True


def set_keys(ident_public_key_to_set, ident_private_key_to_set):
    global ident_public_key
    global ident_private_key
    global connected_to_instance
    global first_datapoint
    global last_data_sent_timestamp

    ident_public_key = ident_public_key_to_set
    ident_private_key = ident_private_key_to_set
    first_datapoint = True
    last_data_sent_timestamp = 0
    connected_to_instance = True


def request_new_plane_instance(plane_title=None, atc_id=None, client=None):

    endpoint_url = "/create_new_plane"
    url = api_url + endpoint_url

    values = {'title': plane_title,
              'atc_id': atc_id,
              'client': client}

    try:
        r = requests.post(url, json=values)
        plane_object = r.json()
        set_keys(plane_object['ident_public_key'], plane_object['ident_private_key'])
    except:
        print ("Error connecting to Find My Plane")
        plane_object = {'status': 'error'}

    print ("Connected to Find My Plane: " + url_to_view())
    return {'status': 'success'}


def disconnect_from_plane_instance():
    global ident_public_key
    global ident_private_key
    global connected_to_instance
    global first_datapoint
    global last_data_sent_timestamp

    ident_public_key = None
    ident_private_key = None
    connected_to_instance = False
    first_datapoint = True
    last_data_sent_timestamp = 0


def set_plane_location(current_latitude, current_longitude, current_compass, current_altitude, current_speed=None, title=None, atc_id=None):

    if connection_status() != "connected":
        return "error: not connected"

    global last_data_sent_timestamp
    global first_datapoint

    if (datetime.now().timestamp() - last_data_sent_timestamp) < threshold_for_how_often_to_send_data:
        return "error: too soon to resend data"

    endpoint_url = "/update_plane_location"
    url = api_url + endpoint_url

    values = {'ident_public_key': ident_public_key,
              'ident_private_key': ident_private_key,
              'current_latitude': current_latitude,
              'current_longitude': current_longitude,
              'current_compass': current_compass,
              'current_altitude': current_altitude,
              'title': title,
              'atc_id': atc_id}

    if current_speed is not None: values['current_speed'] = current_speed

    try:
        r = requests.post(url, json=values)
        if first_datapoint:
            r = requests.post(url, json=values)
            first_datapoint = False
    except:
        return "error: request failed"

    last_data_sent_timestamp = datetime.now().timestamp()
    return "success"


def connection_status():
    if connected_to_instance:
        return "connected"
    else:
        return "disconnected"


def url_to_view():
    if connection_status() == "connected":
        return server_url + "view/" + ident_public_key
    else:
        return "no url set as not connected to instance"

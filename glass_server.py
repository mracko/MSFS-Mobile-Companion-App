from flask import Flask, jsonify, render_template, request
from SimConnect import *
from time import sleep, localtime
import random
import logging
import math
import socket
import asyncio
from threading import Thread
import datetime
import findmyplane_plugin

print (socket.gethostbyname(socket.gethostname()))

ui_friendly_dictionary = {}
event_name = None
value_to_use = None
sm = None
ae = None

# Flask WebApp
def flask_thread_func(threadname):
    
    global ui_friendly_dictionary
    global event_name
    global value_to_use
    global sm
    global ae
    
    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    @app.route('/ui')
    def output_ui_variables():
        # Initialise dictionaru
        ui_friendly_dictionary["STATUS"] = "success"
        return jsonify(ui_friendly_dictionary)

    @app.route('/')
    def index():
        return render_template('glass.html')
    
        
    def trigger_event(event_name, value_to_use=None):
        # This function actually does the work of triggering the event

        EVENT_TO_TRIGGER = ae.find(event_name)
        if EVENT_TO_TRIGGER is not None:
            if value_to_use is None:
                EVENT_TO_TRIGGER()
            else:
                # Convert Hz BCD for NAV1_RADIO_SET, NAV2_RADIO_SET and AD_SET events
                if event_name == "NAV1_RADIO_SET" or event_name == "NAV2_RADIO_SET":
                    freq_hz = float(value_to_use) * 100
                    freq_hz = str(int(freq_hz))
                    freq_hz_bcd = 0
                    for figure,digit in enumerate(reversed(freq_hz)):
                        freq_hz_bcd += int(digit)*(16**(figure))
                    EVENT_TO_TRIGGER(int(freq_hz_bcd))
                elif event_name == "ADF_COMPLETE_SET":
                    freq_hz = int(value_to_use) * 10000
                    freq_hz = str(int(freq_hz))
                    freq_hz_bcd = 0
                    for figure,digit in enumerate(reversed(freq_hz)):
                        freq_hz_bcd += int(digit)*(16**(figure))
                    EVENT_TO_TRIGGER(int(freq_hz_bcd))
                elif event_name == "COM_RADIO_SET" or event_name == "COM2_RADIO_SET":
                    freq_hz = float(value_to_use) * 100
                    flag_3dec = int(freq_hz) != freq_hz
                    freq_hz = str(int(freq_hz))
                    freq_hz_bcd = 0
                    for figure,digit in enumerate(reversed(freq_hz)):
                        freq_hz_bcd += int(digit)*(16**(figure))
                    EVENT_TO_TRIGGER(int(freq_hz_bcd))
                    # Workarouund for 3rd decimal
                    if flag_3dec is True and str(value_to_use)[-2:] != "25" and str(value_to_use)[-2:] != "75":
                        if event_name == "COM_RADIO_SET":
                            trigger_event("COM_STBY_RADIO_SWAP")
                            trigger_event("COM_RADIO_FRACT_INC")
                            trigger_event("COM_STBY_RADIO_SWAP")
                        else:
                            trigger_event("COM2_RADIO_SWAP")
                            trigger_event("COM2_RADIO_FRACT_INC")
                            trigger_event("COM2_RADIO_SWAP")
                elif event_name == "XPNDR_SET":
                    freq_hz = int(value_to_use) * 1
                    freq_hz = str(int(freq_hz))
                    freq_hz_bcd = 0
                    for figure,digit in enumerate(reversed(freq_hz)):
                        freq_hz_bcd += int(digit)*(16**(figure))
                    EVENT_TO_TRIGGER(int(freq_hz_bcd))
                else:
                    EVENT_TO_TRIGGER(int(value_to_use))

            status = "success"
        else:
            status = "Error: %s is not an Event" % (event_name)

        return status
    
    @app.route('/event/<event_name>/trigger', methods=["POST"])
    def trigger_event_endpoint(event_name):
        # This is the http endpoint wrapper for triggering an event

        ds = request.get_json() if request.is_json else request.form
        value_to_use = ds.get('value_to_use')

        status = trigger_event(event_name, value_to_use)

        return jsonify(status)


    # START: Find my plane routes

    @app.route('/findmyplane/status/check', endpoint="check")
    @app.route('/findmyplane/status/set/<status_to_set>', endpoint="set")
    # This route allows the front end to query and set the connection status
    def findmyplane_set_status(status_to_set = "check"):

        if request.endpoint == "check":
            return jsonify({'status': findmyplane_plugin.connection_status(),
                            'ident_public_key': findmyplane_plugin.ident_public_key,
                            'ident_private_key': findmyplane_plugin.ident_private_key,
                            'url_to_view': findmyplane_plugin.url_to_view()
                            })

        # Allows the front end to set the connection status. Passing "connected" will create a new plane instance.
        # Passing "disconnected" will disconnect from the instance, which will prompt the server to delete it in due
        # course if it doesn't receive more data.
        if status_to_set.lower() == "disconnected":
            findmyplane_plugin.disconnect_from_plane_instance()
            return jsonify({'status': 'disconnected'})

        if status_to_set.lower() == "connected":
            findmyplane_connection_attempt = findmyplane_plugin.request_new_plane_instance(client="Mobile Companion App") #Let me know if you are happy with this client description
            if findmyplane_connection_attempt['status'] == "success":
                print ("success")
                return jsonify({
                    'status': 'connected',
                    'ident_public_key': findmyplane_plugin.ident_public_key,
                    'ident_private_key': findmyplane_plugin.ident_private_key,
                    'url_to_view': findmyplane_plugin.url_to_view()
                })
            else:
                print ("failed")
                return jsonify({'status': 'error'})

        return jsonify({'status': 'error', 'reason': 'no valid command passed'})

    # END: Find my plane routes

    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=False)

# SimConnect  App
def simconnect_thread_func(threadname):
    
    global ui_friendly_dictionary
    global event_name
    global value_to_use
    global sm
    global ae
    
    while True:
        try:
            sm = SimConnect()
            print("\n********* MSFS 2020 Mobile Companion App *********\n")
            print(f"Local web server for MSFS 2020 Mobile Companion App initialized.\n")
            print(f"Launch {socket.gethostbyname(socket.gethostname())}:4000 in your browser to access MSFS 2020 Mobile Companion App.\n")
            print(f"Make sure your your mobile device is connected to the same local network (WIFI) as this PC.\n")
            print(f"Notice: If your computer has more than one active ethernet/WIFI adapter, please check ipconfig in command prompt.\n")
            print("**************************************************\n\n")
            break
        except:
            print("Could not find MSFS running. Please launch MSFS first and then restart the MSFS 2020 Mobile Companion App.")
            sleep(5)
            
    ae = AircraftEvents(sm)
    aq = AircraftRequests(sm)

    # Initialize previous altitude for code stability
    previous_alt = -400

    # Initialize vars for landing info
    ui_friendly_dictionary["LANDING_VS1"] = "N/A"
    ui_friendly_dictionary["LANDING_T1"] = 0
    ui_friendly_dictionary["LANDING_VS2"] = "N/A"
    ui_friendly_dictionary["LANDING_T2"] = 0
    ui_friendly_dictionary["LANDING_VS3"] = "N/A"
    ui_friendly_dictionary["LANDING_T3"] = 0

    
    def thousandify(x):
        return f"{x:,}"

    async def ui_dictionary(ui_friendly_dictionary, previous_alt, landing_t1, landing_vs1, landing_t2, landing_vs2, landing_t3, landing_vs3):
        # Position
        try:
            ui_friendly_dictionary["LATITUDE"] = round(await aq.get("PLANE_LATITUDE"),6)
            ui_friendly_dictionary["LONGITUDE"] = round(await aq.get("PLANE_LONGITUDE"),6)
            ui_friendly_dictionary["MAGNETIC_COMPASS"] = round(round(await aq.get("PLANE_HEADING_DEGREES_TRUE"),2) * 180/3.1416, 2)
            #ui_friendly_dictionary["MAGVAR"] = round(await aq.get("MAGVAR"))
        except:
            None

        # Radios
        ui_friendly_dictionary["NAV1_STANDBY"] = round(await aq.get("NAV_STANDBY_FREQUENCY:1"),2)
        ui_friendly_dictionary["NAV1_ACTIVE"] = round(await aq.get("NAV_ACTIVE_FREQUENCY:1"),2)

        ui_friendly_dictionary["NAV2_STANDBY"] = round(await aq.get("NAV_STANDBY_FREQUENCY:2"),2)
        ui_friendly_dictionary["NAV2_ACTIVE"] = round(await aq.get("NAV_ACTIVE_FREQUENCY:2"),2)

        # ADF Active
        adf_use_bcd = int(await aq.get("ADF_ACTIVE_FREQUENCY:1"))
        adf_use_digits = ""

        for i in reversed(range(4)):
            adf_use_digit = math.floor(adf_use_bcd / (65536*(16**i)))
            adf_use_digits = adf_use_digits + str(adf_use_digit)
            adf_use_bcd = adf_use_bcd - (65536*(16**i)) * adf_use_digit

        try:
            ui_friendly_dictionary["ADF_USE_1000"] = adf_use_digits[0]
            ui_friendly_dictionary["ADF_USE_100"] = adf_use_digits[1]
            ui_friendly_dictionary["ADF_USE_10"] = adf_use_digits[2]
            ui_friendly_dictionary["ADF_USE_1"] = adf_use_digits[3]
            ui_friendly_dictionary["ADF_USE"] = int(adf_use_digits)
        except:
            None

        # ADF Standby
        adf_stby = int(await aq.get("ADF_STANDBY_FREQUENCY:1"))/1000
        try:
            if adf_stby >= 1000:
                ui_friendly_dictionary["ADF_STBY_1000"] = str(adf_stby)[0]
                ui_friendly_dictionary["ADF_STBY_100"] = str(adf_stby)[1]
                ui_friendly_dictionary["ADF_STBY_10"] = str(adf_stby)[2]
                ui_friendly_dictionary["ADF_STBY_1"] = str(adf_stby)[3]
            else:
                ui_friendly_dictionary["ADF_STBY_1000"] = "0"
                ui_friendly_dictionary["ADF_STBY_100"] = str(adf_stby)[0]
                ui_friendly_dictionary["ADF_STBY_10"] = str(adf_stby)[1]
                ui_friendly_dictionary["ADF_STBY_1"] = str(adf_stby)[2]
        except:
            None

        # NAV/ADF Compass Settings
        ui_friendly_dictionary["NAV1_OBS_DEG"] = round(await aq.get("NAV_OBS:1"),0)
        ui_friendly_dictionary["ADF_CARD_DEG"] = round(await aq.get("ADF_CARD"),0)
        ui_friendly_dictionary["NAV2_OBS_DEG"] = round(await aq.get("NAV_OBS:2"),0)

        # Comms
        ui_friendly_dictionary["COM1_STANDBY"] = round(await aq.get("COM_STANDBY_FREQUENCY:1"),3)
        ui_friendly_dictionary["COM1_ACTIVE"] = round(await aq.get("COM_ACTIVE_FREQUENCY:1"),3)
        ui_friendly_dictionary["COM1_TRANSMIT"] = await aq.get("COM_TRANSMIT:1")
        ui_friendly_dictionary["COM2_STANDBY"] = round(await aq.get("COM_STANDBY_FREQUENCY:2"),3)
        ui_friendly_dictionary["COM2_ACTIVE"] = round(await aq.get("COM_ACTIVE_FREQUENCY:2"),3)
        ui_friendly_dictionary["COM2_TRANSMIT"] = await aq.get("COM_TRANSMIT:2")
        
        # XPNDR
        xpndr_bcd = await aq.get("TRANSPONDER_CODE:1")
        xpndr_digits = ""
        
        # XPNDR Conversion from BCD to Decimal
        try:
            for i in reversed(range(4)):
                xpndr_digit = math.floor(xpndr_bcd / (16**i))
                xpndr_digits = xpndr_digits + str(xpndr_digit)
                xpndr_bcd = xpndr_bcd - (16**i) * xpndr_digit
        except:
            None

        try:
            ui_friendly_dictionary["XPNDR_1000"] = xpndr_digits[0]
            ui_friendly_dictionary["XPNDR_100"] = xpndr_digits[1]
            ui_friendly_dictionary["XPNDR_10"] = xpndr_digits[2]
            ui_friendly_dictionary["XPNDR_1"] = xpndr_digits[3]
            ui_friendly_dictionary["XPNDR"] = int(xpndr_digits)
        except:
            None

        # Autopilot
        ui_friendly_dictionary["AUTOPILOT_MASTER"] = await aq.get("AUTOPILOT_MASTER")
        ui_friendly_dictionary["AUTOPILOT_NAV1_LOCK"] = await aq.get("AUTOPILOT_NAV1_LOCK")
        ui_friendly_dictionary["AUTOPILOT_HEADING_LOCK"] = await aq.get("AUTOPILOT_HEADING_LOCK")
        ui_friendly_dictionary["AUTOPILOT_HEADING_LOCK_DIR"] = round(await aq.get("AUTOPILOT_HEADING_LOCK_DIR"))
        ui_friendly_dictionary["AUTOPILOT_ALTITUDE_LOCK"] = await aq.get("AUTOPILOT_ALTITUDE_LOCK")
        ui_friendly_dictionary["AUTOPILOT_ALTITUDE_LOCK_VAR"] = thousandify(round(await aq.get("AUTOPILOT_ALTITUDE_LOCK_VAR")))
        ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] = await aq.get("AUTOPILOT_GLIDESLOPE_HOLD")
        ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] = await aq.get("AUTOPILOT_APPROACH_HOLD")
        ui_friendly_dictionary["AUTOPILOT_BACKCOURSE_HOLD"] = await aq.get("AUTOPILOT_BACKCOURSE_HOLD")
        ui_friendly_dictionary["AUTOPILOT_VERTICAL_HOLD"] = await aq.get("AUTOPILOT_VERTICAL_HOLD")
        ui_friendly_dictionary["AUTOPILOT_VERTICAL_HOLD_VAR"] = await aq.get("AUTOPILOT_VERTICAL_HOLD_VAR")
        ui_friendly_dictionary["AUTOPILOT_FLIGHT_LEVEL_CHANGE"] = await aq.get("AUTOPILOT_FLIGHT_LEVEL_CHANGE")
        ui_friendly_dictionary["AUTOPILOT_AIRSPEED_HOLD_VAR"] = round(await aq.get("AUTOPILOT_AIRSPEED_HOLD_VAR"))
        ui_friendly_dictionary["AUTOPILOT_AUTOTHROTTLE"] = await aq.get("AUTOTHROTTLE_ACTIVE")
        ui_friendly_dictionary["AIRSPEED_INDICATED"] = round(await aq.get("AIRSPEED_INDICATED"))
        # Placeholders - Not Actively Used for stress testing
        #ui_friendly_dictionary["AUTOPILOT_NAV_SELECTED"] = await aq.get("AUTOPILOT_NAV_SELECTED")
        #ui_friendly_dictionary["AUTOPILOT_WING_LEVELER"] = await aq.get("AUTOPILOT_WING_LEVELER")
        #ui_friendly_dictionary["AUTOPILOT_PITCH_HOLD"] = await aq.get("AUTOPILOT_PITCH_HOLD")
        #ui_friendly_dictionary["AUTOPILOT_PITCH_HOLD_REF"] = await aq.get("AUTOPILOT_PITCH_HOLD_REF")
        ui_friendly_dictionary["AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE"] = await aq.get("AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE")
        # Lights
        ui_friendly_dictionary["LIGHT_LANDING"] = await aq.get("LIGHT_LANDING")
        ui_friendly_dictionary["LIGHT_TAXI"] = await aq.get("LIGHT_TAXI")
        ui_friendly_dictionary["LIGHT_STROBE"] = await aq.get("LIGHT_STROBE")
        ui_friendly_dictionary["LIGHT_NAV"] = await aq.get("LIGHT_NAV")
        ui_friendly_dictionary["LIGHT_BEACON"] = await aq.get("LIGHT_BEACON")
        ui_friendly_dictionary["LIGHT_CABIN"] = await aq.get("LIGHT_CABIN")
        ui_friendly_dictionary["LIGHT_LOGO"] = await aq.get("LIGHT_CABIN")
        ui_friendly_dictionary["LIGHT_PANEL"] = await aq.get("LIGHT_PANEL")
        ui_friendly_dictionary["LIGHT_WING"] = await aq.get("LIGHT_WING")
        ui_friendly_dictionary["LIGHT_RECOGNITION"] = await aq.get("LIGHT_RECOGNITION")
        # Pitot Heat and Deice
        ui_friendly_dictionary["PITOT_HEAT"] = await aq.get("PITOT_HEAT")
        #ui_friendly_dictionary["PROP_DEICE_SWITCH"] = await aq.get("PROP_DEICE_SWITCH:1")
        ui_friendly_dictionary["ENG_ANTI_ICE"] = await aq.get("ENG_ANTI_ICE:1")
        #ui_friendly_dictionary["GEN_ENG_ANTI_ICE"] = await aq.get("GENERAL_ENG_ANTI_ICE_POSITION:1")
        ui_friendly_dictionary["STRUCTURAL_DEICE_SWITCH"] = await aq.get("STRUCTURAL_DEICE_SWITCH")
        #ui_friendly_dictionary["PANEL_ANTI_ICE_SWITCH"] = await aq.get("PANEL_ANTI_ICE_SWITCH")
        # Sim Rate
        ui_friendly_dictionary["SIMULATION_RATE"] = await aq.get("SIMULATION_RATE")
        
        
        # Current altitude
        current_alt = await aq.get("INDICATED_ALTITUDE")
        if current_alt > -300:
            ui_friendly_dictionary["INDICATED_ALTITUDE"] = round(current_alt)
            previous_alt = current_alt
        else:
            try:
                ui_friendly_dictionary["INDICATED_ALTITUDE"] = previous_alt
            except:
                pass
        
        # LOC and APPR Mode
        try:
            if (ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] == 1 and ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] == 1):
                ui_friendly_dictionary["AUTOPILOT_APPR_MODE"] = 1
            else:
                ui_friendly_dictionary["AUTOPILOT_APPR_MODE"] = 0
            if (ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] == 1 and ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] == 0):
                ui_friendly_dictionary["AUTOPILOT_LOC_MODE"] = 1
            else:
                ui_friendly_dictionary["AUTOPILOT_LOC_MODE"] = 0     
        except:
            None
        
        # Other
        
        current_landing = round(await aq.get("PLANE_TOUCHDOWN_NORMAL_VELOCITY") * 60)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        
        if landing_vs1 != current_landing:
            # Move 2nd to 3rd
            landing_t3 = landing_t2
            landing_vs3 = landing_vs2
            # Move 1st to 2nd
            landing_t2 = landing_t1
            landing_vs2 = landing_vs1
            # Assign new 1st
            landing_t1 = current_time
            landing_vs1 = current_landing
            # Dictionary Output
            ui_friendly_dictionary["LANDING_VS1"] = landing_vs1
            ui_friendly_dictionary["LANDING_T1"] = landing_t1
            ui_friendly_dictionary["LANDING_VS2"] = landing_vs2
            ui_friendly_dictionary["LANDING_T2"] = landing_t2
            ui_friendly_dictionary["LANDING_VS3"] = landing_vs3
            ui_friendly_dictionary["LANDING_T3"] = landing_t3
        
    while True:
        asyncio.run(ui_dictionary(ui_friendly_dictionary, previous_alt, ui_friendly_dictionary["LANDING_T1"], ui_friendly_dictionary["LANDING_VS1"], ui_friendly_dictionary["LANDING_T2"], ui_friendly_dictionary["LANDING_VS2"], ui_friendly_dictionary["LANDING_T3"], ui_friendly_dictionary["LANDING_VS3"]))
        #sleep(0.3)
       

  
if __name__ == "__main__":
    thread1 = Thread(target = simconnect_thread_func, args=('Thread-1', ))
    thread2 = Thread(target = flask_thread_func, args=('Thread-2', ))
    thread1.start()
    thread2.start()
    
    sleep(.5)
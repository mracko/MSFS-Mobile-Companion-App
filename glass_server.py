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
    global fltpln
    
    # Define Supported Aircraft
    planes_list = [
        "Default",
        "Default GNS430",
        "Default GNS530",
        "Default G1000",
        "A32NX (FlyByWire)",
        "CRJ-550/700 (Aerosoft)",
        "PA-28R Arrow III GPS100 (Just Flight)",
        "PA-28R Arrow III GNS530 (Just Flight)",
        "PA-28R Arrow III GNS Dual (Just Flight)"
        ]
    planes_dict = {
        "Default": [["NAV", "nav"],["COM", "com"],["AP", "ap"],["Panel", "panel"]],
        "Default GNS430": [["NAV", "nav"],["COM", "com"],["AP", "ap"],["GPS", "gns430"],["Panel", "panel"]],
        "Default GNS530": [["NAV", "nav"],["COM", "com"],["AP", "ap"],["GPS", "gns530"],["Panel", "panel"]],
        "Default G1000": [["NAV", "nav"],["COM", "com"],["AP", "ap"],["PFD", "g1000_pfd"],["MFD", "g1000_mfd"],["Panel", "panel"]],
        "A32NX (FlyByWire)":[["FCU", "ap_a32nx"],["EFIS", "efis_a32nx"],["COM", "com"],["Panel", "panel_a32nx"]],
        "CRJ-550/700 (Aerosoft)": [["FCP", "ap_as_crj"],["Side\xa0Panel", "side_panel_as_crj"],["NAV", "nav_as_crj"],["COM", "com_as_crj"]],
        "PA-28R Arrow III GPS100 (Just Flight)": [["NAV", "nav_jf_arrow_gps100"],["COM", "com_jf_arrow_gps100"],["AP", "ap_jf_arrow"],["GPS", "gps100_jf_arrow"],["Panel", "panel_jf_arrow"]],
        "PA-28R Arrow III GNS530 (Just Flight)": [["NAV", "nav_jf_arrow_gns"],["COM", "com_jf_arrow_gns"],["AP", "ap_jf_arrow"],["GPS", "gns530"],["Panel", "panel_jf_arrow"]],
        "PA-28R Arrow III GNS Dual (Just Flight)": [["NAV", "nav_jf_arrow_gnsdual"],["COM", "com_jf_arrow_gnsdual"],["AP", "ap_jf_arrow"],["GPS", "gnsdual_jf_arrow"],["Panel", "panel_jf_arrow"]]
        }
    global selected_plane
    selected_plane = planes_list[0]
    
    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    @app.route('/ui')
    def output_ui_variables():
        # Initialise dictionaru
        ui_friendly_dictionary["STATUS"] = "success"
        return jsonify(ui_friendly_dictionary)
    
    @app.route('/', methods=["GET", "POST"])
    def index():
        global selected_plane
        cur_plane_select = request.form.get("plane_selected")
        if cur_plane_select != None:
            selected_plane = cur_plane_select
        return render_template('glass.html', planes_list = planes_list, selected_plane = selected_plane, curr_plane = planes_dict[selected_plane])
    
    @app.route('/landscape', methods=["GET", "POST"])
    def index_landscape():
        global selected_plane
        cur_plane_select = request.form.get("plane_selected")
        if cur_plane_select != None:
            selected_plane = cur_plane_select
        return render_template('glass_landscape.html', planes_list = planes_list, selected_plane = selected_plane, curr_plane = planes_dict[selected_plane])
        
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
    
    # Load Flight Plan
    fltpln = []
    @app.route('/fltpln', methods=["POST"])
    def load_fltpln():
        # Load Settings - MSFS Install Location
        try:
            with open('settings.txt', 'r') as settings:
                lines = settings.readlines()

            # Get Flight Plan
            fltpln_dir = ""
            for line in lines:
                if len(line)>0:
                    if line[0] != "#":
                        fltpln_dir = line
                        # Check to delete \ at the endswith
                        if fltpln_dir[-1] == "\\":
                            fltpln_dir = fltpln_dir[:-1]
                        break
            
            try:
                # MS Store
                fltpln_dir_full = fltpln_dir + "\LocalState\MISSIONS\Custom\CustomFlight\CUSTOMFLIGHT.FLT"
                with open(fltpln_dir_full, 'r') as fltpln:
                    fltpln_lines = fltpln.readlines()
            except:
                # Steam
                fltpln_dir_full = fltpln_dir + "\MISSIONS\Custom\CustomFlight\CUSTOMFLIGHT.FLT"
                with open(fltpln_dir_full, 'r') as fltpln:
                    fltpln_lines = fltpln.readlines()

            # Process Flight Plan Function
            def latlong_dec_convert(to_convert):
                """Function converts deg/min/sec to decimal"""
                elements = to_convert.split(" ")
                conversion = 0
                for element in elements:
                    # Degrees Conversion
                    if element[-1] == "°":
                        conversion = conversion + float(element[1:-1])
                        continue
                    # Minutes Conversion
                    if element[-1] == "'":
                        conversion = conversion + (float(element[0:-1])/60)
                        continue
                    # Seconds Conversion
                    if element[-1] == '"':
                        conversion = conversion + (float(element[0:-1])/3600)
                        continue
                   
                # Degrees Conversion Negative/Positive
                if elements[0][0] in ["W","S"]:
                    conversion = conversion * (-1)
                    
                return conversion

            # Check if ATC_RequestedFlightPlan
            atc_reqfltpln = False
            for idx, line in enumerate(fltpln_lines):
                if line.find("[ATC_RequestedFlightPlan.0]") >= 0:
                    atc_reqfltpln = True
                    fltpln_lines = fltpln_lines[(idx + 1):]
                    break
            
            #Process FLT file
            if atc_reqfltpln == False:
                # For VFR Flights
                # Get No of Waypoints
                no_wpts = 0
                for line in fltpln_lines:
                    if line.find("NumberofWaypoints=") >= 0:
                        no_wpts = int(line.split("=")[1])
                        break
                
                # Get LatLong for Waypoitns
                fltpln_arr = []
                wpts_processed = 0
                for line in fltpln_lines:
                    if wpts_processed < no_wpts:
                        if line.find("Waypoint.") >= 0:
                            line_elements = line.split(",")
                            fltpln_wp = [latlong_dec_convert(line_elements[5].strip()),latlong_dec_convert(line_elements[6].strip())]
                            fltpln_arr.append(fltpln_wp)
                            wpts_processed = wpts_processed + 1
                    else:
                        break
                        
            else:
                # For IFR Flights
                fltpln_arr = []
                wpt_id = False
                for line in fltpln_lines:
                    if line.find("waypoint.") >= 0:
                        line_elements = line.split(",")
                        fltpln_wp = [latlong_dec_convert(line_elements[5].strip()),latlong_dec_convert(line_elements[6].strip())]
                        fltpln_arr.append(fltpln_wp)
                        wpt_id = True
                    else:
                        if wpt_id == True:
                            break

            ui_friendly_dictionary["FLT_PLN"] = fltpln_arr

            success = "Flight plan loaded"

        except:
            print("Error loading flight plan. Make sure you have the correct MSFS installation path in settings.txt.")
            success = "Error loading flight plan"
        
        return success
    
    app.run(host='0.0.0.0', port=4000, debug=False)

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
        ui_friendly_dictionary["AUTOPILOT_YAW_DAMPER"] = await aq.get("AUTOPILOT_YAW_DAMPER")
        ui_friendly_dictionary["AIRSPEED_INDICATED"] = round(await aq.get("AIRSPEED_INDICATED"))
        ui_friendly_dictionary["AUTOPILOT_AIRSPEED_HOLD"] = await aq.get("AUTOPILOT_AIRSPEED_HOLD")
        #ui_friendly_dictionary["AUTOPILOT_MACH_HOLD_VAR"] = round(await aq.get("AUTOPILOT_MACH_HOLD_VAR"),2)
        ui_friendly_dictionary["PLANE_HEADING_DEGREES"] = round(round(await aq.get("PLANE_HEADING_DEGREES_MAGNETIC"),2) * 180/3.1416, 0)
        # Placeholders - Not Actively Used for stress testing
        #ui_friendly_dictionary["ATC_AIRLINE"] = await aq.get("ATC_AIRLINE")
        #ui_friendly_dictionary["SMOKE_ENABLE"] = await aq.get("SMOKE_ENABLE")
        #ui_friendly_dictionary["AUTOPILOT_MACH_HOLD"] = await aq.get("AUTOPILOT_MACH_HOLD")
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
        # GPS Next Waypoint
        ui_friendly_dictionary["NEXT_WP_LAT"] = await aq.get("GPS_WP_NEXT_LAT")
        ui_friendly_dictionary["NEXT_WP_LON"] = await aq.get("GPS_WP_NEXT_LON")
        
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

        #Gear Lever position

        ui_friendly_dictionary["GEAR_HANDLE_POSITION"] = await aq.get("GEAR_HANDLE_POSITION")
        
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
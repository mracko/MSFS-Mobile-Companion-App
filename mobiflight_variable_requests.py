import logging
import struct
from ctypes import sizeof
from ctypes.wintypes import FLOAT
from SimConnect.Enum import SIMCONNECT_CLIENT_DATA_PERIOD, SIMCONNECT_UNUSED


class SimVariable:
    def __init__(self, id, name, float_value = 0):
        self.id = id
        self.name = name
        self.float_value = float_value
    def __str__(self):
        return f"Id={self.id}, value={self.float_value}, name={self.name}"


class MobiFlightVariableRequests:

    def __init__(self, simConnect):
        logging.info("MobiFlightVariableRequests __init__")
        self.sm = simConnect
        self.sim_vars = {}
        self.sim_var_name_to_id = {}
        self.CLIENT_DATA_AREA_LVARS    = 0
        self.CLIENT_DATA_AREA_CMD      = 1
        self.CLIENT_DATA_AREA_RESPONSE = 2
        self.FLAG_DEFAULT = 0
        self.FLAG_CHANGED = 1
        self.DATA_STRING_SIZE = 256
        self.DATA_STRING_OFFSET = 0
        self.DATA_STRING_DEFINITION_ID = 0
        self.sm.register_client_data_handler(self.client_data_callback_handler)
        self.initialize_client_data_areas()


    def add_to_client_data_definition(self, definition_id, offset, size):
        logging.info("add_to_client_data_definition definition_id=%s, offset=%s, size=%s", definition_id, offset, size)
        self.sm.dll.AddToClientDataDefinition(
            self.sm.hSimConnect,
            definition_id, 
            offset,
            size,
            0,  # fEpsilon
            SIMCONNECT_UNUSED) # DatumId

    
    def subscribe_to_data_change(self, data_area_id, request_id, definition_id):
        logging.info("subscribe_to_data_change data_area_id=%s, request_id=%s, definition_id=%s", data_area_id, request_id, definition_id)
        self.sm.dll.RequestClientData(
            self.sm.hSimConnect,
            data_area_id,
            request_id,
            definition_id, 
            SIMCONNECT_CLIENT_DATA_PERIOD.SIMCONNECT_CLIENT_DATA_PERIOD_ON_SET,
            self.FLAG_CHANGED,
            0, # origin
            0, # interval
            0) # limit


    def send_data(self, data_area_id, definition_id, size, dataBytes):
        logging.info("send_data data_area_id=%s, definition_id=%s, size=%s, dataBytes=%s", data_area_id, definition_id, size, dataBytes)
        self.sm.dll.SetClientData(
            self.sm.hSimConnect,
            data_area_id, 
            definition_id,
            self.FLAG_DEFAULT,
            0, # dwReserved
            size, 
            dataBytes)  


    def send_command(self, command):
        logging.info("send_command command=%s", command)
        data_byte_array = bytearray(command, "ascii")
        data_byte_array.extend(bytearray(self.DATA_STRING_SIZE - len(data_byte_array)))  # extend to fix DATA_STRING_SIZE
        self.send_data(self.CLIENT_DATA_AREA_CMD, self.DATA_STRING_DEFINITION_ID, self.DATA_STRING_SIZE, bytes(data_byte_array))

        
    def initialize_client_data_areas(self):
        logging.info("initialize_client_data_areas")
        # register client data area for receiving simvars
        self.sm.dll.MapClientDataNameToID(self.sm.hSimConnect, "MobiFlight.LVars".encode("ascii"), self.CLIENT_DATA_AREA_LVARS)
        self.sm.dll.CreateClientData(self.sm.hSimConnect, self.CLIENT_DATA_AREA_LVARS, 4096, self.FLAG_DEFAULT)
        # register client data area for sending commands
        self.sm.dll.MapClientDataNameToID(self.sm.hSimConnect, "MobiFlight.Command".encode("ascii"), self.CLIENT_DATA_AREA_CMD)
        self.sm.dll.CreateClientData(self.sm.hSimConnect, self.CLIENT_DATA_AREA_CMD, self.DATA_STRING_SIZE, self.FLAG_DEFAULT)
        # register client data area for receiving responses
        self.sm.dll.MapClientDataNameToID(self.sm.hSimConnect, "MobiFlight.Response".encode("ascii"), self.CLIENT_DATA_AREA_RESPONSE)
        self.sm.dll.CreateClientData(self.sm.hSimConnect, self.CLIENT_DATA_AREA_RESPONSE, self.DATA_STRING_SIZE, self.FLAG_DEFAULT)
        # subscribe to WASM Module responses
        self.add_to_client_data_definition(self.DATA_STRING_DEFINITION_ID, self.DATA_STRING_OFFSET, self.DATA_STRING_SIZE)
        self.subscribe_to_data_change(self.CLIENT_DATA_AREA_RESPONSE, self.DATA_STRING_DEFINITION_ID, self.DATA_STRING_DEFINITION_ID)


    # simconnect library callback
    def client_data_callback_handler(self, client_data):
        if client_data.dwDefineID in self.sim_vars:
            data_bytes = struct.pack("i", client_data.dwData[0])
            float_data = struct.unpack('<f', data_bytes)[0]   # unpack delivers a tuple -> [0]
            self.sim_vars[client_data.dwDefineID].float_value = round(float_data, 5)
            logging.debug("client_data_callback_handler %s", self.sim_vars[client_data.dwDefineID])
        else:
            logging.warning("client_data_callback_handler DefinitionID %s not found!", client_data.dwDefineID)


    def get(self, variableString):
        if variableString not in self.sim_var_name_to_id:
            # add new variable
            id = len(self.sim_vars) + 1
            self.sim_vars[id] = SimVariable(id, variableString)
            self.sim_var_name_to_id[variableString] = id
            # subscribe to variable data change
            offset = (id-1)*sizeof(FLOAT)
            self.add_to_client_data_definition(id, offset, sizeof(FLOAT))
            self.subscribe_to_data_change(self.CLIENT_DATA_AREA_LVARS, id, id)
            self.send_command("MF.SimVars.Add." + variableString)  
        # determine id and return value
        variable_id = self.sim_var_name_to_id[variableString]
        float_value = self.sim_vars[variable_id].float_value
        logging.debug("get %s. Return=%s", variableString, float_value)
        return float_value
            

    def clear_sim_variables(self):
        logging.info("clear_sim_variables")
        self.sim_vars.clear()
        self.sim_var_name_to_id.clear()
        self.send_command("MF.SimVars.Clear")
        

       
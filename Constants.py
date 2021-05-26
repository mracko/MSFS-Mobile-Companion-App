import logging
from ctypes.wintypes import *
from ctypes import *

LOGGER = logging.getLogger(__name__)


# //----------------------------------------------------------------------------
# //        Constants
# //----------------------------------------------------------------------------

DWORD_MAX = DWORD(0xFFFFFFFF)
SIMCONNECT_UNUSED = DWORD_MAX
SIMCONNECT_OBJECT_ID_USER = DWORD(0)  # proxy value for User vehicle ObjectID
SIMCONNECT_UNUSED = DWORD_MAX  # special value to indicate unused event, ID

SIMCONNECT_CAMERA_IGNORE_FIELD = c_float(
	-1
)  # Used to tell the Camera API to NOT modify the value in this part of the argument.

SIMCONNECT_CLIENTDATA_MAX_SIZE = DWORD(
	8192
)  # maximum value for SimConnect_CreateClientData dwSize parameter


# Notification Group priority values
SIMCONNECT_GROUP_PRIORITY_HIGHEST = DWORD(1)  # highest priority
SIMCONNECT_GROUP_PRIORITY_HIGHEST_MASKABLE = DWORD(
	10000000
)  # highest priority that allows events to be masked
SIMCONNECT_GROUP_PRIORITY_STANDARD = DWORD(1900000000)  # standard priority
SIMCONNECT_GROUP_PRIORITY_DEFAULT = DWORD(2000000000)  # default priority
SIMCONNECT_GROUP_PRIORITY_LOWEST = DWORD(
	4000000000
)  # priorities lower than this will be ignored

# Weather observations Metar strings
MAX_METAR_LENGTH = DWORD(2000)

# Maximum thermal size is 100 km.
MAX_THERMAL_SIZE = c_float(100000)
MAX_THERMAL_RATE = c_float(1000)

# SIMCONNECT_DATA_INITPOSITION.Airspeed
INITPOSITION_AIRSPEED_CRUISE = DWORD(-1)  # aircraft's cruise airspeed
INITPOSITION_AIRSPEED_KEEP = DWORD(-2)  # keep current airspeed

# AddToClientDataDefinition dwSizeOrType parameter type values
SIMCONNECT_CLIENTDATATYPE_INT8 = DWORD(-1)  # 8-bit integer number
SIMCONNECT_CLIENTDATATYPE_INT16 = DWORD(-2)  # 16-bit integer number
SIMCONNECT_CLIENTDATATYPE_INT32 = DWORD(-3)  # 32-bit integer number
SIMCONNECT_CLIENTDATATYPE_INT64 = DWORD(-4)  # 64-bit integer number
SIMCONNECT_CLIENTDATATYPE_FLOAT32 = DWORD(-5)  # 32-bit floating-point number (float)
SIMCONNECT_CLIENTDATATYPE_FLOAT64 = DWORD(-6)  # 64-bit floating-point number (double)

# AddToClientDataDefinition dwOffset parameter special values
SIMCONNECT_CLIENTDATAOFFSET_AUTO = DWORD(
	-1
)  # automatically compute offset of the ClientData variable

# Open ConfigIndex parameter special value
SIMCONNECT_OPEN_CONFIGINDEX_LOCAL = DWORD(
	-1
)  # ignore SimConnect.cfg settings, and force local connection
SIMCONNECT_OBJECT_ID = DWORD

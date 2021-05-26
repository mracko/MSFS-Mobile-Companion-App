from enum import IntEnum, Enum, auto
from ctypes.wintypes import *
from ctypes import *
from .Constants import *

import logging

LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
#        Enum definitions
# ----------------------------------------------------------------------------


# Define the types we need.
class CtypesEnum(IntEnum):
	"""A ctypes-compatible IntEnum superclass."""

	@classmethod
	def from_param(cls, obj):
		return int(obj)


# Define the types we need.
class CtypesEn(Enum):
	"""A ctypes-compatible Enum superclass."""

	@classmethod
	def from_param(cls, obj):
		return int(obj)


class AutoName(CtypesEnum):
	def _generate_next_value_(name, start, count, last_values):
		return count


# Receive data types
class SIMCONNECT_RECV_ID(CtypesEnum):
	SIMCONNECT_RECV_ID_NULL = 0
	SIMCONNECT_RECV_ID_EXCEPTION = 1
	SIMCONNECT_RECV_ID_OPEN = 2
	SIMCONNECT_RECV_ID_QUIT = 3
	SIMCONNECT_RECV_ID_EVENT = 4
	SIMCONNECT_RECV_ID_EVENT_OBJECT_ADDREMOVE = 5
	SIMCONNECT_RECV_ID_EVENT_FILENAME = 6
	SIMCONNECT_RECV_ID_EVENT_FRAME = 7
	SIMCONNECT_RECV_ID_SIMOBJECT_DATA = 8
	SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE = 9
	SIMCONNECT_RECV_ID_WEATHER_OBSERVATION = 10
	SIMCONNECT_RECV_ID_CLOUD_STATE = 11
	SIMCONNECT_RECV_ID_ASSIGNED_OBJECT_ID = 12
	SIMCONNECT_RECV_ID_RESERVED_KEY = 13
	SIMCONNECT_RECV_ID_CUSTOM_ACTION = 14
	SIMCONNECT_RECV_ID_SYSTEM_STATE = 15
	SIMCONNECT_RECV_ID_CLIENT_DATA = 16
	SIMCONNECT_RECV_ID_EVENT_WEATHER_MODE = 17
	SIMCONNECT_RECV_ID_AIRPORT_LIST = 18
	SIMCONNECT_RECV_ID_VOR_LIST = 19
	SIMCONNECT_RECV_ID_NDB_LIST = 20
	SIMCONNECT_RECV_ID_WAYPOINT_LIST = 21
	SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SERVER_STARTED = 22
	SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_CLIENT_STARTED = 23
	SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SESSION_ENDED = 24
	SIMCONNECT_RECV_ID_EVENT_RACE_END = 25
	SIMCONNECT_RECV_ID_EVENT_RACE_LAP = 26


# Data data types
class SIMCONNECT_DATATYPE(CtypesEnum):
	SIMCONNECT_DATATYPE_INVALID = 0  # invalid data type
	SIMCONNECT_DATATYPE_INT32 = 1  # 32-bit integer number
	SIMCONNECT_DATATYPE_INT64 = 2  # 64-bit integer number
	SIMCONNECT_DATATYPE_FLOAT32 = 3  # 32-bit floating-point number (float)
	SIMCONNECT_DATATYPE_FLOAT64 = 4  # 64-bit floating-point number (double)
	SIMCONNECT_DATATYPE_STRING8 = 5  # 8-byte string
	SIMCONNECT_DATATYPE_STRING32 = 6  # 32-byte string
	SIMCONNECT_DATATYPE_STRING64 = 7  # 64-byte string
	SIMCONNECT_DATATYPE_STRING128 = 8  # 128-byte string
	SIMCONNECT_DATATYPE_STRING256 = 9  # 256-byte string
	SIMCONNECT_DATATYPE_STRING260 = 10  # 260-byte string
	SIMCONNECT_DATATYPE_STRINGV = 11  # variable-length string

	SIMCONNECT_DATATYPE_INITPOSITION = 12  # see SIMCONNECT_DATA_INITPOSITION
	SIMCONNECT_DATATYPE_MARKERSTATE = 13  # see SIMCONNECT_DATA_MARKERSTATE
	SIMCONNECT_DATATYPE_WAYPOINT = 14  # see SIMCONNECT_DATA_WAYPOINT
	SIMCONNECT_DATATYPE_LATLONALT = 15  # see SIMCONNECT_DATA_LATLONALT
	SIMCONNECT_DATATYPE_XYZ = 16  # see SIMCONNECT_DATA_XYZ

	SIMCONNECT_DATATYPE_MAX = 17  # enum limit


# Exception error types
class SIMCONNECT_EXCEPTION(CtypesEnum):
	SIMCONNECT_EXCEPTION_NONE = 0

	SIMCONNECT_EXCEPTION_ERROR = 1
	SIMCONNECT_EXCEPTION_SIZE_MISMATCH = 2
	SIMCONNECT_EXCEPTION_UNRECOGNIZED_ID = 3
	SIMCONNECT_EXCEPTION_UNOPENED = 4
	SIMCONNECT_EXCEPTION_VERSION_MISMATCH = 5
	SIMCONNECT_EXCEPTION_TOO_MANY_GROUPS = 6
	SIMCONNECT_EXCEPTION_NAME_UNRECOGNIZED = 7
	SIMCONNECT_EXCEPTION_TOO_MANY_EVENT_NAMES = 8
	SIMCONNECT_EXCEPTION_EVENT_ID_DUPLICATE = 9
	SIMCONNECT_EXCEPTION_TOO_MANY_MAPS = 10
	SIMCONNECT_EXCEPTION_TOO_MANY_OBJECTS = 11
	SIMCONNECT_EXCEPTION_TOO_MANY_REQUESTS = 12
	SIMCONNECT_EXCEPTION_WEATHER_INVALID_PORT = 13
	SIMCONNECT_EXCEPTION_WEATHER_INVALID_METAR = 14
	SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_GET_OBSERVATION = 15
	SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_CREATE_STATION = 16
	SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_REMOVE_STATION = 17
	SIMCONNECT_EXCEPTION_INVALID_DATA_TYPE = 18
	SIMCONNECT_EXCEPTION_INVALID_DATA_SIZE = 19
	SIMCONNECT_EXCEPTION_DATA_ERROR = 20
	SIMCONNECT_EXCEPTION_INVALID_ARRAY = 21
	SIMCONNECT_EXCEPTION_CREATE_OBJECT_FAILED = 22
	SIMCONNECT_EXCEPTION_LOAD_FLIGHTPLAN_FAILED = 23
	SIMCONNECT_EXCEPTION_OPERATION_INVALID_FOR_OBJECT_TYPE = 24
	SIMCONNECT_EXCEPTION_ILLEGAL_OPERATION = 24
	SIMCONNECT_EXCEPTION_ALREADY_SUBSCRIBED = 26
	SIMCONNECT_EXCEPTION_INVALID_ENUM = 27
	SIMCONNECT_EXCEPTION_DEFINITION_ERROR = 28
	SIMCONNECT_EXCEPTION_DUPLICATE_ID = 29
	SIMCONNECT_EXCEPTION_DATUM_ID = 30
	SIMCONNECT_EXCEPTION_OUT_OF_BOUNDS = 31
	SIMCONNECT_EXCEPTION_ALREADY_CREATED = 32
	SIMCONNECT_EXCEPTION_OBJECT_OUTSIDE_REALITY_BUBBLE = 33
	SIMCONNECT_EXCEPTION_OBJECT_CONTAINER = 34
	SIMCONNECT_EXCEPTION_OBJECT_AI = 35
	SIMCONNECT_EXCEPTION_OBJECT_ATC = 36
	SIMCONNECT_EXCEPTION_OBJECT_SCHEDULE = 37


# Object types
class SIMCONNECT_SIMOBJECT_TYPE(CtypesEnum):
	SIMCONNECT_SIMOBJECT_TYPE_USER = 0
	SIMCONNECT_SIMOBJECT_TYPE_ALL = 1
	SIMCONNECT_SIMOBJECT_TYPE_AIRCRAFT = 2
	SIMCONNECT_SIMOBJECT_TYPE_HELICOPTER = 3
	SIMCONNECT_SIMOBJECT_TYPE_BOAT = 4
	SIMCONNECT_SIMOBJECT_TYPE_GROUND = 5


# EventState values
class SIMCONNECT_STATE(CtypesEnum):
	SIMCONNECT_STATE_OFF = 0
	SIMCONNECT_STATE_ON = 1


# Object Data Request Period values
class SIMCONNECT_PERIOD(CtypesEnum):  #
	SIMCONNECT_PERIOD_NEVER = 0
	SIMCONNECT_PERIOD_ONCE = 1
	SIMCONNECT_PERIOD_VISUAL_FRAME = 2
	SIMCONNECT_PERIOD_SIM_FRAME = 3
	SIMCONNECT_PERIOD_SECOND = 4


class SIMCONNECT_MISSION_END(CtypesEnum):  #
	SIMCONNECT_MISSION_FAILED = 0
	SIMCONNECT_MISSION_CRASHED = 1
	SIMCONNECT_MISSION_SUCCEEDED = 2


# ClientData Request Period values
class SIMCONNECT_CLIENT_DATA_PERIOD(CtypesEnum):  #
	SIMCONNECT_CLIENT_DATA_PERIOD_NEVER = 0
	SIMCONNECT_CLIENT_DATA_PERIOD_ONCE = 1
	SIMCONNECT_CLIENT_DATA_PERIOD_VISUAL_FRAME = 2
	SIMCONNECT_CLIENT_DATA_PERIOD_ON_SET = 3
	SIMCONNECT_CLIENT_DATA_PERIOD_SECOND = 4


class SIMCONNECT_TEXT_TYPE(CtypesEnum):  #
	SIMCONNECT_TEXT_TYPE_SCROLL_BLACK = 0
	SIMCONNECT_TEXT_TYPE_SCROLL_WHITE = 1
	SIMCONNECT_TEXT_TYPE_SCROLL_RED = 2
	SIMCONNECT_TEXT_TYPE_SCROLL_GREEN = 3
	SIMCONNECT_TEXT_TYPE_SCROLL_BLUE = 4
	SIMCONNECT_TEXT_TYPE_SCROLL_YELLOW = 5
	SIMCONNECT_TEXT_TYPE_SCROLL_MAGENTA = 6
	SIMCONNECT_TEXT_TYPE_SCROLL_CYAN = 7
	SIMCONNECT_TEXT_TYPE_PRINT_BLACK = 0x100
	SIMCONNECT_TEXT_TYPE_PRINT_WHITE = 0x101
	SIMCONNECT_TEXT_TYPE_PRINT_RED = 0x102
	SIMCONNECT_TEXT_TYPE_PRINT_GREEN = 0x103
	SIMCONNECT_TEXT_TYPE_PRINT_BLUE = 0x104
	SIMCONNECT_TEXT_TYPE_PRINT_YELLOW = 0x105
	SIMCONNECT_TEXT_TYPE_PRINT_MAGENTA = 0x106
	SIMCONNECT_TEXT_TYPE_PRINT_CYAN = 0x107
	SIMCONNECT_TEXT_TYPE_MENU = 0x0200


class SIMCONNECT_TEXT_RESULT(CtypesEnum):  #
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_1 = 0
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_2 = 1
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_3 = 2
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_4 = 3
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_5 = 4
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_6 = 5
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_7 = 6
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_8 = 7
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_9 = 8
	SIMCONNECT_TEXT_RESULT_MENU_SELECT_10 = 9
	SIMCONNECT_TEXT_RESULT_DISPLAYED = 0x10000
	SIMCONNECT_TEXT_RESULT_QUEUED = 0x10001
	SIMCONNECT_TEXT_RESULT_REMOVED = 0x1002
	SIMCONNECT_TEXT_RESULT_REPLACED = 0x10003
	SIMCONNECT_TEXT_RESULT_TIMEOUT = 0x10004


class SIMCONNECT_WEATHER_MODE(CtypesEnum):  #
	SIMCONNECT_WEATHER_MODE_THEME = 0
	SIMCONNECT_WEATHER_MODE_RWW = 1
	SIMCONNECT_WEATHER_MODE_CUSTOM = 2
	SIMCONNECT_WEATHER_MODE_GLOBAL = 3


class SIMCONNECT_FACILITY_LIST_TYPE(CtypesEnum):  #
	SIMCONNECT_FACILITY_LIST_TYPE_AIRPORT = 0
	SIMCONNECT_FACILITY_LIST_TYPE_WAYPOINT = 1
	SIMCONNECT_FACILITY_LIST_TYPE_NDB = 2
	SIMCONNECT_FACILITY_LIST_TYPE_VOR = 3
	SIMCONNECT_FACILITY_LIST_TYPE_COUNT = 4  # invalid


class SIMCONNECT_VOR_FLAGS(CtypesEn):  # flags for SIMCONNECT_RECV_ID_VOR_LIST
	SIMCONNECT_RECV_ID_VOR_LIST_HAS_NAV_SIGNAL = DWORD(0x00000001)  # Has Nav signal
	SIMCONNECT_RECV_ID_VOR_LIST_HAS_LOCALIZER = DWORD(0x00000002)  # Has localizer
	SIMCONNECT_RECV_ID_VOR_LIST_HAS_GLIDE_SLOPE = DWORD(0x00000004)  # Has Nav signal
	SIMCONNECT_RECV_ID_VOR_LIST_HAS_DME = DWORD(0x00000008)  # Station has DME


# bits for the Waypoint Flags field: may be combined
class SIMCONNECT_WAYPOINT_FLAGS(CtypesEn):  #
	SIMCONNECT_WAYPOINT_NONE = DWORD(0x00)  #
	SIMCONNECT_WAYPOINT_SPEED_REQUESTED = DWORD(
		0x04
	)  # requested speed at waypoint is valid
	SIMCONNECT_WAYPOINT_THROTTLE_REQUESTED = DWORD(
		0x08
	)  # request a specific throttle percentage
	SIMCONNECT_WAYPOINT_COMPUTE_VERTICAL_SPEED = DWORD(
		0x10
	)  # compute vertical to speed to reach waypoint altitude when crossing the waypoint
	SIMCONNECT_WAYPOINT_ALTITUDE_IS_AGL = DWORD(0x20)  # AltitudeIsAGL
	SIMCONNECT_WAYPOINT_ON_GROUND = DWORD(
		0x00100000
	)  # place this waypoint on the ground
	SIMCONNECT_WAYPOINT_REVERSE = DWORD(
		0x00200000
	)  # Back up to this waypoint. Only valid on first waypoint
	SIMCONNECT_WAYPOINT_WRAP_TO_FIRST = DWORD(
		0x00400000
	)  # Wrap around back to first waypoint. Only valid on last waypoint.


class SIMCONNECT_EVENT_FLAG(CtypesEn):  #
	SIMCONNECT_EVENT_FLAG_DEFAULT = DWORD(0x00000000)  #
	SIMCONNECT_EVENT_FLAG_FAST_REPEAT_TIMER = DWORD(
		0x00000001
	)  # set event repeat timer to simulate fast repeat
	SIMCONNECT_EVENT_FLAG_SLOW_REPEAT_TIMER = DWORD(
		0x00000002
	)  # set event repeat timer to simulate slow repeat
	SIMCONNECT_EVENT_FLAG_GROUPID_IS_PRIORITY = DWORD(
		0x00000010
	)  # interpret GroupID parameter as priority value


class SIMCONNECT_DATA_REQUEST_FLAG(CtypesEn):  #
	SIMCONNECT_DATA_REQUEST_FLAG_DEFAULT = DWORD(0x00000000)
	SIMCONNECT_DATA_REQUEST_FLAG_CHANGED = DWORD(
		0x00000001
	)  # send requested data when value(s) change
	SIMCONNECT_DATA_REQUEST_FLAG_TAGGED = DWORD(
		0x00000002
	)  # send requested data in tagged format


class SIMCONNECT_DATA_SET_FLAG(CtypesEn):  #
	SIMCONNECT_DATA_SET_FLAG_DEFAULT = DWORD(0x00000000)
	SIMCONNECT_DATA_SET_FLAG_TAGGED = DWORD(0x00000001)  # data is in tagged format


class SIMCONNECT_CREATE_CLIENT_DATA_FLAG(CtypesEn):  #
	SIMCONNECT_CREATE_CLIENT_DATA_FLAG_DEFAULT = DWORD(0x00000000)  #
	SIMCONNECT_CREATE_CLIENT_DATA_FLAG_READ_ONLY = DWORD(
		0x00000001
	)  # permit only ClientData creator to write into ClientData


class SIMCONNECT_CLIENT_DATA_REQUEST_FLAG(CtypesEn):  #
	SIMCONNECT_CLIENT_DATA_REQUEST_FLAG_DEFAULT = DWORD(0x00000000)  #
	SIMCONNECT_CLIENT_DATA_REQUEST_FLAG_CHANGED = DWORD(
		0x00000001
	)  # send requested ClientData when value(s) change
	SIMCONNECT_CLIENT_DATA_REQUEST_FLAG_TAGGED = DWORD(
		0x00000002
	)  # send requested ClientData in tagged format


class SIMCONNECT_CLIENT_DATA_SET_FLAG(CtypesEn):  #
	SIMCONNECT_CLIENT_DATA_SET_FLAG_DEFAULT = DWORD(0x00000000)  #
	SIMCONNECT_CLIENT_DATA_SET_FLAG_TAGGED = DWORD(
		0x00000001
	)  # data is in tagged format


class SIMCONNECT_VIEW_SYSTEM_EVENT_DATA(
	CtypesEn
):  # dwData contains these flags for the "View" System Event
	SIMCONNECT_VIEW_SYSTEM_EVENT_DATA_COCKPIT_2D = DWORD(
		0x00000001
	)  # 2D Panels in cockpit view
	SIMCONNECT_VIEW_SYSTEM_EVENT_DATA_COCKPIT_VIRTUAL = DWORD(
		0x00000002
	)  # Virtual (3D) panels in cockpit view
	SIMCONNECT_VIEW_SYSTEM_EVENT_DATA_ORTHOGONAL = DWORD(
		0x00000004
	)  # Orthogonal (Map) view


class SIMCONNECT_SOUND_SYSTEM_EVENT_DATA(
	CtypesEn
):  # dwData contains these flags for the "Sound" System Event
	SIMCONNECT_SOUND_SYSTEM_EVENT_DATA_MASTER = DWORD(0x00000001)  # Sound Master


class SIMCONNECT_PICK_FLAGS(CtypesEn):
	SIMCONNECT_PICK_GROUND = DWORD(
		0x01
	)  # pick ground/ pick result item is ground location
	SIMCONNECT_PICK_AI = DWORD(
		0x02
	)  # pick AI    / pick result item is AI, (dwSimObjectID is valid)
	SIMCONNECT_PICK_SCENERY = DWORD(
		0x04
	)  # pick scenery/ pick result item is scenery object (hSceneryObject is valid)
	SIMCONNECT_PICK_ALL = DWORD(
		0x04 | 0x02 | 0x01
	)  # pick all / (not valid on pick result item)
	SIMCONNECT_PICK_COORDSASPIXELS = DWORD(0x08)  #


# ----------------------------------------------------------------------------
#        User-defined enums
# ----------------------------------------------------------------------------
class SIMCONNECT_NOTIFICATION_GROUP_ID(
	AutoName
):  # client-defined notification group ID
	pass


class SIMCONNECT_INPUT_GROUP_ID(AutoName):  # client-defined input group ID
	pass


class SIMCONNECT_DATA_DEFINITION_ID(AutoName):  # client-defined data definition ID
	pass


class SIMCONNECT_DATA_REQUEST_ID(AutoName):  # client-defined request data ID
	pass


class SIMCONNECT_CLIENT_EVENT_ID(AutoName):  # client-defined client event ID
	EVENT_SIM_START = auto()
	EVENT_SIM_STOP = auto()
	EVENT_SIM_PAUSED = auto()
	EVENT_SIM_UNPAUSED = auto()
	pass


class SIMCONNECT_CLIENT_DATA_ID(AutoName):  # client-defined client data ID
	pass


class SIMCONNECT_CLIENT_DATA_DEFINITION_ID(
	AutoName
):  # client-defined client data definition ID
	pass


# ----------------------------------------------------------------------------
#        Struct definitions
# ----------------------------------------------------------------------------


class SIMCONNECT_RECV(Structure):
	_fields_ = [("dwSize", DWORD), ("dwVersion", DWORD), ("dwID", DWORD)]


class SIMCONNECT_RECV_EXCEPTION(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_EXCEPTION
	_fields_ = [
		("dwException", DWORD),  # see SIMCONNECT_EXCEPTION
		("UNKNOWN_SENDID", DWORD),  #
		("dwSendID", DWORD),  # see SimConnect_GetLastSentPacketID
		("UNKNOWN_INDEX", DWORD),  #
		("dwIndex", DWORD),  # index of parameter that was source of error
	]


class SIMCONNECT_RECV_OPEN(SIMCONNECT_RECV):  # when dwID == SIMCONNECT_RECV_ID_OPEN
	_fields_ = [
		("szApplicationName", c_char * 256),
		("dwApplicationVersionMajor", DWORD),
		("dwApplicationVersionMinor", DWORD),
		("dwApplicationBuildMajor", DWORD),
		("dwApplicationBuildMinor", DWORD),
		("dwSimConnectVersionMajor", DWORD),
		("dwSimConnectVersionMinor", DWORD),
		("dwSimConnectBuildMajor", DWORD),
		("dwSimConnectBuildMinor", DWORD),
		("dwReserved1", DWORD),
		("dwReserved2", DWORD),
	]


class SIMCONNECT_RECV_QUIT(SIMCONNECT_RECV):  # when dwID == SIMCONNECT_RECV_ID_QUIT
	pass


class SIMCONNECT_RECV_EVENT(SIMCONNECT_RECV):  # when dwID == SIMCONNECT_RECV_ID_EVENT
	UNKNOWN_GROUP = DWORD_MAX
	_fields_ = [
		("uGroupID", DWORD),
		("uEventID", DWORD),
		("dwData", DWORD),  # uEventID-dependent context
	]


class SIMCONNECT_RECV_EVENT_FILENAME(
	SIMCONNECT_RECV_EVENT
):  # when dwID == SIMCONNECT_RECV_ID_EVENT_FILENAME
	_fields_ = [
		("zFileName", c_char * MAX_PATH),  # uEventID-dependent context
		("dwFlags", DWORD),
	]


class SIMCONNECT_RECV_EVENT_OBJECT_ADDREMOVE(
	SIMCONNECT_RECV_EVENT
):  # when dwID == SIMCONNECT_RECV_ID_EVENT_FILENAME
	eObjType = SIMCONNECT_SIMOBJECT_TYPE


class SIMCONNECT_RECV_EVENT_FRAME(
	SIMCONNECT_RECV_EVENT
):  # when dwID == SIMCONNECT_RECV_ID_EVENT_FRAME
	_fields_ = [("fFrameRate", c_float), ("fSimSpeed", c_float)]


class SIMCONNECT_RECV_EVENT_MULTIPLAYER_SERVER_STARTED(SIMCONNECT_RECV_EVENT):
	# when dwID == SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SERVER_STARTED
	# No event specific data, for now
	pass


class SIMCONNECT_RECV_EVENT_MULTIPLAYER_CLIENT_STARTED(SIMCONNECT_RECV_EVENT):
	# when dwID == SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_CLIENT_STARTED
	# No event specific data, for now
	pass


class SIMCONNECT_RECV_EVENT_MULTIPLAYER_SESSION_ENDED(SIMCONNECT_RECV_EVENT):
	# when dwID == SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SESSION_ENDED
	# No event specific data, for now
	pass


# SIMCONNECT_DATA_RACE_RESULT
class SIMCONNECT_DATA_RACE_RESULT(Structure):
	_fields_ = [
		("dwNumberOfRacers", DWORD),  # The total number of racers
		("szPlayerName", c_char * MAX_PATH),  # The name of the player
		(
			"szSessionType",
			c_char * MAX_PATH,
		),  # The type of the multiplayer session: "LAN", "GAMESPY")
		("szAircraft", c_char * MAX_PATH),  # The aircraft type
		("szPlayerRole", c_char * MAX_PATH),  # The player role in the mission
		("fTotalTime", c_double),  # Total time in seconds, 0 means DNF
		("fPenaltyTime", c_double),  # Total penalty time in seconds
		(
			"MissionGUID",
			DWORD,
		),  # The name of the mission to execute, NULL if no mission
		("dwIsDisqualified", c_double),  # non 0 - disqualified, 0 - not disqualified
	]


class SIMCONNECT_RECV_EVENT_RACE_END(
	SIMCONNECT_RECV_EVENT
):  # when dwID == SIMCONNECT_RECV_ID_EVENT_RACE_END
	RacerData = SIMCONNECT_DATA_RACE_RESULT
	_fields_ = [("dwRacerNumber", DWORD)]  # The index of the racer the results are for


class SIMCONNECT_RECV_EVENT_RACE_LAP(
	SIMCONNECT_RECV_EVENT
):  # when dwID == SIMCONNECT_RECV_ID_EVENT_RACE_LAP
	RacerData = SIMCONNECT_DATA_RACE_RESULT
	_fields_ = [("dwLapIndex", DWORD)]  # The index of the lap the results are for


class SIMCONNECT_RECV_SIMOBJECT_DATA(SIMCONNECT_RECV):
	_fields_ = [
		("dwRequestID", DWORD),
		("dwObjectID", DWORD),
		("dwDefineID", DWORD),
		("dwFlags", DWORD),
		("dwentrynumber", DWORD),
		("dwoutof", DWORD),
		("dwDefineCount", DWORD),
		("dwData", DWORD * 8192),
	]


class SIMCONNECT_RECV_SIMOBJECT_DATA_BYTYPE(SIMCONNECT_RECV_SIMOBJECT_DATA):
	_fields_ = []


class SIMCONNECT_RECV_CLIENT_DATA(
	SIMCONNECT_RECV_SIMOBJECT_DATA
):  # when dwID == SIMCONNECT_RECV_ID_CLIENT_DATA
	_fields_ = []


class SIMCONNECT_RECV_WEATHER_OBSERVATION(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_WEATHER_OBSERVATION
	_fields_ = [
		("dwRequestID", DWORD),
		(
			"szMetar",
			c_char * MAX_METAR_LENGTH.value,
		),  # Variable length string whose maximum size is MAX_METAR_LENGTH
	]


SIMCONNECT_CLOUD_STATE_ARRAY_WIDTH = 64
SIMCONNECT_CLOUD_STATE_ARRAY_SIZE = (
	SIMCONNECT_CLOUD_STATE_ARRAY_WIDTH * SIMCONNECT_CLOUD_STATE_ARRAY_WIDTH
)


class SIMCONNECT_RECV_CLOUD_STATE(SIMCONNECT_RECV):
	# when dwID == SIMCONNECT_RECV_ID_CLOUD_STATE
	_fields_ = [
		("dwRequestID", DWORD),
		("dwArraySize", DWORD),
		# SIMCONNECT_FIXEDTYPE_DATAV(BYTE,    rgbData, dwArraySize, U1 /*member of UnmanagedType enum*/ , System::Byte /*cli type*/);
	]


class SIMCONNECT_RECV_ASSIGNED_OBJECT_ID(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_ASSIGNED_OBJECT_ID
	_fields_ = [("dwRequestID", DWORD), ("dwObjectID", DWORD)]


class SIMCONNECT_RECV_RESERVED_KEY(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_RESERVED_KEY
	_fields_ = [("szChoiceReserved", c_char * 30), ("szReservedKey", c_char * 30)]


class SIMCONNECT_RECV_SYSTEM_STATE(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_SYSTEM_STATE
	_fields_ = [
		("dwRequestID", DWORD),
		("dwInteger", DWORD),
		("fFloat", c_float),
		("szString", c_char * MAX_PATH),
	]


class SIMCONNECT_RECV_CUSTOM_ACTION(SIMCONNECT_RECV_EVENT):  #
	_fields_ = [
		("guidInstanceId", DWORD),  # Instance id of the action that executed
		("dwWaitForCompletion", DWORD),  # Wait for completion flag on the action
		(
			"szPayLoad",
			c_char,
		),  # Variable length string payload associated with the mission action.
	]


class SIMCONNECT_RECV_EVENT_WEATHER_MODE(SIMCONNECT_RECV_EVENT):  #
	_fields_ = (
		[]
	)  # No event specific data - the new weather mode is in the base structure dwData member.


# SIMCONNECT_RECV_FACILITIES_LIST
class SIMCONNECT_RECV_FACILITIES_LIST(SIMCONNECT_RECV):  #
	_fields_ = [
		("dwRequestID", DWORD),
		("dwArraySize", DWORD),
		(
			"dwEntryNumber",
			DWORD,
		),  # when the array of items is too big for one send, which send this is (0..dwOutOf-1)
		("dwOutOf", DWORD),  # total number of transmissions the list is chopped into
	]


# SIMCONNECT_DATA_FACILITY_AIRPORT
class SIMCONNECT_DATA_FACILITY_AIRPORT(Structure):  #
	_fields_ = [
		("Icao", c_char * 9),  # ICAO of the object
		("Latitude", c_double),  # degrees
		("Longitude", c_double),  # degrees
		("Altitude", c_double),  # meters
	]


# SIMCONNECT_RECV_AIRPORT_LIST
# class SIMCONNECT_RECV_AIRPORT_LIST(SIMCONNECT_RECV_FACILITIES_LIST):  #
# 	_fields_ = [
# 		("SIMCONNECT_DATA_FACILITY_AIRPORT", rgData * dwArraySize)
# 	]
#  SIMCONNECT_FIXEDTYPE_DATAV(SIMCONNECT_DATA_FACILITY_AIRPORT, rgData, dwArraySize,
#  U1 /*member of UnmanagedType enum*/, SIMCONNECT_DATA_FACILITY_AIRPORT /*cli type*/);


# SIMCONNECT_DATA_FACILITY_WAYPOINT
class SIMCONNECT_DATA_FACILITY_WAYPOINT(SIMCONNECT_DATA_FACILITY_AIRPORT):  #
	_fields_ = [("fMagVar", c_float)]  # Magvar in degrees


# SIMCONNECT_RECV_WAYPOINT_LIST
# class SIMCONNECT_RECV_WAYPOINT_LIST(SIMCONNECT_RECV_FACILITIES_LIST):  #
# 	_fields_ = [
# 		("", )
# 	]
#    SIMCONNECT_FIXEDTYPE_DATAV(SIMCONNECT_DATA_FACILITY_WAYPOINT,
#   rgData
#   dwArraySize,
#    U1 /*member of UnmanagedType enum*/,
#   SIMCONNECT_DATA_FACILITY_WAYPOINT /*cli type*/);


# SIMCONNECT_DATA_FACILITY_NDB
class SIMCONNECT_DATA_FACILITY_NDB(SIMCONNECT_DATA_FACILITY_WAYPOINT):  #
	_fields_ = [("fFrequency", DWORD)]  # frequency in Hz


# SIMCONNECT_RECV_NDB_LIST
# class SIMCONNECT_RECV_NDB_LIST(SIMCONNECT_RECV_FACILITIES_LIST):  #
# 	_fields_ = [
# 		("", )
# 	]
#    SIMCONNECT_FIXEDTYPE_DATAV(SIMCONNECT_DATA_FACILITY_NDB,
#   rgData
#   dwArraySize,
#    U1 /*member of UnmanagedType enum*/,
#   SIMCONNECT_DATA_FACILITY_NDB /*cli type*/);


# SIMCONNECT_DATA_FACILITY_VOR
class SIMCONNECT_DATA_FACILITY_VOR(SIMCONNECT_DATA_FACILITY_NDB):  #
	_fields_ = [
		("Flags", DWORD),  # SIMCONNECT_VOR_FLAGS
		("fLocalizer", c_float),  # Localizer in degrees
		("GlideLat", c_double),  # Glide Slope Location (deg, deg, meters)
		("GlideLon", c_double),  #
		("GlideAlt", c_double),  #
		("fGlideSlopeAngle", c_float),  # Glide Slope in degrees
	]


# SIMCONNECT_RECV_VOR_LIST
# class SIMCONNECT_RECV_VOR_LIST(SIMCONNECT_RECV_FACILITIES_LIST):  #
# 	_fields_ = [
# 		("", )
# 	]
#    SIMCONNECT_FIXEDTYPE_DATAV(SIMCONNECT_DATA_FACILITY_VOR,
#   rgData
#   dwArraySize,
# 		 U1 /*member of UnmanagedType enum*/, SIMCONNECT_DATA_FACILITY_VOR /*cli type*/);


class SIMCONNECT_RECV_PICK(
	SIMCONNECT_RECV
):  # when dwID == SIMCONNECT_RECV_ID_RESERVED_KEY
	_fields_ = [
		("hContext", HANDLE),
		("dwFlags", DWORD),
		("Latitude", c_double),  # degrees
		("Longitude", c_double),  # degrees
		("Altitude", c_double),  # feet
		("xPos", c_int),  # reserved
		("yPos", c_int),  # reserved
		("dwSimObjectID", DWORD),
		("hSceneryObject", HANDLE),
		(
			"dwentrynumber",
			DWORD,
		),  # if multiple objects returned, this is number <entrynumber> out of <outof>.
		("dwoutof", DWORD),  # note:  starts with 1, not 0.
	]


# SIMCONNECT_DATATYPE_INITPOSITION
class SIMCONNECT_DATA_INITPOSITION(Structure):  #
	_fields_ = [
		("Latitude", c_double),  # degrees
		("Longitude", c_double),  # degrees
		("Altitude", c_double),  # feet
		("Pitch", c_double),  # degrees
		("Bank", c_double),  # degrees
		("Heading", c_double),  # degrees
		("OnGround", DWORD),  # 1=force to be on the ground
		("Airspeed", DWORD),  # knots
	]


# SIMCONNECT_DATATYPE_MARKERSTATE
class SIMCONNECT_DATA_MARKERSTATE(Structure):  #
	_fields_ = [("szMarkerName", c_char * 64), ("dwMarkerState", DWORD)]


# SIMCONNECT_DATATYPE_WAYPOINT
class SIMCONNECT_DATA_WAYPOINT(Structure):  #
	_fields_ = [
		("Latitude", c_double),  # degrees
		("Longitude", c_double),  # degrees
		("Altitude", c_double),  # feet
		("Flags", c_ulong),
		("ktsSpeed", c_double),  # knots
		("percentThrottle", c_double),
	]


# SIMCONNECT_DATA_LATLONALT
class SIMCONNECT_DATA_LATLONALT(Structure):  #
	_fields_ = [("Latitude", c_double), ("Longitude", c_double), ("Altitude", c_double)]


# SIMCONNECT_DATA_XYZ
class SIMCONNECT_DATA_XYZ(Structure):  #
	_fields_ = [("x", c_double), ("y", c_double), ("z", c_double)]

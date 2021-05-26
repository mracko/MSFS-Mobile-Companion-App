from ctypes import *
from ctypes.wintypes import *
import logging
import time
from .Enum import *
from .Constants import *
from .Attributes import *
import os
import threading
import asyncio

_library_path = os.path.abspath(__file__).replace(".py", ".dll")

LOGGER = logging.getLogger(__name__)


def millis():
	return int(round(time.time() * 1000))


class SimConnect:

	def IsHR(self, hr, value):
		_hr = ctypes.HRESULT(hr)
		return ctypes.c_ulong(_hr.value).value == value

	def handle_id_event(self, event):
		uEventID = event.uEventID
		if uEventID == self.dll.EventID.EVENT_SIM_START:
			LOGGER.info("SIM START")
			self.running = True
		if uEventID == self.dll.EventID.EVENT_SIM_STOP:
			LOGGER.info("SIM Stop")
			self.running = False
		# Unknow whay not reciving
		if uEventID == self.dll.EventID.EVENT_SIM_PAUSED:
			LOGGER.info("SIM Paused")
			self.paused = True
		if uEventID == self.dll.EventID.EVENT_SIM_UNPAUSED:
			LOGGER.info("SIM Unpaused")
			self.paused = False

	def handle_simobject_event(self, ObjData):
		dwRequestID = ObjData.dwRequestID
		if dwRequestID in self.Requests:
			_request = self.Requests[dwRequestID]
			rtype = _request.definitions[0][1].decode()
			if 'string' in rtype.lower():
				pS = cast(ObjData.dwData, c_char_p)
				_request.outData = pS.value
			else:
				_request.outData = cast(
					ObjData.dwData, POINTER(c_double * len(_request.definitions))
				).contents[0]
		else:
			LOGGER.warn("Event ID: %d Not Handled." % (dwRequestID))

	def handle_exception_event(self, exc):
		_exception = SIMCONNECT_EXCEPTION(exc.dwException).name
		_unsendid = exc.UNKNOWN_SENDID
		_sendid = exc.dwSendID
		_unindex = exc.UNKNOWN_INDEX
		_index = exc.dwIndex

		# request exceptions
		for _reqin in self.Requests:
			_request = self.Requests[_reqin]
			if _request.LastID == _unsendid:
				LOGGER.warn("%s: in %s" % (_exception, _request.definitions[0]))
				return

		#LOGGER.warn(_exception)

	def handle_state_event(self, pData):
		print("I:", pData.dwInteger, "F:", pData.fFloat, "S:", pData.szString)

	# TODO: update callbackfunction to expand functions.
	def my_dispatch_proc(self, pData, cbData, pContext):
		# print("my_dispatch_proc")
		dwID = pData.contents.dwID
		if dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_EVENT:
			evt = cast(pData, POINTER(SIMCONNECT_RECV_EVENT)).contents
			self.handle_id_event(evt)

		elif dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SYSTEM_STATE:
			state = cast(pData, POINTER(SIMCONNECT_RECV_SYSTEM_STATE)).contents
			self.handle_state_event(state)

		elif dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE:
			pObjData = cast(
				pData, POINTER(SIMCONNECT_RECV_SIMOBJECT_DATA_BYTYPE)
			).contents
			self.handle_simobject_event(pObjData)

		elif dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_OPEN:
			LOGGER.info("SIM OPEN")
			self.ok = True

		elif dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_EXCEPTION:
			exc = cast(pData, POINTER(SIMCONNECT_RECV_EXCEPTION)).contents
			self.handle_exception_event(exc)

		elif (dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_AIRPORT_LIST) or (
			dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_WAYPOINT_LIST) or (
			dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_NDB_LIST) or (
			dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_VOR_LIST):
			pObjData = cast(
				pData, POINTER(SIMCONNECT_RECV_FACILITIES_LIST)
			).contents
			dwRequestID = pObjData.dwRequestID
			for _facilitie in self.Facilities:
				if dwRequestID == _facilitie.REQUEST_ID.value:
					_facilitie.parent.dump(pData)
					_facilitie.dump(pData)

		elif dwID == SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_QUIT:
			self.quit = 1
		else:
			LOGGER.debug("Received:", SIMCONNECT_RECV_ID(dwID))
		return

	def __init__(self, auto_connect=True, library_path=_library_path):

		self.Requests = {}
		self.Facilities = []
		self.dll = SimConnectDll(library_path)
		self.hSimConnect = HANDLE()
		self.quit = 0
		self.ok = False
		self.running = False
		self.paused = False
		self.DEFINITION_POS = None
		self.DEFINITION_WAYPOINT = None
		self.my_dispatch_proc_rd = self.dll.DispatchProc(self.my_dispatch_proc)
		if auto_connect:
			self.connect()

	def connect(self):
		try:
			err = self.dll.Open(
				byref(self.hSimConnect), LPCSTR(b"Request Data"), None, 0, 0, 0
			)
			if self.IsHR(err, 0):
				LOGGER.debug("Connected to Flight Simulator!")
				# Request an event when the simulation starts

				# The user is in control of the aircraft
				self.dll.SubscribeToSystemEvent(
					self.hSimConnect, self.dll.EventID.EVENT_SIM_START, b"SimStart"
				)
				# The user is navigating the UI.
				self.dll.SubscribeToSystemEvent(
					self.hSimConnect, self.dll.EventID.EVENT_SIM_STOP, b"SimStop"
				)
				# Request a notification when the flight is paused
				self.dll.SubscribeToSystemEvent(
					self.hSimConnect, self.dll.EventID.EVENT_SIM_PAUSED, b"Paused"
				)
				# Request a notification when the flight is un-paused.
				self.dll.SubscribeToSystemEvent(
					self.hSimConnect, self.dll.EventID.EVENT_SIM_UNPAUSED, b"Unpaused"
				)
				self.timerThread = threading.Thread(target=self._run)
				self.timerThread.daemon = True
				self.timerThread.start()
				while self.ok is False:
					pass
		except OSError:
			LOGGER.debug("Did not find Flight Simulator running.")
			raise ConnectionError("Did not find Flight Simulator running.")

	def _run(self):
		while self.quit == 0:
			self.dll.CallDispatch(self.hSimConnect, self.my_dispatch_proc_rd, None)
			time.sleep(.002)

	def exit(self):
		self.quit = 1
		self.timerThread.join()
		self.dll.Close(self.hSimConnect)

	def map_to_sim_event(self, name):
		for m in self.dll.EventID:
			if name.decode() == m.name:
				LOGGER.debug("Already have event: ", m)
				return m

		names = [m.name for m in self.dll.EventID] + [name.decode()]
		self.dll.EventID = Enum(self.dll.EventID.__name__, names)
		evnt = list(self.dll.EventID)[-1]
		err = self.dll.MapClientEventToSimEvent(self.hSimConnect, evnt.value, name)
		if self.IsHR(err, 0):
			return evnt
		else:
			LOGGER.error("Error: MapToSimEvent")
			return None

	def add_to_notification_group(self, group, evnt, bMaskable=False):
		self.dll.AddClientEventToNotificationGroup(
			self.hSimConnect, group, evnt, bMaskable
		)

	def request_data(self, _Request):
		_Request.outData = None
		self.dll.RequestDataOnSimObjectType(
			self.hSimConnect,
			_Request.DATA_REQUEST_ID.value,
			_Request.DATA_DEFINITION_ID.value,
			0,
			SIMCONNECT_SIMOBJECT_TYPE.SIMCONNECT_SIMOBJECT_TYPE_USER,
		)
		temp = DWORD(0)
		self.dll.GetLastSentPacketID(self.hSimConnect, temp)
		_Request.LastID = temp.value

	def set_data(self, _Request):
		rtype = _Request.definitions[0][1].decode()
		if 'string' in rtype.lower():
			pyarr = bytearray(_Request.outData)
			dataarray = (ctypes.c_char * len(pyarr))(*pyarr)
		else:
			pyarr = list([_Request.outData])
			dataarray = (ctypes.c_double * len(pyarr))(*pyarr)

		pObjData = cast(
			dataarray, c_void_p
		)
		err = self.dll.SetDataOnSimObject(
			self.hSimConnect,
			_Request.DATA_DEFINITION_ID.value,
			SIMCONNECT_SIMOBJECT_TYPE.SIMCONNECT_SIMOBJECT_TYPE_USER,
			0,
			0,
			sizeof(ctypes.c_double) * len(pyarr),
			pObjData
		)
		if self.IsHR(err, 0):
			# LOGGER.debug("Request Sent")
			return True
		else:
			return False

	async def get_return_data(self, _Request):
		while _Request.outData is None:
			await asyncio.sleep(0.01)

	async def get_data(self, _Request):
		self.request_data(_Request)
		await self.get_return_data(_Request)

	def send_event(self, evnt, data=DWORD(0)):
		err = self.dll.TransmitClientEvent(
			self.hSimConnect,
			SIMCONNECT_OBJECT_ID_USER,
			evnt.value,
			data,
			SIMCONNECT_GROUP_PRIORITY_HIGHEST,
			DWORD(16),
		)

		if self.IsHR(err, 0):
			# LOGGER.debug("Event Sent")
			return True
		else:
			return False

	def new_def_id(self):
		_name = "Definition" + str(len(list(self.dll.DATA_DEFINITION_ID)))
		names = [m.name for m in self.dll.DATA_DEFINITION_ID] + [_name]

		self.dll.DATA_DEFINITION_ID = Enum(self.dll.DATA_DEFINITION_ID.__name__, names)
		DEFINITION_ID = list(self.dll.DATA_DEFINITION_ID)[-1]
		return DEFINITION_ID

	def new_request_id(self):
		name = "Request" + str(len(self.dll.DATA_REQUEST_ID))
		names = [m.name for m in self.dll.DATA_REQUEST_ID] + [name]
		self.dll.DATA_REQUEST_ID = Enum(self.dll.DATA_REQUEST_ID.__name__, names)
		REQUEST_ID = list(self.dll.DATA_REQUEST_ID)[-1]

		return REQUEST_ID

	def add_waypoints(self, _waypointlist):
		if self.DEFINITION_WAYPOINT is None:
			self.DEFINITION_WAYPOINT = self.new_def_id()
			err = self.dll.AddToDataDefinition(
				self.hSimConnect,
				self.DEFINITION_WAYPOINT.value,
				b'AI WAYPOINT LIST',
				b'number',
				SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_WAYPOINT,
				0,
				SIMCONNECT_UNUSED,
			)
		pyarr = []
		for waypt in _waypointlist:
			for e in waypt._fields_:
				pyarr.append(getattr(waypt, e[0]))
		dataarray = (ctypes.c_double * len(pyarr))(*pyarr)
		pObjData = cast(
			dataarray, c_void_p
		)
		sx = int(sizeof(ctypes.c_double) * (len(pyarr) / len(_waypointlist)))
		return
		hr = self.dll.SetDataOnSimObject(
			self.hSimConnect,
			self.DEFINITION_WAYPOINT.value,
			SIMCONNECT_OBJECT_ID_USER,
			0,
			len(_waypointlist),
			sx,
			pObjData
		)
		if self.IsHR(err, 0):
			return True
		else:
			return False

	def set_pos(
		self,
		_Altitude,
		_Latitude,
		_Longitude,
		_Airspeed,
		_Pitch=0.0,
		_Bank=0.0,
		_Heading=0,
		_OnGround=0,
	):
		Init = SIMCONNECT_DATA_INITPOSITION()
		Init.Altitude = _Altitude
		Init.Latitude = _Latitude
		Init.Longitude = _Longitude
		Init.Pitch = _Pitch
		Init.Bank = _Bank
		Init.Heading = _Heading
		Init.OnGround = _OnGround
		Init.Airspeed = _Airspeed

		if self.DEFINITION_POS is None:
			self.DEFINITION_POS = self.new_def_id("DEFINITION_POS")
			err = self.dll.AddToDataDefinition(
				self.hSimConnect,
				self.DEFINITION_POS.value,
				b'Initial Position',
				b'',
				SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_INITPOSITION,
				0,
				SIMCONNECT_UNUSED,
			)

		hr = self.dll.SetDataOnSimObject(
			self.hSimConnect,
			self.DEFINITION_POS.value,
			SIMCONNECT_OBJECT_ID_USER,
			0,
			0,
			sizeof(Init),
			pointer(Init)
		)
		if self.IsHR(hr, 0):
			return True
		else:
			return False

	def load_flight(self, flt_path):
		hr = self.dll.FlightLoad(self.hSimConnect, flt_path.encode())
		if self.IsHR(hr, 0):
			return True
		else:
			return False

	def load_flight_plan(self, pln_path):
		hr = self.dll.FlightPlanLoad(self.hSimConnect, pln_path.encode())
		if self.IsHR(hr, 0):
			return True
		else:
			return False

	def save_flight(
		self,
		flt_path,
		flt_title,
		flt_description,
		flt_mission_type='FreeFlight',
		flt_mission_location='Custom departure',
		flt_original_flight='',
		flt_flight_type='NORMAL'):
		hr = self.dll.FlightSave(self.hSimConnect, flt_path.encode(), flt_title.encode(), flt_description.encode(), 0)
		if not self.IsHR(hr, 0):
			return False

		dicp = self.flight_to_dic(flt_path)
		if 'MissionType' not in dicp['Main']:
			dicp['Main']['MissionType'] = flt_mission_type

		if 'MissionLocation' not in dicp['Main']:
			dicp['Main']['MissionLocation'] = flt_mission_location

		if 'FlightType' not in dicp['Main']:
			dicp['Main']['FlightType'] = flt_flight_type

		if 'OriginalFlight' not in dicp['Main']:
			dicp['Main']['OriginalFlight'] = flt_original_flight
		self.dic_to_flight(dicp, flt_path)

		return False

	def get_paused(self):
		hr = self.dll.RequestSystemState(
			self.hSimConnect,
			self.dll.EventID.EVENT_SIM_PAUSED,
			b"Sim"
		)

	def dic_to_flight(self, dic, fpath):
		with open(fpath, "w") as tempfile:
			for root in dic:
				tempfile.write("\n[%s]\n" % root)
				for member in dic[root]:
					tempfile.write("%s=%s\n" % (member, dic[root][member]))

	def flight_to_dic(self, fpath):
		while not os.path.isfile(fpath):
			pass
		time.sleep(0.5)
		dic = {}
		index = ""
		with open(fpath, "r") as tempfile:
			for line in tempfile.readlines():
				if line[0] == '[':
					index = line[1:-2]
					dic[index] = {}
				else:
					if index != "" and line != '\n':
						temp = line.split("=")
						dic[index][temp[0]] = temp[1].strip()
		return dic

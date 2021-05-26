from SimConnect import *
from .Enum import *
from .Constants import *


class Facilitie(object):
	def __init__(self):
		pass


class FacilitiesHelper:
	def __init__(self, _sm, _parent):
		self.sm = _sm
		self.parent = _parent
		self.REQUEST_ID = _sm.new_request_id()
		self.item = None
		self.sm.Facilities.append(self)

	def subscribe(self, _cbfunc):
		if self.item < SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_COUNT:
			self.cb = _cbfunc
			hr = self.sm.dll.SubscribeToFacilities(
				self.sm.hSimConnect,
				SIMCONNECT_FACILITY_LIST_TYPE(self.item),
				self.REQUEST_ID.value
			)

	def unsubscribe(self):
		self.cb = None
		hr = self.sm.dll.UnsubscribeToFacilities(
			self.sm.hSimConnect,
			SIMCONNECT_FACILITY_LIST_TYPE(self.item)
		)

	def get(self):
		# Get the current cached list of airports, waypoints, etc, as the item indicates
		if self.item < SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_COUNT:
			hr = self.sm.dll.RequestFacilitiesList(
				self.sm.hSimConnect,
				SIMCONNECT_FACILITY_LIST_TYPE(self.item),
				self.REQUEST_ID.value
			)
			# self.sm.run()


class FacilitiesRequests():
	def __init__(self, _sm):
		self.sm = _sm
		self.list = []
		self.Airports = self.__FACILITY_AIRPORT(_sm, self)
		self.list.append(self.Airports)
		self.Waypoints = self.__FACILITY_WAYPOINT(_sm, self)
		self.list.append(self.Waypoints)
		self.NDBs = self.__FACILITY_NDB(_sm, self)
		self.list.append(self.NDBs)
		self.VORs = self.__FACILITY_VOR(_sm, self)
		self.list.append(self.VORs)

	def dump(self, pList):
		pList = cast(pList, POINTER(SIMCONNECT_RECV_FACILITIES_LIST))
		List = pList.contents
		print("RequestID: %d  dwArraySize: %d  dwEntryNumber: %d  dwOutOf: %d" % (
			List.dwRequestID, List.dwArraySize, List.dwEntryNumber, List.dwOutOf)
		)

	# Dump various facility elements
	class __FACILITY_AIRPORT(FacilitiesHelper):
		def __init__(self, _sm, _parent):
			super().__init__(_sm, _parent)
			self.item = SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_AIRPORT

		def dump(self, pFac):
			pFac = cast(pFac, POINTER(SIMCONNECT_DATA_FACILITY_AIRPORT))
			Fac = pFac.contents
			print("Icao: %s  Latitude: %lg  Longitude: %lg  Altitude: %lg" % (
				Fac.Icao.decode(), Fac.Latitude, Fac.Longitude, Fac.Altitude)
			)

	class __FACILITY_WAYPOINT(FacilitiesHelper):
		def __init__(self, _sm, _parent):
			super().__init__(_sm, _parent)
			self.item = SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_WAYPOINT

		def dump(self, pFac):
			pFac = cast(pFac, POINTER(SIMCONNECT_DATA_FACILITY_WAYPOINT))
			Fac = pFac.contents
			self.parent.Airports.dump(pFac)
			print("\tfMagVar: %g" % (Fac.fMagVar))

	class __FACILITY_NDB(FacilitiesHelper):
		def __init__(self, _sm, _parent):
			super().__init__(_sm, _parent)
			self.item = SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_NDB

		def dump(self, pFac):
			pFac = cast(pFac, POINTER(SIMCONNECT_DATA_FACILITY_NDB))
			Fac = pFac.contents
			self.parent.Waypoints.dump(pFac)
			print("\t\tfFrequency: %d" % (Fac.fFrequency))

	class __FACILITY_VOR(FacilitiesHelper):
		def __init__(self, _sm, _parent):
			super().__init__(_sm, _parent)
			self.item = SIMCONNECT_FACILITY_LIST_TYPE.SIMCONNECT_FACILITY_LIST_TYPE_VOR

		def dump(self, pFac):
			pFac = cast(pFac, POINTER(SIMCONNECT_DATA_FACILITY_VOR))
			Fac = pFac.contents
			self.parent.NDBs.dump(pFac)
			print("\t\t\tFlags: %x  fLocalizer: %f  GlideLat: %lg  GlideLon: %lg  GlideAlt: %lg  fGlideSlopeAngle: %f" % (
				Fac.Flags, Fac.fLocalizer, Fac.GlideLat, Fac.GlideLon, Fac.GlideAlt, Fac.fGlideSlopeAngle)
			)

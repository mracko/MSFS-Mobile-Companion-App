from .Enum import *
from .Constants import *
from ctypes import *
from ctypes.wintypes import *


class SimConnectDll(object):

	def __init__(self, library_path):
		self.EventID = SIMCONNECT_CLIENT_EVENT_ID
		self.DATA_DEFINITION_ID = SIMCONNECT_DATA_DEFINITION_ID
		self.DATA_REQUEST_ID = SIMCONNECT_DATA_REQUEST_ID
		self.GROUP_ID = SIMCONNECT_NOTIFICATION_GROUP_ID
		self.INPUT_GROUP_ID = SIMCONNECT_INPUT_GROUP_ID
		self.CLIENT_DATA_ID = SIMCONNECT_CLIENT_DATA_ID
		self.CLIENT_DATA_DEFINITION_ID = SIMCONNECT_CLIENT_DATA_DEFINITION_ID

		self.SimConnect = cdll.LoadLibrary(library_path)
		# SIMCONNECTAPI SimConnect_Open(
		# 	HANDLE * phSimConnect,
		# 	LPCSTR szName,
		# 	HWND hWnd,
		# 	DWORD UserEventWin32,
		# 	HANDLE hEventHandle,
		# 	DWORD ConfigIndex)

		self.Open = self.SimConnect.SimConnect_Open
		self.Open.restype = HRESULT
		self.Open.argtypes = [POINTER(HANDLE), LPCSTR, HWND, DWORD, HANDLE, DWORD]

		# SIMCONNECTAPI SimConnect_Close(
		# 	HANDLE hSimConnect);

		self.Close = self.SimConnect.SimConnect_Close
		self.Close.restype = HRESULT
		self.Close.argtypes = [HANDLE]

		# SIMCONNECTAPI SimConnect_AddToDataDefinition(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_DATA_DEFINITION_ID DefineID,
		# 	const char * DatumName,
		# 	const char * UnitsName,
		# 	SIMCONNECT_DATATYPE DatumType = SIMCONNECT_DATATYPE_FLOAT64,
		# 	float fEpsilon = 0,
		# 	DWORD DatumID = SIMCONNECT_UNUSED);

		self.AddToDataDefinition = self.SimConnect.SimConnect_AddToDataDefinition
		self.AddToDataDefinition.restype = HRESULT
		self.AddToDataDefinition.argtypes = [
			HANDLE,
			self.DATA_DEFINITION_ID,
			c_char_p,
			c_char_p,
			SIMCONNECT_DATATYPE,
			c_float,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_SubscribeToSystemEvent(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_CLIENT_EVENT_ID EventID,
		# 	const char * SystemEventName);

		self.SubscribeToSystemEvent = (
			self.SimConnect.SimConnect_SubscribeToSystemEvent
		)
		self.SubscribeToSystemEvent.restype = HRESULT
		self.SubscribeToSystemEvent.argtypes = [HANDLE, self.EventID, c_char_p]

		# SIMCONNECTAPI SimConnect_CallDispatch(
		# 	HANDLE hSimConnect,
		# 	DispatchProc pfcnDispatch,
		# 	void * pContext);

		self.DispatchProc = CFUNCTYPE(c_void_p, POINTER(SIMCONNECT_RECV), DWORD, c_void_p)

		self.CallDispatch = self.SimConnect.SimConnect_CallDispatch
		self.CallDispatch.restype = HRESULT
		self.CallDispatch.argtypes = [HANDLE, self.DispatchProc, c_void_p]

		# SIMCONNECTAPI SimConnect_RequestDataOnSimObjectType(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_DATA_REQUEST_ID RequestID,
		# 	SIMCONNECT_DATA_DEFINITION_ID DefineID,
		# 	DWORD dwRadiusMeters,
		# 	SIMCONNECT_SIMOBJECT_TYPE type);

		self.RequestDataOnSimObjectType = (
			self.SimConnect.SimConnect_RequestDataOnSimObjectType
		)
		self.RequestDataOnSimObjectType.restype = HRESULT
		self.RequestDataOnSimObjectType.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			self.DATA_DEFINITION_ID,
			DWORD,
			SIMCONNECT_SIMOBJECT_TYPE,
		]

		# SIMCONNECTAPI SimConnect_TransmitClientEvent(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_OBJECT_ID ObjectID,
		# 	SIMCONNECT_CLIENT_EVENT_ID EventID,
		# 	DWORD dwData,
		# 	SIMCONNECT_NOTIFICATION_GROUP_ID GroupID,
		# 	SIMCONNECT_EVENT_FLAG Flags);

		self.TransmitClientEvent = self.SimConnect.SimConnect_TransmitClientEvent
		self.TransmitClientEvent.restype = HRESULT
		self.TransmitClientEvent.argtypes = [
			HANDLE,
			SIMCONNECT_OBJECT_ID,
			self.EventID,
			DWORD,
			DWORD,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_MapClientEventToSimEvent(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_CLIENT_EVENT_ID EventID,
		# 	const char * EventName = "");

		self.MapClientEventToSimEvent = (
			self.SimConnect.SimConnect_MapClientEventToSimEvent
		)
		self.MapClientEventToSimEvent.restype = HRESULT
		self.MapClientEventToSimEvent.argtypes = [HANDLE, self.EventID, c_char_p]

		# SIMCONNECTAPI SimConnect_AddClientEventToNotificationGroup(
		# 	HANDLE hSimConnect,
		# 	SIMCONNECT_NOTIFICATION_GROUP_ID GroupID,
		# 	SIMCONNECT_CLIENT_EVENT_ID EventID,
		# 	BOOL bMaskable = FALSE);

		self.AddClientEventToNotificationGroup = (
			self.SimConnect.SimConnect_AddClientEventToNotificationGroup
		)
		self.AddClientEventToNotificationGroup.restype = HRESULT
		self.AddClientEventToNotificationGroup.argtypes = [
			HANDLE,
			self.GROUP_ID,
			self.EventID,
			c_bool,
		]

		# SIMCONNECTAPI SimConnect_SetSystemEventState(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID EventID
		#   SIMCONNECT_STATE dwState);
		self.SetSystemEventState = self.SimConnect.SimConnect_SetSystemEventState
		self.SetSystemEventState.restype = HRESULT
		self.SetSystemEventState.argtypes = [HANDLE, self.EventID, SIMCONNECT_STATE]

		# SIMCONNECTAPI SimConnect_AddClientEventToNotificationGroup(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_NOTIFICATION_GROUP_ID GroupID
		#   SIMCONNECT_CLIENT_EVENT_ID EventID
		#   BOOL bMaskable = FALSE);
		self.AddClientEventToNotificationGroup = (
			self.SimConnect.SimConnect_AddClientEventToNotificationGroup
		)
		self.AddClientEventToNotificationGroup.restype = HRESULT
		self.AddClientEventToNotificationGroup.argtypes = [
			HANDLE,
			self.GROUP_ID,
			self.EventID,
			c_bool,
		]

		# SIMCONNECTAPI SimConnect_RemoveClientEvent(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_NOTIFICATION_GROUP_ID GroupID
		#   SIMCONNECT_CLIENT_EVENT_ID EventID);
		self.RemoveClientEvent = self.SimConnect.SimConnect_RemoveClientEvent
		self.RemoveClientEvent.restype = HRESULT
		self.RemoveClientEvent.argtypes = [HANDLE, self.GROUP_ID, self.EventID]

		# SIMCONNECTAPI SimConnect_SetNotificationGroupPriority(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_NOTIFICATION_GROUP_ID GroupID
		#   DWORD uPriority);
		self.SetNotificationGroupPriority = (
			self.SimConnect.SimConnect_SetNotificationGroupPriority
		)
		self.SetNotificationGroupPriority.restype = HRESULT
		self.SetNotificationGroupPriority.argtypes = [HANDLE, self.GROUP_ID, DWORD]

		# SIMCONNECTAPI SimConnect_ClearNotificationGroup(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_NOTIFICATION_GROUP_ID GroupID);
		self.ClearNotificationGroup = (
			self.SimConnect.SimConnect_ClearNotificationGroup
		)
		self.ClearNotificationGroup.restype = HRESULT
		self.ClearNotificationGroup.argtypes = [HANDLE, self.GROUP_ID]

		# SIMCONNECTAPI SimConnect_RequestNotificationGroup(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_NOTIFICATION_GROUP_ID GroupID
		#   DWORD dwReserved = 0
		#   DWORD Flags = 0);
		self.RequestNotificationGroup = (
			self.SimConnect.SimConnect_RequestNotificationGroup
		)
		self.RequestNotificationGroup.restype = HRESULT
		self.RequestNotificationGroup.argtypes = [HANDLE, self.GROUP_ID, DWORD, DWORD]

		# SIMCONNECTAPI SimConnect_ClearDataDefinition(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_DEFINITION_ID DefineID);
		self.ClearDataDefinition = self.SimConnect.SimConnect_ClearDataDefinition
		self.ClearDataDefinition.restype = HRESULT
		self.ClearDataDefinition.argtypes = [HANDLE, self.DATA_DEFINITION_ID]

		# SIMCONNECTAPI SimConnect_RequestDataOnSimObject(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   SIMCONNECT_DATA_DEFINITION_ID DefineID
		#   SIMCONNECT_OBJECT_ID ObjectID
		#   SIMCONNECT_PERIOD Period
		#   SIMCONNECT_DATA_REQUEST_FLAG Flags = 0
		#   DWORD origin = 0
		#   DWORD interval = 0
		#   DWORD limit = 0);
		self.RequestDataOnSimObject = (
			self.SimConnect.SimConnect_RequestDataOnSimObject
		)
		self.RequestDataOnSimObject.restype = HRESULT
		self.RequestDataOnSimObject.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			self.DATA_DEFINITION_ID,
			SIMCONNECT_OBJECT_ID,
			SIMCONNECT_PERIOD,
			SIMCONNECT_DATA_REQUEST_FLAG,
			DWORD,
			DWORD,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_SetDataOnSimObject(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_DEFINITION_ID DefineID
		#   SIMCONNECT_OBJECT_ID ObjectID
		#   SIMCONNECT_DATA_SET_FLAG Flags
		#   DWORD ArrayCount
		#   DWORD cbUnitSize
		#   void * pDataSet);
		self.SetDataOnSimObject = self.SimConnect.SimConnect_SetDataOnSimObject
		self.SetDataOnSimObject.restype = HRESULT
		self.SetDataOnSimObject.argtypes = [
			HANDLE,
			self.DATA_DEFINITION_ID,
			SIMCONNECT_OBJECT_ID,
			SIMCONNECT_DATA_SET_FLAG,
			DWORD,
			DWORD,
			c_void_p,
		]

		# SIMCONNECTAPI SimConnect_MapInputEventToClientEvent(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_INPUT_GROUP_ID GroupID
		#   const char * szInputDefinition
		#   SIMCONNECT_CLIENT_EVENT_ID DownEventID
		#   DWORD DownValue = 0
		#   SIMCONNECT_CLIENT_EVENT_ID UpEventID = (SIMCONNECT_CLIENT_EVENT_ID)SIMCONNECT_UNUSED
		#   DWORD UpValue = 0
		#   BOOL bMaskable = FALSE);
		self.MapInputEventToClientEvent = (
			self.SimConnect.SimConnect_MapInputEventToClientEvent
		)
		self.MapInputEventToClientEvent.restype = HRESULT
		self.MapInputEventToClientEvent.argtypes = [
			HANDLE,
			self.INPUT_GROUP_ID,
			c_char_p,
			self.EventID,
			DWORD,
			self.EventID,
			DWORD,
			c_bool,
		]

		# SIMCONNECTAPI SimConnect_SetInputGroupPriority(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_INPUT_GROUP_ID GroupID
		#   DWORD uPriority);
		self.SetInputGroupPriority = self.SimConnect.SimConnect_SetInputGroupPriority
		self.SetInputGroupPriority.restype = HRESULT
		self.SetInputGroupPriority.argtypes = [HANDLE, self.INPUT_GROUP_ID, DWORD]

		# SIMCONNECTAPI SimConnect_RemoveInputEvent(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_INPUT_GROUP_ID GroupID
		#   const char * szInputDefinition);
		self.RemoveInputEvent = self.SimConnect.SimConnect_RemoveInputEvent
		self.RemoveInputEvent.restype = HRESULT
		self.RemoveInputEvent.argtypes = [HANDLE, self.INPUT_GROUP_ID, c_char_p]

		# SIMCONNECTAPI SimConnect_ClearInputGroup(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_INPUT_GROUP_ID GroupID);
		self.ClearInputGroup = self.SimConnect.SimConnect_ClearInputGroup
		self.ClearInputGroup.restype = HRESULT
		self.ClearInputGroup.argtypes = [HANDLE, self.INPUT_GROUP_ID]

		# SIMCONNECTAPI SimConnect_SetInputGroupState(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_INPUT_GROUP_ID GroupID
		#   DWORD dwState);
		self.SetInputGroupState = self.SimConnect.SimConnect_SetInputGroupState
		self.SetInputGroupState.restype = HRESULT
		self.SetInputGroupState.argtypes = [HANDLE, self.INPUT_GROUP_ID, DWORD]

		# SIMCONNECTAPI SimConnect_RequestReservedKey(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID EventID
		#   const char * szKeyChoice1 = ""
		#   const char * szKeyChoice2 = ""
		#   const char * szKeyChoice3 = "");
		self.RequestReservedKey = self.SimConnect.SimConnect_RequestReservedKey
		self.RequestReservedKey.restype = HRESULT
		self.RequestReservedKey.argtypes = [
			HANDLE,
			self.EventID,
			c_char_p,
			c_char_p,
			c_char_p,
		]

		# SIMCONNECTAPI SimConnect_UnsubscribeFromSystemEvent(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID EventID);
		self.UnsubscribeFromSystemEvent = (
			self.SimConnect.SimConnect_UnsubscribeFromSystemEvent
		)
		self.UnsubscribeFromSystemEvent.restype = HRESULT
		self.UnsubscribeFromSystemEvent.argtypes = [HANDLE, self.EventID]

		# SIMCONNECTAPI SimConnect_WeatherRequestInterpolatedObservation(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   float lat
		#   float lon
		#   float alt);
		self.WeatherRequestInterpolatedObservation = (
			self.SimConnect.SimConnect_WeatherRequestInterpolatedObservation
		)
		self.WeatherRequestInterpolatedObservation.restype = HRESULT
		self.WeatherRequestInterpolatedObservation.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_float,
			c_float,
			c_float,
		]

		# SIMCONNECTAPI SimConnect_WeatherRequestObservationAtStation(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   const char * szICAO);
		self.WeatherRequestObservationAtStation = (
			self.SimConnect.SimConnect_WeatherRequestObservationAtStation
		)
		self.WeatherRequestObservationAtStation.restype = HRESULT
		self.WeatherRequestObservationAtStation.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_char_p,
		]

		# SIMCONNECTAPI SimConnect_WeatherRequestObservationAtNearestStation(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   float lat
		#   float lon);
		self.WeatherRequestObservationAtNearestStation = (
			self.SimConnect.SimConnect_WeatherRequestObservationAtNearestStation
		)
		self.WeatherRequestObservationAtNearestStation.restype = HRESULT
		self.WeatherRequestObservationAtNearestStation.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_float,
			c_float,
		]

		# SIMCONNECTAPI SimConnect_WeatherCreateStation(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   const char * szICAO
		#   const char * szName
		#   float lat
		#   float lon
		#   float alt);
		self.WeatherCreateStation = self.SimConnect.SimConnect_WeatherCreateStation
		self.WeatherCreateStation.restype = HRESULT
		self.WeatherCreateStation.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_char_p,
			c_char_p,
			c_float,
			c_float,
			c_float,
		]

		# SIMCONNECTAPI SimConnect_WeatherRemoveStation(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   const char * szICAO);
		self.WeatherRemoveStation = self.SimConnect.SimConnect_WeatherRemoveStation
		self.WeatherRemoveStation.restype = HRESULT
		self.WeatherRemoveStation.argtypes = [HANDLE, self.DATA_REQUEST_ID, c_char_p]

		# SIMCONNECTAPI SimConnect_WeatherSetObservation(
		#   HANDLE hSimConnect,
		#   DWORD Seconds
		#   const char * szMETAR);
		self.WeatherSetObservation = self.SimConnect.SimConnect_WeatherSetObservation
		self.WeatherSetObservation.restype = HRESULT
		self.WeatherSetObservation.argtypes = [HANDLE, DWORD, c_char_p]

		# SIMCONNECTAPI SimConnect_WeatherSetModeServer(
		#   HANDLE hSimConnect,
		#   DWORD dwPort
		#   DWORD dwSeconds);
		self.WeatherSetModeServer = self.SimConnect.SimConnect_WeatherSetModeServer
		self.WeatherSetModeServer.restype = HRESULT
		self.WeatherSetModeServer.argtypes = [HANDLE, DWORD, DWORD]

		# SIMCONNECTAPI SimConnect_WeatherSetModeTheme(
		#   HANDLE hSimConnect,
		#   const char * szThemeName);
		self.WeatherSetModeTheme = self.SimConnect.SimConnect_WeatherSetModeTheme
		self.WeatherSetModeTheme.restype = HRESULT
		self.WeatherSetModeTheme.argtypes = [HANDLE, c_char_p]

		# SIMCONNECTAPI SimConnect_WeatherSetModeGlobal(
		#   HANDLE hSimConnect);
		self.WeatherSetModeGlobal = self.SimConnect.SimConnect_WeatherSetModeGlobal
		self.WeatherSetModeGlobal.restype = HRESULT
		self.WeatherSetModeGlobal.argtypes = [HANDLE]

		# SIMCONNECTAPI SimConnect_WeatherSetModeCustom(
		#   HANDLE hSimConnect);
		self.WeatherSetModeCustom = self.SimConnect.SimConnect_WeatherSetModeCustom
		self.WeatherSetModeCustom.restype = HRESULT
		self.WeatherSetModeCustom.argtypes = [HANDLE]

		# SIMCONNECTAPI SimConnect_WeatherSetDynamicUpdateRate(
		#   HANDLE hSimConnect,
		#   DWORD dwRate);
		self.WeatherSetDynamicUpdateRate = (
			self.SimConnect.SimConnect_WeatherSetDynamicUpdateRate
		)
		self.WeatherSetDynamicUpdateRate.restype = HRESULT
		self.WeatherSetDynamicUpdateRate.argtypes = [HANDLE, DWORD]

		# SIMCONNECTAPI SimConnect_WeatherRequestCloudState(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   float minLat
		#   float minLon
		#   float minAlt
		#   float maxLat
		#   float maxLon
		#   float maxAlt
		#   DWORD dwFlags = 0);
		self.WeatherRequestCloudState = (
			self.SimConnect.SimConnect_WeatherRequestCloudState
		)
		self.WeatherRequestCloudState.restype = HRESULT
		self.WeatherRequestCloudState.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_WeatherCreateThermal(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   float lat
		#   float lon
		#   float alt
		#   float radius
		#   float height
		#   float coreRate = 3.0f
		#   float coreTurbulence = 0.05f
		#   float sinkRate = 3.0f
		#   float sinkTurbulence = 0.2f
		#   float coreSize = 0.4f
		#   float coreTransitionSize = 0.1f
		#   float sinkLayerSize = 0.4f
		#   float sinkTransitionSize = 0.1f);
		self.WeatherCreateThermal = self.SimConnect.SimConnect_WeatherCreateThermal
		self.WeatherCreateThermal.restype = HRESULT
		self.WeatherCreateThermal.argtypes = [
			HANDLE,
			self.DATA_REQUEST_ID,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
			c_float,
		]

		# SIMCONNECTAPI SimConnect_WeatherRemoveThermal(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_OBJECT_ID ObjectID);
		self.WeatherRemoveThermal = self.SimConnect.SimConnect_WeatherRemoveThermal
		self.WeatherRemoveThermal.restype = HRESULT
		self.WeatherRemoveThermal.argtypes = [HANDLE, SIMCONNECT_OBJECT_ID]

		# SIMCONNECTAPI SimConnect_AICreateParkedATCAircraft(
		#   HANDLE hSimConnect,
		#   const char * szContainerTitle
		#   const char * szTailNumber
		#   const char * szAirportID
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AICreateParkedATCAircraft = (
			self.SimConnect.SimConnect_AICreateParkedATCAircraft
		)
		self.AICreateParkedATCAircraft.restype = HRESULT
		self.AICreateParkedATCAircraft.argtypes = [
			HANDLE,
			c_char_p,
			c_char_p,
			c_char_p,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AICreateEnrouteATCAircraft(
		#   HANDLE hSimConnect,
		#   const char * szContainerTitle
		#   const char * szTailNumber
		#   int iFlightNumber
		#   const char * szFlightPlanPath
		#   double dFlightPlanPosition
		#   BOOL bTouchAndGo
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AICreateEnrouteATCAircraft = (
			self.SimConnect.SimConnect_AICreateEnrouteATCAircraft
		)
		self.AICreateEnrouteATCAircraft.restype = HRESULT
		self.AICreateEnrouteATCAircraft.argtypes = [
			HANDLE,
			c_char_p,
			c_char_p,
			c_int,
			c_char_p,
			c_double,
			c_bool,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AICreateNonATCAircraft(
		#   HANDLE hSimConnect,
		#   const char * szContainerTitle
		#   const char * szTailNumber
		#   SIMCONNECT_DATA_INITPOSITION InitPos
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AICreateNonATCAircraft = (
			self.SimConnect.SimConnect_AICreateNonATCAircraft
		)
		self.AICreateNonATCAircraft.restype = HRESULT
		self.AICreateNonATCAircraft.argtypes = [
			HANDLE,
			c_double,
			c_double,
			SIMCONNECT_DATA_INITPOSITION,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AICreateSimulatedObject(
		#   HANDLE hSimConnect,
		#   const char * szContainerTitle
		#   SIMCONNECT_DATA_INITPOSITION InitPos
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AICreateSimulatedObject = (
			self.SimConnect.SimConnect_AICreateSimulatedObject
		)
		self.AICreateSimulatedObject.restype = HRESULT
		self.AICreateSimulatedObject.argtypes = [
			HANDLE,
			c_char_p,
			SIMCONNECT_DATA_INITPOSITION,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AIReleaseControl(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_OBJECT_ID ObjectID
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AIReleaseControl = self.SimConnect.SimConnect_AIReleaseControl
		self.AIReleaseControl.restype = HRESULT
		self.AIReleaseControl.argtypes = [
			HANDLE,
			SIMCONNECT_OBJECT_ID,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AIRemoveObject(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_OBJECT_ID ObjectID
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AIRemoveObject = self.SimConnect.SimConnect_AIRemoveObject
		self.AIRemoveObject.restype = HRESULT
		self.AIRemoveObject.argtypes = [
			HANDLE,
			SIMCONNECT_OBJECT_ID,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_AISetAircraftFlightPlan(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_OBJECT_ID ObjectID
		#   const char * szFlightPlanPath
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.AISetAircraftFlightPlan = (
			self.SimConnect.SimConnect_AISetAircraftFlightPlan
		)
		self.AISetAircraftFlightPlan.restype = HRESULT
		self.AISetAircraftFlightPlan.argtypes = [
			HANDLE,
			SIMCONNECT_OBJECT_ID,
			c_char_p,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_ExecuteMissionAction(
		#   HANDLE hSimConnect,
		#   const GUID guidInstanceId);
		self.ExecuteMissionAction = self.SimConnect.SimConnect_ExecuteMissionAction
		self.ExecuteMissionAction.restype = HRESULT
		self.ExecuteMissionAction.argtypes = []

		# SIMCONNECTAPI SimConnect_CompleteCustomMissionAction(
		#   HANDLE hSimConnect,
		#   const GUID guidInstanceId);
		self.CompleteCustomMissionAction = (
			self.SimConnect.SimConnect_CompleteCustomMissionAction
		)
		self.CompleteCustomMissionAction.restype = HRESULT
		self.CompleteCustomMissionAction.argtypes = []

		# SIMCONNECTAPI SimConnect_RetrieveString(
		#   SIMCONNECT_RECV * pData,
		#   DWORD cbData
		#   void * pStringV
		#   char ** pszString
		#   DWORD * pcbString);
		self.RetrieveString = self.SimConnect.SimConnect_RetrieveString
		self.RetrieveString.restype = HRESULT
		self.RetrieveString.argtypes = []

		# SIMCONNECTAPI SimConnect_GetLastSentPacketID(
		#   HANDLE hSimConnect,
		#   DWORD * pdwError);
		self.GetLastSentPacketID = self.SimConnect.SimConnect_GetLastSentPacketID
		self.GetLastSentPacketID.restype = HRESULT
		self.GetLastSentPacketID.argtypes = [HANDLE, POINTER(DWORD)]

		# SIMCONNECTAPI SimConnect_GetNextDispatch(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_RECV ** ppData
		#   DWORD * pcbData);
		self.GetNextDispatch = self.SimConnect.SimConnect_GetNextDispatch
		self.GetNextDispatch.restype = HRESULT
		self.GetNextDispatch.argtypes = []

		# SIMCONNECTAPI SimConnect_RequestResponseTimes(
		#   HANDLE hSimConnect,
		#   DWORD nCount
		#   float * fElapsedSeconds);
		self.RequestResponseTimes = self.SimConnect.SimConnect_RequestResponseTimes
		self.RequestResponseTimes.restype = HRESULT
		self.RequestResponseTimes.argtypes = [HANDLE, DWORD, c_float]

		# SIMCONNECTAPI SimConnect_InsertString(
		#   char * pDest,
		#   DWORD cbDest
		#   void ** ppEnd
		#   DWORD * pcbStringV
		#   const char * pSource);
		self.InsertString = self.SimConnect.SimConnect_InsertString
		self.InsertString.restype = HRESULT
		self.InsertString.argtypes = []

		# SIMCONNECTAPI SimConnect_CameraSetRelative6DOF(
		#   HANDLE hSimConnect,
		#   float fDeltaX
		#   float fDeltaY
		#   float fDeltaZ
		#   float fPitchDeg
		#   float fBankDeg
		#   float fHeadingDeg);
		self.CameraSetRelative6DOF = self.SimConnect.SimConnect_CameraSetRelative6DOF
		self.CameraSetRelative6DOF.restype = HRESULT
		self.CameraSetRelative6DOF.argtypes = []

		# SIMCONNECTAPI SimConnect_MenuAddItem(
		#   HANDLE hSimConnect,
		#   const char * szMenuItem
		#   SIMCONNECT_CLIENT_EVENT_ID MenuEventID
		#   DWORD dwData);
		self.MenuAddItem = self.SimConnect.SimConnect_MenuAddItem
		self.MenuAddItem.restype = HRESULT
		self.MenuAddItem.argtypes = []

		# SIMCONNECTAPI SimConnect_MenuDeleteItem(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID MenuEventID);
		self.MenuDeleteItem = self.SimConnect.SimConnect_MenuDeleteItem
		self.MenuDeleteItem.restype = HRESULT
		self.MenuDeleteItem.argtypes = []

		# SIMCONNECTAPI SimConnect_MenuAddSubItem(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID MenuEventID
		#   const char * szMenuItem
		#   SIMCONNECT_CLIENT_EVENT_ID SubMenuEventID
		#   DWORD dwData);
		self.MenuAddSubItem = self.SimConnect.SimConnect_MenuAddSubItem
		self.MenuAddSubItem.restype = HRESULT
		self.MenuAddSubItem.argtypes = []

		# SIMCONNECTAPI SimConnect_MenuDeleteSubItem(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_EVENT_ID MenuEventID
		#   const SIMCONNECT_CLIENT_EVENT_ID SubMenuEventID);
		self.MenuDeleteSubItem = self.SimConnect.SimConnect_MenuDeleteSubItem
		self.MenuDeleteSubItem.restype = HRESULT
		self.MenuDeleteSubItem.argtypes = []

		# SIMCONNECTAPI SimConnect_RequestSystemState(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   const char * szState);
		self.RequestSystemState = self.SimConnect.SimConnect_RequestSystemState
		self.RequestSystemState.restype = HRESULT
		self.RequestSystemState.argtypes = []

		# SIMCONNECTAPI SimConnect_SetSystemState(
		#   HANDLE hSimConnect,
		#   const char * szState
		#   DWORD dwInteger
		#   float fFloat
		#   const char * szString);
		self.SetSystemState = self.SimConnect.SimConnect_SetSystemState
		self.SetSystemState.restype = HRESULT
		self.SetSystemState.argtypes = []

		# SIMCONNECTAPI SimConnect_MapClientDataNameToID(
		#   HANDLE hSimConnect,
		#   const char * szClientDataName
		#   SIMCONNECT_CLIENT_DATA_ID ClientDataID);
		self.MapClientDataNameToID = self.SimConnect.SimConnect_MapClientDataNameToID
		self.MapClientDataNameToID.restype = HRESULT
		self.MapClientDataNameToID.argtypes = []

		# SIMCONNECTAPI SimConnect_CreateClientData(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_DATA_ID ClientDataID
		#   DWORD dwSize
		#   SIMCONNECT_CREATE_CLIENT_DATA_FLAG Flags);
		self.CreateClientData = self.SimConnect.SimConnect_CreateClientData
		self.CreateClientData.restype = HRESULT
		self.CreateClientData.argtypes = [
			HANDLE,
			self.CLIENT_DATA_ID,
			DWORD,
			SIMCONNECT_CREATE_CLIENT_DATA_FLAG,
		]

		# SIMCONNECTAPI SimConnect_AddToClientDataDefinition(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_DATA_DEFINITION_ID DefineID
		#   DWORD dwOffset
		#   DWORD dwSizeOrType
		#   float fEpsilon = 0
		#   DWORD DatumID = SIMCONNECT_UNUSED);
		self.AddToClientDataDefinition = (
			self.SimConnect.SimConnect_AddToClientDataDefinition
		)
		self.AddToClientDataDefinition.restype = HRESULT
		self.AddToClientDataDefinition.argtypes = [
			HANDLE,
			self.CLIENT_DATA_DEFINITION_ID,
			DWORD,
			DWORD,
			c_float,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_ClearClientDataDefinition(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_DATA_DEFINITION_ID DefineID);
		self.ClearClientDataDefinition = (
			self.SimConnect.SimConnect_ClearClientDataDefinition
		)
		self.ClearClientDataDefinition.restype = HRESULT
		self.ClearClientDataDefinition.argtypes = [
			HANDLE,
			self.CLIENT_DATA_DEFINITION_ID,
		]

		# SIMCONNECTAPI SimConnect_RequestClientData(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_DATA_ID ClientDataID
		#   SIMCONNECT_DATA_REQUEST_ID RequestID
		#   SIMCONNECT_CLIENT_DATA_DEFINITION_ID DefineID
		#   SIMCONNECT_CLIENT_DATA_PERIOD Period = SIMCONNECT_CLIENT_DATA_PERIOD_ONCE
		#   SIMCONNECT_CLIENT_DATA_REQUEST_FLAG Flags = 0
		#   DWORD origin = 0
		#   DWORD interval = 0
		#   DWORD limit = 0);
		self.RequestClientData = self.SimConnect.SimConnect_RequestClientData
		self.RequestClientData.restype = HRESULT
		self.RequestClientData.argtypes = [
			HANDLE,
			self.CLIENT_DATA_ID,
			self.DATA_REQUEST_ID,
			self.CLIENT_DATA_DEFINITION_ID,
			SIMCONNECT_CLIENT_DATA_PERIOD,
			SIMCONNECT_CLIENT_DATA_REQUEST_FLAG,
			DWORD,
			DWORD,
			DWORD,
		]

		# SIMCONNECTAPI SimConnect_SetClientData(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_CLIENT_DATA_ID ClientDataID
		#   SIMCONNECT_CLIENT_DATA_DEFINITION_ID DefineID
		#   SIMCONNECT_CLIENT_DATA_SET_FLAG Flags
		#   DWORD dwReserved
		#   DWORD cbUnitSize
		#   void * pDataSet);
		self.SetClientData = self.SimConnect.SimConnect_SetClientData
		self.SetClientData.restype = HRESULT
		self.SetClientData.argtypes = [
			HANDLE,
			self.CLIENT_DATA_ID,
			self.CLIENT_DATA_DEFINITION_ID,
			SIMCONNECT_CLIENT_DATA_SET_FLAG,
			DWORD,
			DWORD,
			c_void_p,
		]

		# SIMCONNECTAPI SimConnect_FlightLoad(
		#   HANDLE hSimConnect,
		#   const char * szFileName);
		self.FlightLoad = self.SimConnect.SimConnect_FlightLoad
		self.FlightLoad.restype = HRESULT
		self.FlightLoad.argtypes = [HANDLE, c_char_p]

		# SIMCONNECTAPI SimConnect_FlightSave(
		#   HANDLE hSimConnect,
		#   const char * szFileName
		#   const char * szTitle
		#   const char * szDescription
		#   DWORD Flags);
		self.FlightSave = self.SimConnect.SimConnect_FlightSave
		self.FlightSave.restype = HRESULT
		self.FlightSave.argtypes = [HANDLE, c_char_p, c_char_p, c_char_p, DWORD]

		# SIMCONNECTAPI SimConnect_FlightPlanLoad(
		#   HANDLE hSimConnect,
		#   const char * szFileName);
		self.FlightPlanLoad = self.SimConnect.SimConnect_FlightPlanLoad
		self.FlightPlanLoad.restype = HRESULT
		self.FlightPlanLoad.argtypes = [HANDLE, c_char_p]

		# SIMCONNECTAPI SimConnect_Text(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_TEXT_TYPE type
		#   float fTimeSeconds
		#   SIMCONNECT_CLIENT_EVENT_ID EventID
		#   DWORD cbUnitSize
		#   void * pDataSet);
		self.Text = self.SimConnect.SimConnect_Text
		self.Text.restype = HRESULT
		self.Text.argtypes = [
			HANDLE,
			SIMCONNECT_TEXT_TYPE,
			c_float,
			self.EventID,
			DWORD,
			c_void_p,
		]

		# SIMCONNECTAPI SimConnect_SubscribeToFacilities(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_FACILITY_LIST_TYPE type
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.SubscribeToFacilities = self.SimConnect.SimConnect_SubscribeToFacilities
		self.SubscribeToFacilities.restype = HRESULT
		self.SubscribeToFacilities.argtypes = [
			HANDLE,
			SIMCONNECT_FACILITY_LIST_TYPE,
			self.DATA_REQUEST_ID,
		]

		# SIMCONNECTAPI SimConnect_UnsubscribeToFacilities(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_FACILITY_LIST_TYPE type);
		self.UnsubscribeToFacilities = (
			self.SimConnect.SimConnect_UnsubscribeToFacilities
		)
		self.UnsubscribeToFacilities.restype = HRESULT
		self.UnsubscribeToFacilities.argtypes = [
			HANDLE,
			SIMCONNECT_FACILITY_LIST_TYPE,
		]

		# SIMCONNECTAPI SimConnect_RequestFacilitiesList(
		#   HANDLE hSimConnect,
		#   SIMCONNECT_FACILITY_LIST_TYPE type
		#   SIMCONNECT_DATA_REQUEST_ID RequestID);
		self.RequestFacilitiesList = (
			self.SimConnect.SimConnect_RequestFacilitiesList
		)
		self.RequestFacilitiesList.restype = HRESULT
		self.RequestFacilitiesList.argtypes = [
			HANDLE,
			SIMCONNECT_FACILITY_LIST_TYPE,
			self.DATA_REQUEST_ID,
		]

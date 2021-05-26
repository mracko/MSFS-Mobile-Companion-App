from SimConnect import *
from .Enum import *
from .Constants import *
import asyncio


class Request(object):

	async def get(self):
		return self.value

	def set(self, _value):
		self.value = _value

	@property
	async def value(self):
		if self._deff_test():
			# self.sm.run()
			if (self.LastData + self.time) < millis():
				await self.sm.get_data(self)
				self.LastData = millis()
			return self.outData
		else:
			raise Exception(self.definitions[0][0])

	@value.setter
	def value(self, val):
		if self._deff_test() and self.settable:
			self.outData = val
			self.sm.set_data(self)
			# self.sm.run()

	def __init__(self, _deff, _sm, _time=10, _dec=None, _settable=False, _attemps=10):
		self.DATA_DEFINITION_ID = None
		self.definitions = []
		self.description = _dec
		self._name = None
		self.definitions.append(_deff)
		self.outData = None
		self.attemps = _attemps
		self.sm = _sm
		self.time = _time
		self.defined = False
		self.settable = _settable
		self.LastData = 0
		self.LastID = 0
		if ':index' in str(self.definitions[0][0]):
			self.lastIndex = b':index'

	def setIndex(self, index):
		if not hasattr(self, "lastIndex"):
			return False
		(dec, stype) = self.definitions[0]
		newindex = str(":" + str(index)).encode()
		if newindex == self.lastIndex:
			return
		dec = dec.replace(self.lastIndex, newindex)
		self.lastIndex = newindex
		self.definitions[0] = (dec, stype)
		self.redefine()
		return True

	def redefine(self):
		if self.DATA_DEFINITION_ID is not None:
			self.sm.dll.ClearDataDefinition(
				self.sm.hSimConnect,
				self.DATA_DEFINITION_ID.value,
			)
			self.defined = False
			# self.sm.run()
		# if self._deff_test():
		# 	# self.sm.run()
		# 	self.sm.get_data(self)

	def _deff_test(self):
		if ':index' in str(self.definitions[0][0]):
			self.lastIndex = b':index'
			return False
		if self.defined is True:
			return True
		if self.DATA_DEFINITION_ID is None:
			self.DATA_DEFINITION_ID = self.sm.new_def_id()
			self.DATA_REQUEST_ID = self.sm.new_request_id()
			self.outData = None
			self.sm.Requests[self.DATA_REQUEST_ID.value] = self

		rtype = self.definitions[0][1]
		DATATYPE = SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64
		if 'String' in rtype.decode() or 'string' in rtype.decode():
			rtype = None
			DATATYPE = SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_STRINGV

		err = self.sm.dll.AddToDataDefinition(
			self.sm.hSimConnect,
			self.DATA_DEFINITION_ID.value,
			self.definitions[0][0],
			rtype,
			DATATYPE,
			0,
			SIMCONNECT_UNUSED,
		)
		if self.sm.IsHR(err, 0):
			self.defined = True
			temp = DWORD(0)
			self.sm.dll.GetLastSentPacketID(self.sm.hSimConnect, temp)
			self.LastID = temp.value
			return True
		else:
			LOGGER.error("SIM def" + str(self.definitions[0]))
			return False


class RequestHelper:
	def __init__(self, _sm, _time=10, _attemps=10):
		self.sm = _sm
		self.dic = []
		self.time = _time
		self.attemps = _attemps

	def __getattribute__(self, _name):
		return super().__getattribute__(_name)

	def __getattr__(self, _name):
		if _name in self.list:
			key = self.list.get(_name)
			setable = False
			if key[3] == 'Y':
				setable = True
			ne = Request((key[1], key[2]), self.sm, _dec=key[0], _settable=setable, _time=self.time, _attemps=self.attemps)
			setattr(self, _name, ne)
			return ne
		return None

	async def get(self, _name):
		if getattr(self, _name) is None:
			return None
		return await getattr(self, _name).value

	def set(self, _name, _value=0):
		temp = getattr(self, _name)
		if temp is None:
			return False
		if not getattr(temp, "settable"):
			return False

		setattr(temp, "value", _value)
		return True

	def json(self):
		map = {}
		for att in self.list:
			val = self.get(att)
			if val is not None:
				try:
					map[att] = val.value
				except AttributeError:
					map[att] = val
		return map


class AircraftRequests():
	def find(self, key):
		index = None
		if ':' in key:
			(keyname, index) = key.split(":", 1)
			key = "%s:index" % (keyname)

		for clas in self.list:
			if key in clas.list:
				rqest = getattr(clas, key)
				if index is not None:
					rqest.setIndex(index)
				return rqest
		return None

	def get(self, key):
		request = self.find(key)
		if request is None:
			return None
		return request.value

	def set(self, key, _value):
		request = self.find(key)
		if request is None:
			return False
		request.value = _value
		return True

	def __init__(self, _sm, _time=10, _attemps=10):
		self.sm = _sm
		self.list = []
		self.EngineData = self.__AircraftEngineData(_sm, _time, _attemps)
		self.list.append(self.EngineData)
		self.FuelTankSelection = self.__FuelTankSelection(_sm, _time, _attemps)
		self.list.append(self.FuelTankSelection)
		self.FuelData = self.__AircraftFuelData(_sm, _time, _attemps)
		self.list.append(self.FuelData)
		self.LightsData = self.__AircraftLightsData(_sm, _time, _attemps)
		self.list.append(self.LightsData)
		self.PositionandSpeedData = self.__AircraftPositionandSpeedData(_sm, _time, _attemps)
		self.list.append(self.PositionandSpeedData)
		self.FlightInstrumentationData = self.__AircraftFlightInstrumentationData(_sm, _time, _attemps)
		self.list.append(self.FlightInstrumentationData)
		self.AvionicsData = self.__AircraftAvionicsData(_sm, _time, _attemps)
		self.list.append(self.AvionicsData)
		self.ControlsData = self.__AircraftControlsData(_sm, _time, _attemps)
		self.list.append(self.ControlsData)
		self.AutopilotData = self.__AircraftAutopilotData(_sm, _time, _attemps)
		self.list.append(self.AutopilotData)
		self.LandingGearData = self.__AircraftLandingGearData(_sm, _time, _attemps)
		self.list.append(self.LandingGearData)
		self.EnvironmentData = self.__AircraftEnvironmentData(_sm, _time, _attemps)
		self.list.append(self.EnvironmentData)
		self.HelicopterSpecificData = self.__HelicopterSpecificData(_sm, _time, _attemps)
		self.list.append(self.HelicopterSpecificData)
		self.MiscellaneousSystemsData = self.__AircraftMiscellaneousSystemsData(_sm, _time, _attemps)
		self.list.append(self.MiscellaneousSystemsData)
		self.MiscellaneousData = self.__AircraftMiscellaneousData(_sm, _time, _attemps)
		self.list.append(self.MiscellaneousData)
		self.StringData = self.__AircraftStringData(_sm, _time, _attemps)
		self.list.append(self.StringData)
		self.AIControlledAircraft = self.__AIControlledAircraft(_sm, _time, _attemps)
		self.list.append(self.AIControlledAircraft)
		self.CarrierOperations = self.__CarrierOperations(_sm, _time, _attemps)
		self.list.append(self.CarrierOperations)
		self.Racing = self.__Racing(_sm, _time, _attemps)
		self.list.append(self.Racing)
		self.EnvironmentData = self.__EnvironmentData(_sm, _time, _attemps)
		self.list.append(self.EnvironmentData)
		self.SlingsandHoists = self.__SlingsandHoists(_sm, _time, _attemps)
		self.list.append(self.SlingsandHoists)

	class __AircraftEngineData(RequestHelper):
		list = {
			"NUMBER_OF_ENGINES": ["Number of engines (minimum 0, maximum 4)", b'NUMBER OF ENGINES', b'Number', 'N'],
			"ENGINE_CONTROL_SELECT": ["Selected engines (combination of bit flags); 1 = Engine 1; 2 = Engine 2; 4 = Engine 3; 8 = Engine 4", b'ENGINE CONTROL SELECT', b'Mask', 'Y'],
			"THROTTLE_LOWER_LIMIT": ["Percent throttle defining lower limit (negative for reverse thrust equipped airplanes)", b'THROTTLE LOWER LIMIT', b'Percent', 'N'],
			"ENGINE_TYPE": ["Engine type:; 0 = Piston; 1 = Jet; 2 = None; 3 = Helo(Bell) turbine; 4 = Unsupported; 5 = Turboprop", b'ENGINE TYPE', b'Enum', 'N'],
			"MASTER_IGNITION_SWITCH": ["Aircraft master ignition switch (grounds all engines magnetos)", b'MASTER IGNITION SWITCH', b'Bool', 'N'],
			"GENERAL_ENG_COMBUSTION:index": ["Combustion flag", b'GENERAL ENG COMBUSTION:index', b'Bool', 'Y'],
			"GENERAL_ENG_MASTER_ALTERNATOR:index": ["Alternator (generator) switch", b'GENERAL ENG MASTER ALTERNATOR:index', b'Bool', 'N'],
			"GENERAL_ENG_FUEL_PUMP_SWITCH:index": ["Fuel pump switch", b'GENERAL ENG FUEL PUMP SWITCH:index', b'Bool', 'N'],
			"GENERAL_ENG_FUEL_PUMP_ON:index": ["Fuel pump on/off", b'GENERAL ENG FUEL PUMP ON:index', b'Bool', 'N'],
			"GENERAL_ENG_RPM:index": ["Engine rpm", b'GENERAL ENG RPM:index', b'Rpm', 'N'],
			"GENERAL_ENG_PCT_MAX_RPM:index": ["Percent of max rated rpm", b'GENERAL ENG PCT MAX RPM:index', b'Percent', 'N'],
			"GENERAL_ENG_MAX_REACHED_RPM:index": ["Maximum attained rpm", b'GENERAL ENG MAX REACHED RPM:index', b'Rpm', 'N'],
			"GENERAL_ENG_THROTTLE_LEVER_POSITION:index": ["Percent of max throttle position", b'GENERAL ENG THROTTLE LEVER POSITION:index', b'Percent', 'Y'],
			"GENERAL_ENG_MIXTURE_LEVER_POSITION:index": ["Percent of max mixture lever position", b'GENERAL ENG MIXTURE LEVER POSITION:index', b'Percent', 'Y'],
			"GENERAL_ENG_PROPELLER_LEVER_POSITION:index": ["Percent of max prop lever position", b'GENERAL ENG PROPELLER LEVER POSITION:index', b'Percent', 'Y'],
			"GENERAL_ENG_STARTER:index": ["Engine starter on/off", b'GENERAL ENG STARTER:index', b'Bool', 'N'],
			"GENERAL_ENG_EXHAUST_GAS_TEMPERATURE:index": ["Engine exhaust gas temperature.", b'GENERAL ENG EXHAUST GAS TEMPERATURE:index', b'Rankine', 'Y'],
			"GENERAL_ENG_OIL_PRESSURE:index": ["Engine oil pressure", b'GENERAL ENG OIL PRESSURE:index', b'Psf', 'Y'],
			"GENERAL_ENG_OIL_LEAKED_PERCENT:index": ["Percent of max oil capacity leaked", b'GENERAL ENG OIL LEAKED PERCENT:index', b'Percent', 'N'],
			"GENERAL_ENG_COMBUSTION_SOUND_PERCENT:index": ["Percent of maximum engine sound", b'GENERAL ENG COMBUSTION SOUND PERCENT:index', b'Percent', 'N'],
			"GENERAL_ENG_DAMAGE_PERCENT:index": ["Percent of total engine damage", b'GENERAL ENG DAMAGE PERCENT:index', b'Percent', 'N'],
			"GENERAL_ENG_OIL_TEMPERATURE:index": ["Engine oil temperature", b'GENERAL ENG OIL TEMPERATURE:index', b'Rankine', 'Y'],
			"GENERAL_ENG_FAILED:index": ["Fail flag", b'GENERAL ENG FAILED:index', b'Bool', 'N'],
			"GENERAL_ENG_GENERATOR_SWITCH:index": ["Alternator (generator) switch", b'GENERAL ENG GENERATOR SWITCH:index', b'Bool', 'N'],
			"GENERAL_ENG_GENERATOR_ACTIVE:index": ["Alternator (generator) on/off", b'GENERAL ENG GENERATOR ACTIVE:index', b'Bool', 'Y'],
			"GENERAL_ENG_ANTI_ICE_POSITION:index": ["Engine anti-ice switch", b'GENERAL ENG ANTI ICE POSITION:index', b'Bool', 'N'],
			"GENERAL_ENG_FUEL_VALVE:index": ["Fuel valve state", b'GENERAL ENG FUEL VALVE:index', b'Bool', 'N'],
			"GENERAL_ENG_FUEL_PRESSURE:index": ["Engine fuel pressure", b'GENERAL ENG FUEL PRESSURE:index', b'Psi', 'Y'],
			"GENERAL_ENG_ELAPSED_TIME:index": ["Total engine elapsed time", b'GENERAL ENG ELAPSED TIME:index', b'Hours', 'N'],
			"RECIP_ENG_COWL_FLAP_POSITION:index": ["Percent cowl flap opened", b'RECIP ENG COWL FLAP POSITION:index', b'Percent', 'Y'],
			"RECIP_ENG_PRIMER:index": ["Engine primer position", b'RECIP ENG PRIMER:index', b'Bool', 'Y'],
			"RECIP_ENG_MANIFOLD_PRESSURE:index": ["Engine manifold pressure", b'RECIP ENG MANIFOLD PRESSURE:index', b'Psi', 'Y'],
			"RECIP_ENG_ALTERNATE_AIR_POSITION:index": ["Alternate air control", b'RECIP ENG ALTERNATE AIR POSITION:index', b'Position', 'Y'],
			"RECIP_ENG_COOLANT_RESERVOIR_PERCENT:index": ["Percent coolant available", b'RECIP ENG COOLANT RESERVOIR PERCENT:index', b'Percent', 'Y'],
			"RECIP_ENG_LEFT_MAGNETO:index": ["Left magneto state", b'RECIP ENG LEFT MAGNETO:index', b'Bool', 'Y'],
			"RECIP_ENG_RIGHT_MAGNETO:index": ["Right magneto state", b'RECIP ENG RIGHT MAGNETO:index', b'Bool', 'Y'],
			"RECIP_ENG_BRAKE_POWER:index": ["Brake power produced by engine", b'RECIP ENG BRAKE POWER:index', b'Foot pounds per second', 'Y'],
			"RECIP_ENG_STARTER_TORQUE:index": ["Torque produced by engine", b'RECIP ENG STARTER TORQUE:index', b'Foot pound', 'Y'],
			"RECIP_ENG_TURBOCHARGER_FAILED:index": ["Turbo failed state", b'RECIP ENG TURBOCHARGER FAILED:index', b'Bool', 'Y'],
			"RECIP_ENG_EMERGENCY_BOOST_ACTIVE:index": ["War emergency power active", b'RECIP ENG EMERGENCY BOOST ACTIVE:index', b'Bool', 'Y'],
			"RECIP_ENG_EMERGENCY_BOOST_ELAPSED_TIME:index": ["Elapsed time war emergency power active", b'RECIP ENG EMERGENCY BOOST ELAPSED TIME:index', b'Hours', 'Y'],
			"RECIP_ENG_WASTEGATE_POSITION:index": ["Percent turbo wastegate closed", b'RECIP ENG WASTEGATE POSITION:index', b'Percent', 'Y'],
			"RECIP_ENG_TURBINE_INLET_TEMPERATURE:index": ["Engine turbine inlet temperature", b'RECIP ENG TURBINE INLET TEMPERATURE:index', b'Celsius', 'Y'],
			"RECIP_ENG_CYLINDER_HEAD_TEMPERATURE:index": ["Engine cylinder head temperature", b'RECIP ENG CYLINDER HEAD TEMPERATURE:index', b'Celsius', 'Y'],
			"RECIP_ENG_RADIATOR_TEMPERATURE:index": ["Engine radiator temperature", b'RECIP ENG RADIATOR TEMPERATURE:index', b'Celsius', 'Y'],
			"RECIP_ENG_FUEL_AVAILABLE:index": ["True if fuel is available", b'RECIP ENG FUEL AVAILABLE:index', b'Bool', 'Y'],
			"RECIP_ENG_FUEL_FLOW:index": ["Engine fuel flow", b'RECIP ENG FUEL FLOW:index', b'Pounds per hour', 'Y'],
			"RECIP_ENG_FUEL_TANK_SELECTOR:index": ["Fuel tank selected for engine. See fuel tank list.", b'RECIP ENG FUEL TANK SELECTOR:index', b'Enum', 'N'],
			"ENGINE_TYPE": ["Engine type:; 0 = Piston; 1 = Jet; 2 = None; 3 = Helo(Bell) turbine; 4 = Unsupported; 5 = Turboprop", b'ENGINE TYPE', b'Enum', 'N'],
			"RECIP_ENG_FUEL_NUMBER_TANKS_USED:index": ["Number of tanks currently being used", b'RECIP ENG FUEL NUMBER TANKS USED:index', b'Number', 'N'],
			"RECIP_CARBURETOR_TEMPERATURE:index": ["Carburetor temperature", b'RECIP CARBURETOR TEMPERATURE:index', b'Celsius', 'Y'],
			"RECIP_MIXTURE_RATIO:index": ["Fuel / Air mixture ratio", b'RECIP MIXTURE RATIO:index', b'Ratio', 'Y'],
			"TURB_ENG_N1:index": ["Turbine engine N1", b'TURB ENG N1:index', b'Percent', 'Y'],
			"TURB_ENG_N2:index": ["Turbine engine N2", b'TURB ENG N2:index', b'Percent', 'Y'],
			"TURB_ENG_CORRECTED_N1:index": ["Turbine engine corrected N1", b'TURB ENG CORRECTED N1:index', b'Percent', 'Y'],
			"TURB_ENG_CORRECTED_N2:index": ["Turbine engine corrected N2", b'TURB ENG CORRECTED N2:index', b'Percent', 'Y'],
			"TURB_ENG_CORRECTED_FF:index": ["Corrected fuel flow", b'TURB ENG CORRECTED FF:index', b'Pounds per hour', 'Y'],
			"TURB_ENG_MAX_TORQUE_PERCENT:index": ["Percent of max rated torque", b'TURB ENG MAX TORQUE PERCENT:index', b'Percent', 'Y'],
			"TURB_ENG_PRESSURE_RATIO:index": ["Engine pressure ratio", b'TURB ENG PRESSURE RATIO:index', b'Ratio', 'Y'],
			"TURB_ENG_ITT:index": ["Engine ITT", b'TURB ENG ITT:index', b'Rankine', 'Y'],
			"TURB_ENG_AFTERBURNER:index": ["Afterburner state", b'TURB ENG AFTERBURNER:index', b'Bool', 'N'],
			"TURB_ENG_JET_THRUST:index": ["Engine jet thrust", b'TURB ENG JET THRUST:index', b'Pounds', 'N'],
			"TURB_ENG_BLEED_AIR:index": ["Bleed air pressure", b'TURB ENG BLEED AIR:index', b'Psi', 'N'],
			"TURB_ENG_TANK_SELECTOR:index": ["Fuel tank selected for engine. See fuel tank list.", b'TURB ENG TANK SELECTOR:index', b'Enum', 'N'],
			"ENGINE_TYPE": ["Engine type:; 0 = Piston; 1 = Jet; 2 = None; 3 = Helo(Bell) turbine; 4 = Unsupported; 5 = Turboprop", b'ENGINE TYPE', b'Enum', 'N'],
			"TURB_ENG_NUM_TANKS_USED:index": ["Number of tanks currently being used", b'TURB ENG NUM TANKS USED:index', b'Number', 'N'],
			"TURB_ENG_FUEL_FLOW_PPH:index": ["Engine fuel flow", b'TURB ENG FUEL FLOW PPH:index', b'Pounds per hour', 'N'],
			"TURB_ENG_FUEL_AVAILABLE:index": ["True if fuel is available", b'TURB ENG FUEL AVAILABLE:index', b'Bool', 'N'],
			"TURB_ENG_REVERSE_NOZZLE_PERCENT:index": ["Percent thrust reverser nozzles deployed", b'TURB ENG REVERSE NOZZLE PERCENT:index', b'Percent', 'N'],
			"TURB_ENG_VIBRATION:index": ["Engine vibration value", b'TURB ENG VIBRATION:index', b'Number', 'N'],
			"ENG_FAILED:index": ["Failure flag", b'ENG FAILED:index', b'Number', 'N'],
			"ENG_RPM_ANIMATION_PERCENT:index": ["Percent max rated rpm used for visual animation", b'ENG RPM ANIMATION PERCENT:index', b'Percent', 'N'],
			"ENG_ON_FIRE:index": ["On fire state", b'ENG ON FIRE:index', b'Bool', 'Y'],
			"ENG_FUEL_FLOW_BUG_POSITION:index": ["Fuel flow reference", b'ENG FUEL FLOW BUG POSITION:index', b'Pounds per hour', 'N'],
			"PROP_RPM:index": ["Propeller rpm", b'PROP RPM:index', b'Rpm', 'Y'],
			"PROP_MAX_RPM_PERCENT:index": ["Percent of max rated rpm", b'PROP MAX RPM PERCENT:index', b'Percent', 'N'],
			"PROP_THRUST:index": ["Propeller thrust", b'PROP THRUST:index', b'Pounds', 'N'],
			"PROP_BETA:index": ["Prop blade pitch angle", b'PROP BETA:index', b'Radians', 'N'],
			"PROP_FEATHERING_INHIBIT:index": ["Feathering inhibit flag", b'PROP FEATHERING INHIBIT:index', b'Bool', 'N'],
			"PROP_FEATHERED:index": ["Feathered state", b'PROP FEATHERED:index', b'Bool', 'N'],
			"PROP_SYNC_DELTA_LEVER:index": ["Corrected prop correction input on slaved engine", b'PROP SYNC DELTA LEVER:index', b'Position', 'N'],
			"PROP_AUTO_FEATHER_ARMED:index": ["Auto-feather armed state", b'PROP AUTO FEATHER ARMED:index', b'Bool', 'N'],
			"PROP_FEATHER_SWITCH:index": ["Prop feather switch", b'PROP FEATHER SWITCH:index', b'Bool', 'N'],
			"PANEL_AUTO_FEATHER_SWITCH:index": ["Auto-feather arming switch", b'PANEL AUTO FEATHER SWITCH:index', b'Bool', 'N'],
			"PROP_SYNC_ACTIVE:index": ["True if prop sync is active", b'PROP SYNC ACTIVE:index', b'Bool', 'N'],
			"PROP_DEICE_SWITCH:index": ["True if prop deice switch on", b'PROP DEICE SWITCH:index', b'Bool', 'N'],
			"ENG_COMBUSTION": ["True if the engine is running", b'ENG COMBUSTION', b'Bool', 'N'],
			"ENG_N1_RPM:index": ["Engine N1 rpm", b'ENG N1 RPM:index', b'Rpm (0 to 16384 = 0 to 100%)', 'N'],
			"ENG_N2_RPM:index": ["Engine N2 rpm", b'ENG N2 RPM:index', b'Rpm(0 to 16384 = 0 to 100%)', 'N'],
			"ENG_FUEL_FLOW_GPH:index": ["Engine fuel flow", b'ENG FUEL FLOW GPH:index', b'Gallons per hour', 'N'],
			"ENG_FUEL_FLOW_PPH:index": ["Engine fuel flow", b'ENG FUEL FLOW PPH:index', b'Pounds per hour', 'N'],
			"ENG_TORQUE:index": ["Torque", b'ENG TORQUE:index', b'Foot pounds', 'N'],
			"ENG_ANTI_ICE:index": ["Anti-ice switch", b'ENG ANTI ICE:index', b'Bool', 'N'],
			"ENG_PRESSURE_RATIO:index": ["Engine pressure ratio", b'ENG PRESSURE RATIO:index', b'Ratio (0-16384)', 'N'],
			"ENG_EXHAUST_GAS_TEMPERATURE:index": ["Exhaust gas temperature", b'ENG EXHAUST GAS TEMPERATURE:index', b'Rankine', 'N'],
			"ENG_EXHAUST_GAS_TEMPERATURE_GES:index": ["Governed engine setting", b'ENG EXHAUST GAS TEMPERATURE GES:index', b'Percent over 100', 'N'],
			"ENG_CYLINDER_HEAD_TEMPERATURE:index": ["Engine cylinder head temperature", b'ENG CYLINDER HEAD TEMPERATURE:index', b'Rankine', 'N'],
			"ENG_OIL_TEMPERATURE:index": ["Engine oil temperature", b'ENG OIL TEMPERATURE:index', b'Rankine', 'N'],
			"ENG_OIL_PRESSURE:index": ["Engine oil pressure", b'ENG OIL PRESSURE:index', b'foot pounds', 'N'],
			"ENG_OIL_QUANTITY:index": ["Engine oil quantitiy as a percentage of full capacity", b'ENG OIL QUANTITY:index', b'Percent over 100', 'N'],
			"ENG_HYDRAULIC_PRESSURE:index": ["Engine hydraulic pressure", b'ENG HYDRAULIC PRESSURE:index', b'foot pounds', 'N'],
			"ENG_HYDRAULIC_QUANTITY:index": ["Engine hydraulic fluid quantity, as a percentage of total capacity", b'ENG HYDRAULIC QUANTITY:index', b'Percent over 100', 'N'],
			"ENG_MANIFOLD_PRESSURE:index": ["Engine manifold pressure.", b'ENG MANIFOLD PRESSURE:index', b'inHG.', 'N'],
			"ENG_VIBRATION:index": ["Engine vibration", b'ENG VIBRATION:index', b'Number', 'N'],
			"ENG_RPM_SCALER:index": ["Obsolete", b'ENG RPM SCALER:index', b'Scalar', 'N'],
			"ENG_MAX_RPM": ["Maximum rpm", b'ENG MAX RPM', b'Rpm', 'N'],
			"GENERAL_ENG_STARTER_ACTIVE": ["True if engine starter is active", b'GENERAL ENG STARTER ACTIVE', b'Bool', 'N'],
			"GENERAL_ENG_FUEL_USED_SINCE_START": ["Fuel used since the engines were last started", b'GENERAL ENG FUEL USED SINCE START', b'Pounds', 'N'],
			"TURB_ENG_PRIMARY_NOZZLE_PERCENT:index": ["Percent thrust of primary nozzle", b'TURB ENG PRIMARY NOZZLE PERCENT:index', b'Percent over 100', 'N'],
			"TURB_ENG_IGNITION_SWITCH": ["True if the turbine engine ignition switch is on", b'TURB ENG IGNITION SWITCH', b'Bool', 'N'],
			"TURB_ENG_MASTER_STARTER_SWITCH": ["True if the turbine engine master starter switch is on", b'TURB ENG MASTER STARTER SWITCH', b'Bool', 'N'],
			"TURB_ENG_AFTERBURNER_STAGE_ACTIVE": ["The stage of the afterburner, or 0 if the afterburner is not active.", b'TURB ENG AFTERBURNER STAGE ACTIVE', b'Number', 'N'],
		}

	class __FuelTankSelection(RequestHelper):
		list = {
		}

	class __AircraftFuelData(RequestHelper):
		list = {
			"FUEL_TANK_CENTER_LEVEL": ["Percent of maximum capacity", b'FUEL TANK CENTER LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_CENTER2_LEVEL": ["Percent of maximum capacity", b'FUEL TANK CENTER2 LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_CENTER3_LEVEL": ["Percent of maximum capacity", b'FUEL TANK CENTER3 LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_LEFT_MAIN_LEVEL": ["Percent of maximum capacity", b'FUEL TANK LEFT MAIN LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_LEFT_AUX_LEVEL": ["Percent of maximum capacity", b'FUEL TANK LEFT AUX LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_LEFT_TIP_LEVEL": ["Percent of maximum capacity", b'FUEL TANK LEFT TIP LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_RIGHT_MAIN_LEVEL": ["Percent of maximum capacity", b'FUEL TANK RIGHT MAIN LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_RIGHT_AUX_LEVEL": ["Percent of maximum capacity", b'FUEL TANK RIGHT AUX LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_RIGHT_TIP_LEVEL": ["Percent of maximum capacity", b'FUEL TANK RIGHT TIP LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_EXTERNAL1_LEVEL": ["Percent of maximum capacity", b'FUEL TANK EXTERNAL1 LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_EXTERNAL2_LEVEL": ["Percent of maximum capacity", b'FUEL TANK EXTERNAL2 LEVEL', b'Percent Over 100', 'Y'],
			"FUEL_TANK_CENTER_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK CENTER CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_CENTER2_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK CENTER2 CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_CENTER3_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK CENTER3 CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_LEFT_MAIN_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK LEFT MAIN CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_LEFT_AUX_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK LEFT AUX CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_LEFT_TIP_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK LEFT TIP CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_RIGHT_MAIN_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK RIGHT MAIN CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_RIGHT_AUX_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK RIGHT AUX CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_RIGHT_TIP_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK RIGHT TIP CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_EXTERNAL1_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK EXTERNAL1 CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_EXTERNAL2_CAPACITY": ["Maximum capacity in volume", b'FUEL TANK EXTERNAL2 CAPACITY', b'Gallons', 'N'],
			"FUEL_LEFT_CAPACITY": ["Maximum capacity in volume", b'FUEL LEFT CAPACITY', b'Gallons', 'N'],
			"FUEL_RIGHT_CAPACITY": ["Maximum capacity in volume", b'FUEL RIGHT CAPACITY', b'Gallons', 'N'],
			"FUEL_TANK_CENTER_QUANTITY": ["Current quantity in volume", b'FUEL TANK CENTER QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_CENTER2_QUANTITY": ["Current quantity in volume", b'FUEL TANK CENTER2 QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_CENTER3_QUANTITY": ["Current quantity in volume", b'FUEL TANK CENTER3 QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_LEFT_MAIN_QUANTITY": ["Current quantity in volume", b'FUEL TANK LEFT MAIN QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_LEFT_AUX_QUANTITY": ["Current quantity in volume", b'FUEL TANK LEFT AUX QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_LEFT_TIP_QUANTITY": ["Current quantity in volume", b'FUEL TANK LEFT TIP QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_RIGHT_MAIN_QUANTITY": ["Current quantity in volume", b'FUEL TANK RIGHT MAIN QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_RIGHT_AUX_QUANTITY": ["Current quantity in volume", b'FUEL TANK RIGHT AUX QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_RIGHT_TIP_QUANTITY": ["Current quantity in volume", b'FUEL TANK RIGHT TIP QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_EXTERNAL1_QUANTITY": ["Current quantity in volume", b'FUEL TANK EXTERNAL1 QUANTITY', b'Gallons', 'Y'],
			"FUEL_TANK_EXTERNAL2_QUANTITY": ["Current quantity in volume", b'FUEL TANK EXTERNAL2 QUANTITY', b'Gallons', 'Y'],
			"FUEL_LEFT_QUANTITY": ["Current quantity in volume", b'FUEL LEFT QUANTITY', b'Gallons', 'N'],
			"FUEL_RIGHT_QUANTITY": ["Current quantity in volume", b'FUEL RIGHT QUANTITY', b'Gallons', 'N'],
			"FUEL_TOTAL_QUANTITY": ["Current quantity in volume", b'FUEL TOTAL QUANTITY', b'Gallons', 'N'],
			"FUEL_WEIGHT_PER_GALLON": ["Fuel weight per gallon", b'FUEL WEIGHT PER GALLON', b'Pounds', 'N'],
			"FUEL_TANK_SELECTOR:index": ["Which tank is selected. See fuel tank list.", b'FUEL TANK SELECTOR:index', b'Enum', 'N'],
			"FUEL_CROSS_FEED": ["Cross feed valve:; 0 = Closed; 1 = Open", b'FUEL CROSS FEED', b'Enum', 'N'],
			"FUEL_TOTAL_CAPACITY": ["Total capacity of the aircraft", b'FUEL TOTAL CAPACITY', b'Gallons', 'N'],
			"FUEL_SELECTED_QUANTITY_PERCENT": ["Percent or capacity for selected tank", b'FUEL SELECTED QUANTITY PERCENT', b'Percent Over 100', 'N'],
			"FUEL_SELECTED_QUANTITY": ["Quantity of selected tank", b'FUEL SELECTED QUANTITY', b'Gallons', 'N'],
			"FUEL_TOTAL_QUANTITY_WEIGHT": ["Current total fuel weight of the aircraft", b'FUEL TOTAL QUANTITY WEIGHT', b'Pounds', 'N'],
			"NUM_FUEL_SELECTORS": ["Number of selectors on the aircraft", b'NUM FUEL SELECTORS', b'Number', 'N'],
			"UNLIMITED_FUEL": ["Unlimited fuel flag", b'UNLIMITED FUEL', b'Bool', 'N'],
			"ESTIMATED_FUEL_FLOW": ["Estimated fuel flow at cruise", b'ESTIMATED FUEL FLOW', b'Pounds per hour', 'N'],
		}

	class __AircraftLightsData(RequestHelper):
		list = {
			"LIGHT_STROBE": ["Light switch state", b'LIGHT STROBE', b'Bool', 'N'],
			"LIGHT_PANEL": ["Light switch state", b'LIGHT PANEL', b'Bool', 'N'],
			"LIGHT_LANDING": ["Light switch state", b'LIGHT LANDING', b'Bool', 'N'],
			"LIGHT_TAXI": ["Light switch state", b'LIGHT TAXI', b'Bool', 'N'],
			"LIGHT_BEACON": ["Light switch state", b'LIGHT BEACON', b'Bool', 'N'],
			"LIGHT_NAV": ["Light switch state", b'LIGHT NAV', b'Bool', 'N'],
			"LIGHT_LOGO": ["Light switch state", b'LIGHT LOGO', b'Bool', 'N'],
			"LIGHT_WING": ["Light switch state", b'LIGHT WING', b'Bool', 'N'],
			"LIGHT_RECOGNITION": ["Light switch state", b'LIGHT RECOGNITION', b'Bool', 'N'],
			"LIGHT_CABIN": ["Light switch state", b'LIGHT CABIN', b'Bool', 'N'],
			"LIGHT_ON_STATES": ["Bit mask:; 0x0001: Nav; 0x0002: Beacon; 0x0004: Landing; 0x0008: Taxi; 0x0010: Strobe; 0x0020: Panel; 0x0040: Recognition; 0x0080: Wing; 0x0100: Logo; 0x0200: Cabin", b'LIGHT ON STATES', b'Mask', 'N'],
			"LIGHT_STATES": ["Same as LIGHT ON STATES", b'LIGHT STATES', b'Mask', 'N'],
			# "LANDING_LIGHT_PBH": ["Landing light pitch bank and heading", b'LANDING LIGHT PBH', b'SIMCONNECT_DATA_XYZ', 'N'],
			"LIGHT_TAXI_ON": ["Return true if the light is on.", b'LIGHT TAXI ON', b'Bool', 'N'],
			"LIGHT_STROBE_ON": ["Return true if the light is on.", b'LIGHT STROBE ON', b'Bool', 'N'],
			"LIGHT_PANEL_ON": ["Return true if the light is on.", b'LIGHT PANEL ON', b'Bool', 'N'],
			"LIGHT_RECOGNITION_ON": ["Return true if the light is on.", b'LIGHT RECOGNITION ON', b'Bool', 'N'],
			"LIGHT_WING_ON": ["Return true if the light is on.", b'LIGHT WING ON', b'Bool', 'N'],
			"LIGHT_LOGO_ON": ["Return true if the light is on.", b'LIGHT LOGO ON', b'Bool', 'N'],
			"LIGHT_CABIN_ON": ["Return true if the light is on.", b'LIGHT CABIN ON', b'Bool', 'N'],
			"LIGHT_HEAD_ON": ["Return true if the light is on.", b'LIGHT HEAD ON', b'Bool', 'N'],
			"LIGHT_BRAKE_ON": ["Return true if the light is on.", b'LIGHT BRAKE ON', b'Bool', 'N'],
			"LIGHT_NAV_ON": ["Return true if the light is on.", b'LIGHT NAV ON', b'Bool', 'N'],
			"LIGHT_BEACON_ON": ["Return true if the light is on.", b'LIGHT BEACON ON', b'Bool', 'N'],
			"LIGHT_LANDING_ON": ["Return true if the light is on.", b'LIGHT LANDING ON', b'Bool', 'N'],
		}

	class __AircraftPositionandSpeedData(RequestHelper):
		list = {
			"GROUND_VELOCITY": ["Speed relative to the earths surface", b'GROUND VELOCITY', b'Knots', 'N'],
			"TOTAL_WORLD_VELOCITY": ["Speed relative to the earths center", b'TOTAL WORLD VELOCITY', b'Feet per second', 'N'],
			"VELOCITY_BODY_Z": ["True longitudinal speed, relative to aircraft axis", b'VELOCITY BODY Z', b'Feet per second', 'Y'],
			"VELOCITY_BODY_X": ["True lateral speed, relative to aircraft axis", b'VELOCITY BODY X', b'Feet per second', 'Y'],
			"VELOCITY_BODY_Y": ["True vertical speed, relative to aircraft axis", b'VELOCITY BODY Y', b'Feet per second', 'Y'],
			"VELOCITY_WORLD_Z": ["Speed relative to earth, in North/South direction", b'VELOCITY WORLD Z', b'Feet per second', 'Y'],
			"VELOCITY_WORLD_X": ["Speed relative to earth, in East/West direction", b'VELOCITY WORLD X', b'Feet per second', 'Y'],
			"VELOCITY_WORLD_Y": ["Speed relative to earth, in vertical direction", b'VELOCITY WORLD Y', b'Feet per second', 'Y'],
			"ACCELERATION_WORLD_X": ["Acceleration relative to earth, in east/west direction", b'ACCELERATION WORLD X', b'Feet per second squared', 'Y'],
			"ACCELERATION_WORLD_Y": ["Acceleration relative to earch, in vertical direction", b'ACCELERATION WORLD Y', b'Feet per second squared', 'Y'],
			"ACCELERATION_WORLD_Z": ["Acceleration relative to earth, in north/south direction", b'ACCELERATION WORLD Z', b'Feet per second squared', 'Y'],
			"ACCELERATION_BODY_X": ["Acceleration relative to aircraft axix, in east/west direction", b'ACCELERATION BODY X', b'Feet per second squared', 'Y'],
			"ACCELERATION_BODY_Y": ["Acceleration relative to aircraft axis, in vertical direction", b'ACCELERATION BODY Y', b'Feet per second squared', 'Y'],
			"ACCELERATION_BODY_Z": ["Acceleration relative to aircraft axis, in north/south direction", b'ACCELERATION BODY Z', b'Feet per second squared', 'Y'],
			"ROTATION_VELOCITY_BODY_X": ["Rotation relative to aircraft axis", b'ROTATION VELOCITY BODY X', b'Feet per second', 'Y'],
			"ROTATION_VELOCITY_BODY_Y": ["Rotation relative to aircraft axis", b'ROTATION VELOCITY BODY Y', b'Feet per second', 'Y'],
			"ROTATION_VELOCITY_BODY_Z": ["Rotation relative to aircraft axis", b'ROTATION VELOCITY BODY Z', b'Feet per second', 'Y'],
			"RELATIVE_WIND_VELOCITY_BODY_X": ["Lateral speed relative to wind", b'RELATIVE WIND VELOCITY BODY X', b'Feet per second', 'N'],
			"RELATIVE_WIND_VELOCITY_BODY_Y": ["Vertical speed relative to wind", b'RELATIVE WIND VELOCITY BODY Y', b'Feet per second', 'N'],
			"RELATIVE_WIND_VELOCITY_BODY_Z": ["Longitudinal speed relative to wind", b'RELATIVE WIND VELOCITY BODY Z', b'Feet per second', 'N'],
			"PLANE_ALT_ABOVE_GROUND": ["Altitude above the surface", b'PLANE ALT ABOVE GROUND', b'Feet', 'Y'],
			"PLANE_LATITUDE": ["Latitude of aircraft, North is positive, South negative", b'PLANE LATITUDE', b'Degrees', 'Y'],
			"PLANE_LONGITUDE": ["Longitude of aircraft, East is positive, West negative", b'PLANE LONGITUDE', b'Degrees', 'Y'],
			"PLANE_ALTITUDE": ["Altitude of aircraft", b'PLANE ALTITUDE', b'Feet', 'Y'],
			"PLANE_PITCH_DEGREES": ["Pitch angle, although the name mentions degrees the units used are radians", b'PLANE PITCH DEGREES', b'Radians', 'Y'],
			"PLANE_BANK_DEGREES": ["Bank angle, although the name mentions degrees the units used are radians", b'PLANE BANK DEGREES', b'Radians', 'Y'],
			"PLANE_HEADING_DEGREES_TRUE": ["Heading relative to true north, although the name mentions degrees the units used are radians", b'PLANE HEADING DEGREES TRUE', b'Radians', 'Y'],
			"PLANE_HEADING_DEGREES_MAGNETIC": ["Heading relative to magnetic north, although the name mentions degrees the units used are radians", b'PLANE HEADING DEGREES MAGNETIC', b'Radians', 'Y'],
			"MAGVAR": ["Magnetic variation", b'MAGVAR', b'Degrees', 'N'],
			"GROUND_ALTITUDE": ["Altitude of surface", b'GROUND ALTITUDE', b'Meters', 'N'],
			"SIM_ON_GROUND": ["On ground flag", b'SIM ON GROUND', b'Bool', 'N'],
			"INCIDENCE_ALPHA": ["Angle of attack", b'INCIDENCE ALPHA', b'Radians', 'N'],
			"INCIDENCE_BETA": ["Sideslip angle", b'INCIDENCE BETA', b'Radians', 'N'],
			"WING_FLEX_PCT:index": ["The current wing flex. Different values can be set for each wing (for example, during banking). Set an index of 1 for the left wing, and 2 for the right wing.", b'WING FLEX PCT:index', b'Percent over 100', 'Y'],
			"PLANE_TOUCHDOWN_NORMAL_VELOCITY": ["Vertical speed at landing.", b'PLANE TOUCHDOWN NORMAL VELOCITY', b'Feet per second', 'N'],
			# "STRUCT_LATLONALT": ["Returns the latitude, longitude and altitude of the user aircraft.", b'STRUCT LATLONALT', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "STRUCT_LATLONALTPBH": ["Returns the pitch, bank and heading of the user aircraft.", b'STRUCT LATLONALTPBH', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "STRUCT_SURFACE_RELATIVE_VELOCITY": ["The relative surface velocity.", b'STRUCT SURFACE RELATIVE VELOCITY', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_WORLDVELOCITY": ["The world velocity.", b'STRUCT WORLDVELOCITY', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_WORLD_ROTATION_VELOCITY": ["The world rotation velocity.", b'STRUCT WORLD ROTATION VELOCITY', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_BODY_VELOCITY": ["The object body velocity.", b'STRUCT BODY VELOCITY', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_BODY_ROTATION_VELOCITY": ["The body rotation velocity. Individual body rotation values are in the Aircraft Position and Speed section.", b'STRUCT BODY ROTATION VELOCITY', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_WORLD_ACCELERATION": ["The world acceleration for each axis. Individual world acceleration values are in the Aircraft Position and Speed section.", b'STRUCT WORLD ACCELERATION', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_ENGINE_POSITION:index": ["The engine position relative to the reference datum position for the aircraft.", b'STRUCT ENGINE POSITION:index', b'SIMCONNECT_DATA_XYZ.', 'N'],
			# "STRUCT_EYEPOINT_DYNAMIC_ANGLE": ["The angle of the eyepoint view. Zero, zero, zero is straight ahead.", b'STRUCT EYEPOINT DYNAMIC ANGLE', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "STRUCT_EYEPOINT_DYNAMIC_OFFSET": ["A variable offset away from the EYEPOINT POSITION", b'STRUCT EYEPOINT DYNAMIC OFFSET', b'SIMCONNECT_DATA_XYZ', 'N'],
			# "EYEPOINT_POSITION": ["The eyepoint position relative to the reference datum position for the aircraft.", b'EYEPOINT POSITION', b'SIMCONNECT_DATA_XYZ', 'N'],
		}

	class __AircraftFlightInstrumentationData(RequestHelper):
		list = {
			"AIRSPEED_TRUE": ["True airspeed", b'AIRSPEED TRUE', b'Knots', 'Y'],
			"AIRSPEED_INDICATED": ["Indicated airspeed", b'AIRSPEED INDICATED', b'Knots', 'Y'],
			"AIRSPEED_TRUE_CALIBRATE": ["Angle of True calibration scale on airspeed indicator", b'AIRSPEED TRUE CALIBRATE', b'Degrees', 'Y'],
			"AIRSPEED_BARBER_POLE": ["Redline airspeed (dynamic on some aircraft)", b'AIRSPEED BARBER POLE', b'Knots', 'N'],
			"AIRSPEED_MACH": ["Current mach", b'AIRSPEED MACH', b'Mach', 'N'],
			"VERTICAL_SPEED": ["Vertical speed indication", b'VERTICAL SPEED', b'feet/minute', 'Y'],
			"MACH_MAX_OPERATE": ["Maximum design mach", b'MACH MAX OPERATE', b'Mach', 'N'],
			"STALL_WARNING": ["Stall warning state", b'STALL WARNING', b'Bool', 'N'],
			"OVERSPEED_WARNING": ["Overspeed warning state", b'OVERSPEED WARNING', b'Bool', 'N'],
			"BARBER_POLE_MACH": ["Mach associated with maximum airspeed", b'BARBER POLE MACH', b'Mach', 'N'],
			"INDICATED_ALTITUDE": ["Altimeter indication", b'INDICATED ALTITUDE', b'Feet', 'Y'],
			"KOHLSMAN_SETTING_MB": ["Altimeter setting", b'KOHLSMAN SETTING MB', b'Millibars', 'Y'],
			"KOHLSMAN_SETTING_HG": ["Altimeter setting", b'KOHLSMAN SETTING HG', b'inHg', 'N'],
			"ATTITUDE_INDICATOR_PITCH_DEGREES": ["AI pitch indication", b'ATTITUDE INDICATOR PITCH DEGREES', b'Radians', 'N'],
			"ATTITUDE_INDICATOR_BANK_DEGREES": ["AI bank indication", b'ATTITUDE INDICATOR BANK DEGREES', b'Radians', 'N'],
			"ATTITUDE_BARS_POSITION": ["AI reference pitch reference bars", b'ATTITUDE BARS POSITION', b'Percent Over 100', 'N'],
			"ATTITUDE_CAGE": ["AI caged state", b'ATTITUDE CAGE', b'Bool', 'N'],
			"WISKEY_COMPASS_INDICATION_DEGREES": ["Magnetic compass indication", b'WISKEY COMPASS INDICATION DEGREES', b'Degrees', 'Y'],
			"PLANE_HEADING_DEGREES_GYRO": ["Heading indicator (directional gyro) indication", b'PLANE HEADING DEGREES GYRO', b'Radians', 'Y'],
			"HEADING_INDICATOR": ["Heading indicator (directional gyro) indication", b'HEADING INDICATOR', b'Radians', 'N'],
			"GYRO_DRIFT_ERROR": ["Angular error of heading indicator", b'GYRO DRIFT ERROR', b'Radians', 'N'],
			"DELTA_HEADING_RATE": ["Rate of turn of heading indicator", b'DELTA HEADING RATE', b'Radians per second', 'Y'],
			"TURN_COORDINATOR_BALL": ["Turn coordinator ball position", b'TURN COORDINATOR BALL', b'Position', 'N'],
			"ANGLE_OF_ATTACK_INDICATOR": ["AoA indication", b'ANGLE OF ATTACK INDICATOR', b'Radians', 'N'],
			"RADIO_HEIGHT": ["Radar altitude", b'RADIO HEIGHT', b'Feet', 'N'],
			"PARTIAL_PANEL_ADF": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL ADF', b'Enum', 'Y'],
			"PARTIAL_PANEL_AIRSPEED": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL AIRSPEED', b'Enum', 'Y'],
			"PARTIAL_PANEL_ALTIMETER": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL ALTIMETER', b'Enum', 'Y'],
			"PARTIAL_PANEL_ATTITUDE": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL ATTITUDE', b'Enum', 'Y'],
			"PARTIAL_PANEL_COMM": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL COMM', b'Enum', 'Y'],
			"PARTIAL_PANEL_COMPASS": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL COMPASS', b'Enum', 'Y'],
			"PARTIAL_PANEL_ELECTRICAL": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL ELECTRICAL', b'Enum', 'Y'],
			"PARTIAL_PANEL_AVIONICS": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL AVIONICS', b'Enum', 'N'],
			"PARTIAL_PANEL_ENGINE": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL ENGINE', b'Enum', 'Y'],
			"PARTIAL_PANEL_FUEL_INDICATOR": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL FUEL INDICATOR', b'Enum', 'N'],
			"PARTIAL_PANEL_HEADING": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL HEADING', b'Enum', 'Y'],
			"PARTIAL_PANEL_VERTICAL_VELOCITY": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL VERTICAL VELOCITY', b'Enum', 'Y'],
			"PARTIAL_PANEL_TRANSPONDER": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL TRANSPONDER', b'Enum', 'Y'],
			"PARTIAL_PANEL_NAV": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL NAV', b'Enum', 'Y'],
			"PARTIAL_PANEL_PITOT": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL PITOT', b'Enum', 'Y'],
			"PARTIAL_PANEL_TURN_COORDINATOR": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL TURN COORDINATOR', b'Enum', 'N'],
			"PARTIAL_PANEL_VACUUM": ["Gauge fail flag (0 = ok, 1 = fail, 2 = blank)", b'PARTIAL PANEL VACUUM', b'Enum', 'Y'],
			"MAX_G_FORCE": ["Maximum G force attained", b'MAX G FORCE', b'Gforce', 'N'],
			"MIN_G_FORCE": ["Minimum G force attained", b'MIN G FORCE', b'Gforce', 'N'],
			"SUCTION_PRESSURE": ["Vacuum system suction pressure", b'SUCTION PRESSURE', b'inHg', 'Y'],
		}

	class __AircraftAvionicsData(RequestHelper):
		list = {
			"AVIONICS_MASTER_SWITCH": ["Avionics switch state", b'AVIONICS MASTER SWITCH', b'Bool', 'N'],
			"NAV_SOUND:index": ["Nav audio flag. Index of 1 or 2.", b'NAV SOUND:index', b'Bool', 'N'],
			"DME_SOUND": ["DME audio flag", b'DME SOUND', b'Bool', 'N'],
			"ADF_SOUND:index": ["ADF audio flag. Index of 0 or 1.", b'ADF SOUND:index', b'Bool', 'N'],
			"MARKER_SOUND": ["Marker audio flag", b'MARKER SOUND', b'Bool', 'N'],
			"COM_TRANSMIT:index": ["Audio panel com transmit state. Index of 1 or 2.", b'COM TRANSMIT:index', b'Bool', 'N'],
			"COM_RECIEVE_ALL": ["Flag if all Coms receiving", b'COM RECIEVE ALL', b'Bool', 'N'],
			"COM_ACTIVE_FREQUENCY:index": ["Com frequency. Index is 1 or 2.", b'COM ACTIVE FREQUENCY:index', b'MHz', 'N'],
			"COM_STANDBY_FREQUENCY:index": ["Com standby frequency. Index is 1 or 2.", b'COM STANDBY FREQUENCY:index', b'MHz', 'N'],
			"NAV_AVAILABLE:index": ["Flag if Nav equipped on aircraft", b'NAV AVAILABLE:index', b'Bool', 'N'],
			"NAV_ACTIVE_FREQUENCY:index": ["Nav active frequency. Index is 1 or 2.", b'NAV ACTIVE FREQUENCY:index', b'MHz', 'N'],
			"NAV_STANDBY_FREQUENCY:index": ["Nav standby frequency. Index is 1 or 2.", b'NAV STANDBY FREQUENCY:index', b'MHz', 'N'],
			"NAV_SIGNAL:index": ["Nav signal strength", b'NAV SIGNAL:index', b'Number', 'N'],
			"NAV_HAS_NAV:index": ["Flag if Nav has signal", b'NAV HAS NAV:index', b'Bool', 'N'],
			"NAV_HAS_LOCALIZER:index": ["Flag if tuned station is a localizer", b'NAV HAS LOCALIZER:index', b'Bool', 'N'],
			"NAV_HAS_DME:index": ["Flag if tuned station has a DME", b'NAV HAS DME:index', b'Bool', 'N'],
			"NAV_HAS_GLIDE_SLOPE:index": ["Flag if tuned station has a glideslope", b'NAV HAS GLIDE SLOPE:index', b'Bool', 'N'],
			"NAV_BACK_COURSE_FLAGS:index": ["Returns the following bit flags:; BIT0: 1=back course available; BIT1: 1=localizer tuned in; BIT2: 1=on course; BIT7: 1=station active", b'NAV BACK COURSE FLAGS:index', b'Flags', 'N'],
			"NAV_MAGVAR:index": ["Magnetic variation of tuned nav station", b'NAV MAGVAR:index', b'Degrees', 'N'],
			"NAV_RADIAL:index": ["Radial that aircraft is on", b'NAV RADIAL:index', b'Degrees', 'N'],
			"NAV_RADIAL_ERROR:index": ["Difference between current radial and OBS tuned radial", b'NAV RADIAL ERROR:index', b'Degrees', 'N'],
			"NAV_LOCALIZER:index": ["Localizer course heading", b'NAV LOCALIZER:index', b'Degrees', 'N'],
			"NAV_GLIDE_SLOPE_ERROR:index": ["Difference between current position and glideslope angle. Note that this provides 32 bit floating point precision, rather than the 8 bit integer precision of NAV GSI.", b'NAV GLIDE SLOPE ERROR:index', b'Degrees', 'N'],
			"NAV_CDI:index": ["CDI needle deflection (+/- 127)", b'NAV CDI:index', b'Number', 'N'],
			"NAV_GSI:index": ["Glideslope needle deflection (+/- 119). Note that this provides only 8 bit precision, whereas NAV GLIDE SLOPE ERROR provides 32 bit floating point precision.", b'NAV GSI:index', b'Number', 'N'],
			"NAV_GS_FLAG:index": ["Glideslope flag", b'NAV GS FLAG:index', b'Bool', 'N'],
			"NAV_OBS:index": ["OBS setting. Index of 1 or 2.", b'NAV OBS:index', b'Degrees', 'N'],
			"NAV_DME:index": ["DME distance", b'NAV DME:index', b'Nautical miles', 'N'],
			"NAV_DMESPEED:index": ["DME speed", b'NAV DMESPEED:index', b'Knots', 'N'],
			"ADF_ACTIVE_FREQUENCY:index": ["ADF frequency. Index of 1 or 2.", b'ADF ACTIVE FREQUENCY:index', b'Frequency ADF BCD32', 'N'],
			"ADF_STANDBY_FREQUENCY:index": ["ADF standby frequency", b'ADF STANDBY FREQUENCY:index', b'Hz', 'N'],
			"ADF_RADIAL:index": ["Current direction from NDB station", b'ADF RADIAL:index', b'Degrees', 'N'],
			"ADF_SIGNAL:index": ["Signal strength", b'ADF SIGNAL:index', b'Number', 'N'],
			"TRANSPONDER_CODE:index": ["4-digit code", b'TRANSPONDER CODE:index', b'BCO16', 'N'],
			"MARKER_BEACON_STATE": ["Marker beacon state:; 0 = None; 1 = Outer; 2 = Middle; 3 = Inner", b'MARKER BEACON STATE', b'Enum', 'Y'],
			"INNER_MARKER": ["Inner marker state", b'INNER MARKER', b'Bool', 'Y'],
			"MIDDLE_MARKER": ["Middle marker state", b'MIDDLE MARKER', b'Bool', 'Y'],
			"OUTER_MARKER": ["Outer marker state", b'OUTER MARKER', b'Bool', 'Y'],
			"NAV_RAW_GLIDE_SLOPE:index": ["Glide slope angle", b'NAV RAW GLIDE SLOPE:index', b'Degrees', 'N'],
			"ADF_CARD": ["ADF compass rose setting", b'ADF CARD', b'Degrees', 'N'],
			"HSI_CDI_NEEDLE": ["Needle deflection (+/- 127)", b'HSI CDI NEEDLE', b'Number', 'N'],
			"HSI_GSI_NEEDLE": ["Needle deflection (+/- 119)", b'HSI GSI NEEDLE', b'Number', 'N'],
			"HSI_CDI_NEEDLE_VALID": ["Signal valid", b'HSI CDI NEEDLE VALID', b'Bool', 'N'],
			"HSI_GSI_NEEDLE_VALID": ["Signal valid", b'HSI GSI NEEDLE VALID', b'Bool', 'N'],
			"HSI_TF_FLAGS": ["Nav TO/FROM flag:; 0 = Off; 1 = TO; 2 = FROM", b'HSI TF FLAGS', b'Enum', 'N'],
			"HSI_BEARING_VALID": ["This will return true if the HSI BEARING variable contains valid data.", b'HSI BEARING VALID', b'Bool', 'N'],
			"HSI_BEARING": ["If the GPS DRIVES NAV1 variable is true and the HSI BEARING VALID variable is true, this variable contains the HSI needle bearing. If the GPS DRIVES NAV1 variable is false and the HSI BEARING VALID variable is true, this variable contains the ADF1 frequency.", b'HSI BEARING', b'Degrees', 'N'],
			"HSI_HAS_LOCALIZER": ["Station is a localizer", b'HSI HAS LOCALIZER', b'Bool', 'N'],
			"HSI_SPEED": ["DME/GPS speed", b'HSI SPEED', b'Knots', 'N'],
			"HSI_DISTANCE": ["DME/GPS distance", b'HSI DISTANCE', b'Nautical miles', 'N'],
			"GPS_POSITION_LAT": ["Current GPS latitude", b'GPS POSITION LAT', b'Degrees', 'N'],
			"GPS_POSITION_LON": ["Current GPS longitude", b'GPS POSITION LON', b'Degrees', 'N'],
			"GPS_POSITION_ALT": ["Current GPS altitude", b'GPS POSITION ALT', b'Meters', 'N'],
			"GPS_MAGVAR": ["Current GPS magnetic variation", b'GPS MAGVAR', b'Radians', 'N'],
			"GPS_IS_ACTIVE_FLIGHT_PLAN": ["Flight plan mode active", b'GPS IS ACTIVE FLIGHT PLAN', b'Bool', 'N'],
			"GPS_IS_ACTIVE_WAY_POINT": ["Waypoint mode active", b'GPS IS ACTIVE WAY POINT', b'Bool', 'N'],
			"GPS_IS_ARRIVED": ["Is flight plan destination reached", b'GPS IS ARRIVED', b'Bool', 'N'],
			"GPS_IS_DIRECTTO_FLIGHTPLAN": ["Is Direct To Waypoint mode active", b'GPS IS DIRECTTO FLIGHTPLAN', b'Bool', 'N'],
			"GPS_GROUND_SPEED": ["Current ground speed", b'GPS GROUND SPEED', b'Meters per second', 'N'],
			"GPS_GROUND_TRUE_HEADING": ["Current true heading", b'GPS GROUND TRUE HEADING', b'Radians', 'N'],
			"GPS_GROUND_MAGNETIC_TRACK": ["Current magnetic ground track", b'GPS GROUND MAGNETIC TRACK', b'Radians', 'N'],
			"GPS_GROUND_TRUE_TRACK": ["Current true ground track", b'GPS GROUND TRUE TRACK', b'Radians', 'N'],
			"GPS_WP_DISTANCE": ["Distance to waypoint", b'GPS WP DISTANCE', b'Meters', 'N'],
			"GPS_WP_BEARING": ["Magnetic bearing to waypoint", b'GPS WP BEARING', b'Radians', 'N'],
			"GPS_WP_TRUE_BEARING": ["True bearing to waypoint", b'GPS WP TRUE BEARING', b'Radians', 'N'],
			"GPS_WP_CROSS_TRK": ["Cross track distance", b'GPS WP CROSS TRK', b'Meters', 'N'],
			"GPS_WP_DESIRED_TRACK": ["Desired track to waypoint", b'GPS WP DESIRED TRACK', b'Radians', 'N'],
			"GPS_WP_TRUE_REQ_HDG": ["Required true heading to waypoint", b'GPS WP TRUE REQ HDG', b'Radians', 'N'],
			"GPS_WP_VERTICAL_SPEED": ["Vertical speed to waypoint", b'GPS WP VERTICAL SPEED', b'Meters per second', 'N'],
			"GPS_WP_TRACK_ANGLE_ERROR": ["Tracking angle error to waypoint", b'GPS WP TRACK ANGLE ERROR', b'Radians', 'N'],
			"GPS_ETE": ["Estimated time enroute to destination", b'GPS ETE', b'Seconds', 'N'],
			"GPS_ETA": ["Estimated time of arrival at destination", b'GPS ETA', b'Seconds', 'N'],
			"GPS_WP_NEXT_LAT": ["Latitude of next waypoint", b'GPS WP NEXT LAT', b'Degrees', 'N'],
			"GPS_WP_NEXT_LON": ["Longitude of next waypoint", b'GPS WP NEXT LON', b'Degrees', 'N'],
			"GPS_WP_NEXT_ALT": ["Altitude of next waypoint", b'GPS WP NEXT ALT', b'Meters', 'N'],
			"GPS_WP_PREV_VALID": ["Is previous waypoint valid (i.e. current waypoint is not the first waypoint)", b'GPS WP PREV VALID', b'Bool', 'N'],
			"GPS_WP_PREV_LAT": ["Latitude of previous waypoint", b'GPS WP PREV LAT', b'Degrees', 'N'],
			"GPS_WP_PREV_LON": ["Longitude of previous waypoint", b'GPS WP PREV LON', b'Degrees', 'N'],
			"GPS_WP_PREV_ALT": ["Altitude of previous waypoint", b'GPS WP PREV ALT', b'Meters', 'N'],
			"GPS_WP_ETE": ["Estimated time enroute to waypoint", b'GPS WP ETE', b'Seconds', 'N'],
			"GPS_WP_ETA": ["Estimated time of arrival at waypoint", b'GPS WP ETA', b'Seconds', 'N'],
			"GPS_COURSE_TO_STEER": ["Suggested heading to steer (for autopilot)", b'GPS COURSE TO STEER', b'Radians', 'N'],
			"GPS_FLIGHT_PLAN_WP_INDEX": ["Index of waypoint", b'GPS FLIGHT PLAN WP INDEX', b'Number', 'N'],
			"GPS_FLIGHT_PLAN_WP_COUNT": ["Number of waypoints", b'GPS FLIGHT PLAN WP COUNT', b'Number', 'N'],
			"GPS_IS_ACTIVE_WP_LOCKED": ["Is switching to next waypoint locked", b'GPS IS ACTIVE WP LOCKED', b'Bool', 'N'],
			"GPS_IS_APPROACH_LOADED": ["Is approach loaded", b'GPS IS APPROACH LOADED', b'Bool', 'N'],
			"GPS_IS_APPROACH_ACTIVE": ["Is approach mode active", b'GPS IS APPROACH ACTIVE', b'Bool', 'N'],
			"GPS_APPROACH_IS_WP_RUNWAY": ["Waypoint is the runway", b'GPS APPROACH IS WP RUNWAY', b'Bool', 'N'],
			"GPS_APPROACH_APPROACH_INDEX": ["Index of approach for given airport", b'GPS APPROACH APPROACH INDEX', b'Number', 'N'],
			"GPS_APPROACH_TRANSITION_INDEX": ["Index of approach transition", b'GPS APPROACH TRANSITION INDEX', b'Number', 'N'],
			"GPS_APPROACH_IS_FINAL": ["Is approach transition final approach segment", b'GPS APPROACH IS FINAL', b'Bool', 'N'],
			"GPS_APPROACH_IS_MISSED": ["Is approach segment missed approach segment", b'GPS APPROACH IS MISSED', b'Bool', 'N'],
			"GPS_APPROACH_TIMEZONE_DEVIATION": ["Deviation of local time from GMT", b'GPS APPROACH TIMEZONE DEVIATION', b'Seconds', 'N'],
			"GPS_APPROACH_WP_INDEX": ["Index of current waypoint", b'GPS APPROACH WP INDEX', b'Number', 'N'],
			"GPS_APPROACH_WP_COUNT": ["Number of waypoints", b'GPS APPROACH WP COUNT', b'Number', 'N'],
			"GPS_DRIVES_NAV1": ["GPS is driving Nav 1 indicator", b'GPS DRIVES NAV1', b'Bool', 'N'],
			"COM_RECEIVE_ALL": ["Toggles all COM radios to receive on", b'COM RECEIVE ALL', b'Bool', 'N'],
			"COM_AVAILABLE": ["True if either COM1 or COM2 is available", b'COM AVAILABLE', b'Bool', 'N'],
			"COM_TEST:index": ["Enter an index of 1 or 2. True if the COM system is working.", b'COM TEST:index', b'Bool', 'N'],
			"TRANSPONDER_AVAILABLE": ["True if a transponder is available", b'TRANSPONDER AVAILABLE', b'Bool', 'N'],
			"ADF_AVAILABLE": ["True if ADF is available", b'ADF AVAILABLE', b'Bool', 'N'],
			"ADF_FREQUENCY:index": ["Legacy, use ADF ACTIVE FREQUENCY", b'ADF FREQUENCY:index', b'Frequency BCD16', 'N'],
			"ADF_EXT_FREQUENCY:index": ["Legacy, use ADF ACTIVE FREQUENCY", b'ADF EXT FREQUENCY:index', b'Frequency BCD16', 'N'],
			"ADF_IDENT": ["ICAO code", b'ADF IDENT', b'String', 'N'],
			"ADF_NAME": ["Descriptive name", b'ADF NAME', b'String', 'N'],
			"NAV_IDENT": ["ICAO code", b'NAV IDENT', b'String', 'N'],
			"NAV_NAME": ["Descriptive name", b'NAV NAME', b'String', 'N'],
			"NAV_CODES:index": ["Returns bit flags with the following meaning:; BIT7: 0= VOR  1= Localizer; BIT6: 1= glideslope available; BIT5: 1= no localizer backcourse; BIT4: 1= DME transmitter at glide slope transmitter; BIT3: 1= no nav signal available; BIT2: 1= voice available; BIT1: 1 = TACAN available; BIT0: 1= DME available", b'NAV CODES:index', b'Flags', 'N'],
			"NAV_GLIDE_SLOPE": ["The glide slope gradient.", b'NAV GLIDE SLOPE', b'Number', 'N'],
			"NAV_RELATIVE_BEARING_TO_STATION:index": ["Relative bearing to station", b'NAV RELATIVE BEARING TO STATION:index', b'Degrees', 'N'],
			"SELECTED_DME": ["Selected DME", b'SELECTED DME', b'Number', 'N'],
			"GPS_WP_NEXT_ID": ["ID of next GPS waypoint", b'GPS WP NEXT ID', b'String', 'N'],
			"GPS_WP_PREV_ID": ["ID of previous GPS waypoint", b'GPS WP PREV ID', b'String', 'N'],
			"GPS_TARGET_DISTANCE": ["Distance to target", b'GPS TARGET DISTANCE', b'Meters', 'N'],
			"GPS_TARGET_ALTITUDE": ["Altitude of GPS target", b'GPS TARGET ALTITUDE', b'Meters', 'N'],
			# "ADF_LATLONALT:index": ["Returns the latitude, longitude and altitude of the station the radio equipment is currently tuned to, or zeros if the radio is not tuned to any ADF station. Index of 1 or 2 for ADF 1 and ADF 2.", b'ADF LATLONALT:index', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "NAV_VOR_LATLONALT:index": ["Returns the VOR station latitude, longitude and altitude.", b'NAV VOR LATLONALT:index', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "NAV_GS_LATLONALT:index": ["Returns the glide slope.", b'NAV GS LATLONALT:index', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "NAV_DME_LATLONALT:index": ["Returns the DME station.", b'NAV DME LATLONALT:index', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "INNER_MARKER_LATLONALT": ["Returns the latitude, longitude and altitude of the inner marker of an approach to a runway, if the aircraft is within the required proximity, otherwise it will return zeros.", b'INNER MARKER LATLONALT', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "MIDDLE_MARKER_LATLONALT": ["Returns the latitude, longitude and altitude of the middle marker.", b'MIDDLE MARKER LATLONALT', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "OUTER_MARKER_LATLONALT": ["Returns the latitude, longitude and altitude of the outer marker.", b'OUTER MARKER LATLONALT', b'SIMCONNECT_DATA_LATLONALT', 'N'],
		}

	class __AircraftControlsData(RequestHelper):
		list = {
			"YOKE_Y_POSITION": ["Percent control deflection fore/aft (for animation)", b'YOKE Y POSITION', b'Position', 'Y'],
			"YOKE_X_POSITION": ["Percent control deflection left/right (for animation)", b'YOKE X POSITION', b'Position', 'Y'],
			"RUDDER_PEDAL_POSITION": ["Percent rudder pedal deflection (for animation)", b'RUDDER PEDAL POSITION', b'Position', 'Y'],
			"RUDDER_POSITION": ["Percent rudder input deflection", b'RUDDER POSITION', b'Position', 'Y'],
			"ELEVATOR_POSITION": ["Percent elevator input deflection", b'ELEVATOR POSITION', b'Position', 'Y'],
			"AILERON_POSITION": ["Percent aileron input left/right", b'AILERON POSITION', b'Position', 'Y'],
			"ELEVATOR_TRIM_POSITION": ["Elevator trim deflection", b'ELEVATOR TRIM POSITION', b'Radians', 'Y'],
			"ELEVATOR_TRIM_INDICATOR": ["Percent elevator trim (for indication)", b'ELEVATOR TRIM INDICATOR', b'Position', 'N'],
			"ELEVATOR_TRIM_PCT": ["Percent elevator trim", b'ELEVATOR TRIM PCT', b'Percent Over 100', 'N'],
			"BRAKE_LEFT_POSITION": ["Percent left brake", b'BRAKE LEFT POSITION', b'Position', 'Y'],
			"BRAKE_RIGHT_POSITION": ["Percent right brake", b'BRAKE RIGHT POSITION', b'Position', 'Y'],
			"BRAKE_INDICATOR": ["Brake on indication", b'BRAKE INDICATOR', b'Position', 'N'],
			"BRAKE_PARKING_POSITION": ["Parking brake on", b'BRAKE PARKING POSITION', b'Position', 'Y'],
			"BRAKE_PARKING_INDICATOR": ["Parking brake indicator", b'BRAKE PARKING INDICATOR', b'Bool', 'N'],
			"SPOILERS_ARMED": ["Auto-spoilers armed", b'SPOILERS ARMED', b'Bool', 'N'],
			"SPOILERS_HANDLE_POSITION": ["Spoiler handle position", b'SPOILERS HANDLE POSITION', b'Percent Over 100', 'Y'],
			"SPOILERS_LEFT_POSITION": ["Percent left spoiler deflected", b'SPOILERS LEFT POSITION', b'Percent Over 100', 'N'],
			"SPOILERS_RIGHT_POSITION": ["Percent right spoiler deflected", b'SPOILERS RIGHT POSITION', b'Percent Over 100', 'N'],
			"FLAPS_HANDLE_PERCENT": ["Percent flap handle extended", b'FLAPS HANDLE PERCENT', b'Percent Over 100', 'N'],
			"FLAPS_HANDLE_INDEX": ["Index of current flap position", b'FLAPS HANDLE INDEX', b'Number', 'Y'],
			"FLAPS_NUM_HANDLE_POSITIONS": ["Number of flap positions", b'FLAPS NUM HANDLE POSITIONS', b'Number', 'N'],
			"TRAILING_EDGE_FLAPS_LEFT_PERCENT": ["Percent left trailing edge flap extended", b'TRAILING EDGE FLAPS LEFT PERCENT', b'Percent Over 100', 'Y'],
			"TRAILING_EDGE_FLAPS_RIGHT_PERCENT": ["Percent right trailing edge flap extended", b'TRAILING EDGE FLAPS RIGHT PERCENT', b'Percent Over 100', 'Y'],
			"TRAILING_EDGE_FLAPS_LEFT_ANGLE": ["Angle left trailing edge flap extended. Use TRAILING EDGE FLAPS LEFT PERCENT to set a value.", b'TRAILING EDGE FLAPS LEFT ANGLE', b'Radians', 'N'],
			"TRAILING_EDGE_FLAPS_RIGHT_ANGLE": ["Angle right trailing edge flap extended. Use TRAILING EDGE FLAPS RIGHT PERCENT to set a value.", b'TRAILING EDGE FLAPS RIGHT ANGLE', b'Radians', 'N'],
			"LEADING_EDGE_FLAPS_LEFT_PERCENT": ["Percent left leading edge flap extended", b'LEADING EDGE FLAPS LEFT PERCENT', b'Percent Over 100', 'Y'],
			"LEADING_EDGE_FLAPS_RIGHT_PERCENT": ["Percent right leading edge flap extended", b'LEADING EDGE FLAPS RIGHT PERCENT', b'Percent Over 100', 'Y'],
			"LEADING_EDGE_FLAPS_LEFT_ANGLE": ["Angle left leading edge flap extended. Use LEADING EDGE FLAPS LEFT PERCENT to set a value.", b'LEADING EDGE FLAPS LEFT ANGLE', b'Radians', 'N'],
			"LEADING_EDGE_FLAPS_RIGHT_ANGLE": ["Angle right leading edge flap extended. Use LEADING EDGE FLAPS RIGHT PERCENT to set a value.", b'LEADING EDGE FLAPS RIGHT ANGLE', b'Radians', 'N'],
			"AILERON_LEFT_DEFLECTION": ["Angle deflection", b'AILERON LEFT DEFLECTION', b'Radians', 'N'],
			"AILERON_LEFT_DEFLECTION_PCT": ["Percent deflection", b'AILERON LEFT DEFLECTION PCT', b'Percent Over 100', 'N'],
			"AILERON_RIGHT_DEFLECTION": ["Angle deflection", b'AILERON RIGHT DEFLECTION', b'Radians', 'N'],
			"AILERON_RIGHT_DEFLECTION_PCT": ["Percent deflection", b'AILERON RIGHT DEFLECTION PCT', b'Percent Over 100', 'N'],
			"AILERON_AVERAGE_DEFLECTION": ["Angle deflection", b'AILERON AVERAGE DEFLECTION', b'Radians', 'N'],
			"AILERON_TRIM": ["Angle deflection", b'AILERON TRIM', b'Radians', 'N'],
			"AILERON_TRIM_PCT": ["Percent deflection", b'AILERON TRIM PCT', b'Percent Over 100', 'Y'],
			"RUDDER_DEFLECTION": ["Angle deflection", b'RUDDER DEFLECTION', b'Radians', 'N'],
			"RUDDER_DEFLECTION_PCT": ["Percent deflection", b'RUDDER DEFLECTION PCT', b'Percent Over 100', 'N'],
			"RUDDER_TRIM": ["Angle deflection", b'RUDDER TRIM', b'Radians', 'N'],
			"RUDDER_TRIM_PCT": ["Percent deflection", b'RUDDER TRIM PCT', b'Percent Over 100', 'Y'],
			"FLAPS_AVAILABLE": ["True if flaps available", b'FLAPS AVAILABLE', b'Bool', 'N'],
			"FLAP_DAMAGE_BY_SPEED": ["True if flagps are damaged by excessive speed", b'FLAP DAMAGE BY SPEED', b'Bool', 'N'],
			"FLAP_SPEED_EXCEEDED": ["True if safe speed limit for flaps exceeded", b'FLAP SPEED EXCEEDED', b'Bool', 'N'],
			"ELEVATOR_DEFLECTION": ["Angle deflection", b'ELEVATOR DEFLECTION', b'Radians', 'N'],
			"ELEVATOR_DEFLECTION_PCT": ["Percent deflection", b'ELEVATOR DEFLECTION PCT', b'Percent Over 100', 'N'],
			"ALTERNATE_STATIC_SOURCE_OPEN": ["Alternate static air source", b'ALTERNATE STATIC SOURCE OPEN', b'Bool', 'N'],
			"AILERON_TRIM_PCT": ["The trim position of the ailerons. Zero is fully retracted.", b'AILERON TRIM PCT', b'Percent over 100', 'Y'],
			"RUDDER_TRIM_PCT": ["The trim position of the rudder. Zero is no trim.", b'RUDDER TRIM PCT', b'Percent over 100', 'Y'],
			"FOLDING_WING_HANDLE_POSITION": ["True if the folding wing handle is engaged.", b'FOLDING WING HANDLE POSITION', b'Bool', 'N'],
			"FUEL_DUMP_SWITCH": ["If true the aircraft is dumping fuel at the rate set in the configuration file.", b'FUEL DUMP SWITCH', b'Bool', 'N'],
		}

	class __AircraftAutopilotData(RequestHelper):
		list = {
			"AUTOPILOT_AVAILABLE": ["Available flag", b'AUTOPILOT AVAILABLE', b'Bool', 'N'],
			"AUTOPILOT_MASTER": ["On/off flag", b'AUTOPILOT MASTER', b'Bool', 'N'],
			"AUTOPILOT_NAV_SELECTED": ["Index of Nav radio selected", b'AUTOPILOT NAV SELECTED', b'Number', 'N'],
			"AUTOPILOT_WING_LEVELER": ["Wing leveler active", b'AUTOPILOT WING LEVELER', b'Bool', 'N'],
			"AUTOPILOT_NAV1_LOCK": ["Lateral nav mode active", b'AUTOPILOT NAV1 LOCK', b'Bool', 'N'],
			"AUTOPILOT_HEADING_LOCK": ["Heading mode active", b'AUTOPILOT HEADING LOCK', b'Bool', 'N'],
			"AUTOPILOT_HEADING_LOCK_DIR": ["Selected heading", b'AUTOPILOT HEADING LOCK DIR', b'Degrees', 'N'],
			"AUTOPILOT_ALTITUDE_LOCK": ["Altitude hole active", b'AUTOPILOT ALTITUDE LOCK', b'Bool', 'N'],
			"AUTOPILOT_ALTITUDE_LOCK_VAR": ["Selected altitude", b'AUTOPILOT ALTITUDE LOCK VAR', b'Feet', 'N'],
			"AUTOPILOT_ATTITUDE_HOLD": ["Attitude hold active", b'AUTOPILOT ATTITUDE HOLD', b'Bool', 'N'],
			"AUTOPILOT_GLIDESLOPE_HOLD": ["GS hold active", b'AUTOPILOT GLIDESLOPE HOLD', b'Bool', 'N'],
			"AUTOPILOT_PITCH_HOLD_REF": ["Current reference pitch", b'AUTOPILOT PITCH HOLD REF', b'Radians', 'N'],
			"AUTOPILOT_APPROACH_HOLD": ["Approach mode active", b'AUTOPILOT APPROACH HOLD', b'Bool', 'N'],
			"AUTOPILOT_BACKCOURSE_HOLD": ["Back course mode active", b'AUTOPILOT BACKCOURSE HOLD', b'Bool', 'N'],
			"AUTOPILOT_VERTICAL_HOLD_VAR": ["Selected vertical speed", b'AUTOPILOT VERTICAL HOLD VAR', b'Feet/minute', 'N'],
			"AUTOPILOT_PITCH_HOLD": ["Set to True if the autopilot pitch hold has is engaged.", b'AUTOPILOT PITCH HOLD', b'Bool', 'N'],
			"AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE": ["Flight director active", b'AUTOPILOT FLIGHT DIRECTOR ACTIVE', b'Bool', 'N'],
			"AUTOPILOT_FLIGHT_DIRECTOR_PITCH": ["Reference pitch angle", b'AUTOPILOT FLIGHT DIRECTOR PITCH', b'Radians', 'N'],
			"AUTOPILOT_FLIGHT_DIRECTOR_BANK": ["Reference bank angle", b'AUTOPILOT FLIGHT DIRECTOR BANK', b'Radians', 'N'],
			"AUTOPILOT_AIRSPEED_HOLD": ["Airspeed hold active", b'AUTOPILOT AIRSPEED HOLD', b'Bool', 'N'],
			"AUTOPILOT_AIRSPEED_HOLD_VAR": ["Selected airspeed", b'AUTOPILOT AIRSPEED HOLD VAR', b'Knots', 'N'],
			"AUTOPILOT_MACH_HOLD": ["Mach hold active", b'AUTOPILOT MACH HOLD', b'Bool', 'N'],
			"AUTOPILOT_MACH_HOLD_VAR": ["Selected mach", b'AUTOPILOT MACH HOLD VAR', b'Number', 'N'],
			"AUTOPILOT_YAW_DAMPER": ["Yaw damper active", b'AUTOPILOT YAW DAMPER', b'Bool', 'N'],
			"AUTOPILOT_RPM_HOLD_VAR": ["Selected rpm", b'AUTOPILOT RPM HOLD VAR', b'Number', 'N'],
			"AUTOPILOT_THROTTLE_ARM": ["Autothrottle armed", b'AUTOPILOT THROTTLE ARM', b'Bool', 'N'],
			"AUTOPILOT_TAKEOFF_POWER_ACTIVE": ["Takeoff / Go Around power mode active", b'AUTOPILOT TAKEOFF POWER ACTIVE', b'Bool', 'N'],
			"AUTOTHROTTLE_ACTIVE": ["Auto-throttle active", b'AUTOTHROTTLE ACTIVE', b'Bool', 'N'],
			"AUTOPILOT_NAV1_LOCK": ["True if autopilot nav1 lock applied", b'AUTOPILOT NAV1 LOCK', b'Bool', 'N'],
			"AUTOPILOT_VERTICAL_HOLD": ["True if autopilot vertical hold applied", b'AUTOPILOT VERTICAL HOLD', b'Bool', 'N'],
			"AUTOPILOT_RPM_HOLD": ["True if autopilot rpm hold applied", b'AUTOPILOT RPM HOLD', b'Bool', 'N'],
			"AUTOPILOT_MAX_BANK": ["True if autopilot max bank applied", b'AUTOPILOT MAX BANK', b'Radians', 'N'],
			"FLY_BY_WIRE_ELAC_SWITCH": ["True if the fly by wire Elevators and Ailerons computer is on.", b'FLY BY WIRE ELAC SWITCH', b'Bool', 'N'],
			"FLY_BY_WIRE_FAC_SWITCH": ["True if the fly by wire Flight Augmentation computer is on.", b'FLY BY WIRE FAC SWITCH', b'Bool', 'N'],
			"FLY_BY_WIRE_SEC_SWITCH": ["True if the fly by wire Spoilers and Elevators computer is on.", b'FLY BY WIRE SEC SWITCH', b'Bool', 'N'],
			"FLY_BY_WIRE_ELAC_FAILED": ["True if the Elevators and Ailerons computer has failed.", b'FLY BY WIRE ELAC FAILED', b'Bool', 'N'],
			"FLY_BY_WIRE_FAC_FAILED": ["True if the Flight Augmentation computer has failed.", b'FLY BY WIRE FAC FAILED', b'Bool', 'N'],
			"FLY_BY_WIRE_SEC_FAILED": ["True if the Spoilers and Elevators computer has failed.", b'FLY BY WIRE SEC FAILED', b'Bool', 'N'],
			"AUTOPILOT_FLIGHT_LEVEL_CHANGE": ["True if autopilot FLC mode applied", b'AUTOPILOT FLIGHT LEVEL CHANGE', b'Bool', 'N'],
		}

	class __AircraftLandingGearData(RequestHelper):
		list = {
			"IS_GEAR_RETRACTABLE": ["True if gear can be retracted", b'IS GEAR RETRACTABLE', b'Bool', 'N'],
			"IS_GEAR_SKIS": ["True if landing gear is skis", b'IS GEAR SKIS', b'Bool', 'N'],
			"IS_GEAR_FLOATS": ["True if landing gear is floats", b'IS GEAR FLOATS', b'Bool', 'N'],
			"IS_GEAR_SKIDS": ["True if landing gear is skids", b'IS GEAR SKIDS', b'Bool', 'N'],
			"IS_GEAR_WHEELS": ["True if landing gear is wheels", b'IS GEAR WHEELS', b'Bool', 'N'],
			"GEAR_HANDLE_POSITION": ["True if gear handle is applied", b'GEAR HANDLE POSITION', b'Bool', 'Y'],
			"GEAR_HYDRAULIC_PRESSURE": ["Gear hydraulic pressure", b'GEAR HYDRAULIC PRESSURE', b'psf', 'N'],
			"TAILWHEEL_LOCK_ON": ["True if tailwheel lock applied", b'TAILWHEEL LOCK ON', b'Bool', 'N'],
			"GEAR_CENTER_POSITION": ["Percent center gear extended", b'GEAR CENTER POSITION', b'Percent Over 100', 'Y'],
			"GEAR_LEFT_POSITION": ["Percent left gear extended", b'GEAR LEFT POSITION', b'Percent Over 100', 'Y'],
			"GEAR_RIGHT_POSITION": ["Percent right gear extended", b'GEAR RIGHT POSITION', b'Percent Over 100', 'Y'],
			"GEAR_TAIL_POSITION": ["Percent tail gear extended", b'GEAR TAIL POSITION', b'Percent Over 100', 'N'],
			"GEAR_AUX_POSITION": ["Percent auxiliary gear extended", b'GEAR AUX POSITION', b'Percent Over 100', 'N'],
			"GEAR_POSITION:index": ["Position of landing gear:; 0 = unknown; 1 = up; 2 = down", b'GEAR POSITION:index', b'Enum', 'Y'],
			"GEAR_ANIMATION_POSITION:index": ["Percent gear animation extended", b'GEAR ANIMATION POSITION:index', b'Number', 'N'],
			"GEAR_TOTAL_PCT_EXTENDED": ["Percent total gear extended", b'GEAR TOTAL PCT EXTENDED', b'Percentage', 'N'],
			"AUTO_BRAKE_SWITCH_CB": ["Auto brake switch position", b'AUTO BRAKE SWITCH CB', b'Number', 'N'],
			"WATER_RUDDER_HANDLE_POSITION": ["Position of the water rudder handle (0 handle retracted, 100 rudder handle applied)", b'WATER RUDDER HANDLE POSITION', b'Percent Over 100', 'Y'],
			"WATER_LEFT_RUDDER_EXTENDED": ["Percent extended", b'WATER LEFT RUDDER EXTENDED', b'Percentage', 'N'],
			"WATER_RIGHT_RUDDER_EXTENDED": ["Percent extended", b'WATER RIGHT RUDDER EXTENDED', b'Percentage', 'N'],
			"GEAR_CENTER_STEER_ANGLE": ["Center wheel angle, negative to the left, positive to the right.", b'GEAR CENTER STEER ANGLE', b'Percent Over 100', 'N'],
			"GEAR_LEFT_STEER_ANGLE": ["Left wheel angle, negative to the left, positive to the right.", b'GEAR LEFT STEER ANGLE', b'Percent Over 100', 'N'],
			"GEAR_RIGHT_STEER_ANGLE": ["Right wheel angle, negative to the left, positive to the right.", b'GEAR RIGHT STEER ANGLE', b'Percent Over 100', 'N'],
			"GEAR_AUX_STEER_ANGLE": ["Aux wheel angle, negative to the left, positive to the right. The aux wheel is the fourth set of gear, sometimes used on helicopters.", b'GEAR AUX STEER ANGLE', b'Percent Over 100', 'N'],
			"GEAR_STEER_ANGLE:index": ["Alternative method of getting the steer angle. Index is; 0 = center; 1 = left; 2 = right; 3 = aux", b'GEAR STEER ANGLE:index', b'Percent Over 100', 'N'],
			"WATER_LEFT_RUDDER_STEER_ANGLE": ["Water left rudder angle, negative to the left, positive to the right.", b'WATER LEFT RUDDER STEER ANGLE', b'Percent Over 100', 'N'],
			"WATER_RIGHT_RUDDER_STEER_ANGLE": ["Water right rudder angle, negative to the left, positive to the right.", b'WATER RIGHT RUDDER STEER ANGLE', b'Percent Over 100', 'N'],
			"GEAR_CENTER_STEER_ANGLE_PCT": ["Center steer angle as a percentage", b'GEAR CENTER STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"GEAR_LEFT_STEER_ANGLE_PCT": ["Left steer angle as a percentage", b'GEAR LEFT STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"GEAR_RIGHT_STEER_ANGLE_PCT": ["Right steer angle as a percentage", b'GEAR RIGHT STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"GEAR_AUX_STEER_ANGLE_PCT": ["Aux steer angle as a percentage", b'GEAR AUX STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"GEAR_STEER_ANGLE_PCT:index": ["Alternative method of getting steer angle as a percentage. Index is; 0 = center; 1 = left; 2 = right; 3 = aux", b'GEAR STEER ANGLE PCT:index', b'Percent Over 100', 'N'],
			"WATER_LEFT_RUDDER_STEER_ANGLE_PCT": ["Water left rudder angle as a percentage", b'WATER LEFT RUDDER STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"WATER_RIGHT_RUDDER_STEER_ANGLE_PCT": ["Water right rudder as a percentage", b'WATER RIGHT RUDDER STEER ANGLE PCT', b'Percent Over 100', 'N'],
			"WHEEL_RPM:index": ["Wheel rpm. Index is; 0 = center; 1 = left; 2 = right; 3 = aux", b'WHEEL RPM:index', b'Rpm', 'N'],
			"CENTER_WHEEL_RPM": ["Center landing gear rpm", b'CENTER WHEEL RPM', b'Rpm', 'N'],
			"LEFT_WHEEL_RPM": ["Left landing gear rpm", b'LEFT WHEEL RPM', b'Rpm', 'N'],
			"RIGHT_WHEEL_RPM": ["Right landing gear rpm", b'RIGHT WHEEL RPM', b'Rpm', 'N'],
			"AUX_WHEEL_RPM": ["Rpm of fourth set of gear wheels.", b'AUX WHEEL RPM', b'Rpm', 'N'],
			"WHEEL_ROTATION_ANGLE:index": ["Wheel rotation angle. Index is; 0 = center; 1 = left; 2 = right; 3 = aux", b'WHEEL ROTATION ANGLE:index', b'Radians', 'N'],
			"CENTER_WHEEL_ROTATION_ANGLE": ["Center wheel rotation angle", b'CENTER WHEEL ROTATION ANGLE', b'Radians', 'N'],
			"LEFT_WHEEL_ROTATION_ANGLE": ["Left wheel rotation angle", b'LEFT WHEEL ROTATION ANGLE', b'Radians', 'N'],
			"RIGHT_WHEEL_ROTATION_ANGLE": ["Right wheel rotation angle", b'RIGHT WHEEL ROTATION ANGLE', b'Radians', 'N'],
			"AUX_WHEEL_ROTATION_ANGLE": ["Aux wheel rotation angle", b'AUX WHEEL ROTATION ANGLE', b'Radians', 'N'],
			"GEAR_EMERGENCY_HANDLE_POSITION": ["True if gear emergency handle applied", b'GEAR EMERGENCY HANDLE POSITION', b'Bool', 'N'],
			"GEAR_WARNING": ["One of:; 0: unknown; 1: normal; 2: amphib", b'GEAR WARNING', b'Enum', 'N'],
			"ANTISKID_BRAKES_ACTIVE": ["True if antiskid brakes active", b'ANTISKID BRAKES ACTIVE', b'Bool', 'N'],
			"RETRACT_FLOAT_SWITCH": ["True if retract float switch on", b'RETRACT FLOAT SWITCH', b'Bool', 'N'],
			"RETRACT_LEFT_FLOAT_EXTENDED": ["If aircraft has retractable floats.", b'RETRACT LEFT FLOAT EXTENDED', b'Percent', 'N'],
			"RETRACT_RIGHT_FLOAT_EXTENDED": ["If aircraft has retractable floats.", b'RETRACT RIGHT FLOAT EXTENDED', b'Percent', 'N'],
			"STEER_INPUT_CONTROL": ["Position of steering tiller", b'STEER INPUT CONTROL', b'Percent over 100', 'N'],
			"GEAR_DAMAGE_BY_SPEED": ["True if gear has been damaged by excessive speed", b'GEAR DAMAGE BY SPEED', b'Bool', 'N'],
			"GEAR_SPEED_EXCEEDED": ["True if safe speed limit for gear exceeded", b'GEAR SPEED EXCEEDED', b'Bool', 'N'],
			"NOSEWHEEL_LOCK_ON": ["True if the nosewheel lock is engaged.", b'NOSEWHEEL LOCK ON', b'Bool', 'N'],
		}

	class __AircraftEnvironmentData(RequestHelper):
		list = {
			"AMBIENT_DENSITY": ["Ambient density", b'AMBIENT DENSITY', b'Slugs per cubic feet', 'N'],
			"AMBIENT_TEMPERATURE": ["Ambient temperature", b'AMBIENT TEMPERATURE', b'Celsius', 'N'],
			"AMBIENT_PRESSURE": ["Ambient pressure", b'AMBIENT PRESSURE', b'inHg', 'N'],
			"AMBIENT_WIND_VELOCITY": ["Wind velocity", b'AMBIENT WIND VELOCITY', b'Knots', 'N'],
			"AMBIENT_WIND_DIRECTION": ["Wind direction", b'AMBIENT WIND DIRECTION', b'Degrees', 'N'],
			"AMBIENT_WIND_X": ["Wind component in East/West direction.", b'AMBIENT WIND X', b'Meters per second', 'N'],
			"AMBIENT_WIND_Y": ["Wind component in vertical direction.", b'AMBIENT WIND Y', b'Meters per second', 'N'],
			"AMBIENT_WIND_Z": ["Wind component in North/South direction.", b'AMBIENT WIND Z', b'Meters per second', 'N'],
			"STRUCT_AMBIENT_WIND": ["X (latitude), Y (vertical) and Z (longitude) components of the wind.", b'STRUCT AMBIENT WIND', b'Feet per second', 'N'],
			"AIRCRAFT_WIND_X": ["Wind component in aircraft lateral axis", b'AIRCRAFT WIND X', b'Knots', 'N'],
			"AIRCRAFT_WIND_Y": ["Wind component in aircraft vertical axis", b'AIRCRAFT WIND Y', b'Knots', 'N'],
			"AIRCRAFT_WIND_Z": ["Wind component in aircraft longitudinal axis", b'AIRCRAFT WIND Z', b'Knots', 'N'],
			"BAROMETER_PRESSURE": ["Barometric pressure", b'BAROMETER PRESSURE', b'Millibars', 'N'],
			"SEA_LEVEL_PRESSURE": ["Barometric pressure at sea level", b'SEA LEVEL PRESSURE', b'Millibars', 'N'],
			"TOTAL_AIR_TEMPERATURE": ["Total air temperature is the air temperature at the front of the aircraft where the ram pressure from the speed of the aircraft is taken into account.", b'TOTAL AIR TEMPERATURE', b'Celsius', 'N'],
			"WINDSHIELD_RAIN_EFFECT_AVAILABLE": ["Is visual effect available on this aircraft", b'WINDSHIELD RAIN EFFECT AVAILABLE', b'Bool', 'N'],
			"AMBIENT_IN_CLOUD": ["True if the aircraft is in a cloud.", b'AMBIENT IN CLOUD', b'Bool', 'N'],
			"AMBIENT_VISIBILITY": ["Ambient visibility", b'AMBIENT VISIBILITY', b'Meters', 'N'],
			"STANDARD_ATM_TEMPERATURE": ["Outside temperature on the standard ATM scale", b'STANDARD ATM TEMPERATURE', b'Rankine', 'N'],
		}

	class __HelicopterSpecificData(RequestHelper):
		list = {
			"ROTOR_BRAKE_HANDLE_POS": ["Percent actuated", b'ROTOR BRAKE HANDLE POS', b'Percent Over 100', 'N'],
			"ROTOR_BRAKE_ACTIVE": ["Active", b'ROTOR BRAKE ACTIVE', b'Bool', 'N'],
			"ROTOR_CLUTCH_SWITCH_POS": ["Switch position", b'ROTOR CLUTCH SWITCH POS', b'Bool', 'N'],
			"ROTOR_CLUTCH_ACTIVE": ["Active", b'ROTOR CLUTCH ACTIVE', b'Bool', 'N'],
			"ROTOR_TEMPERATURE": ["Main rotor transmission temperature", b'ROTOR TEMPERATURE', b'Rankine', 'N'],
			"ROTOR_CHIP_DETECTED": ["Chip detection", b'ROTOR CHIP DETECTED', b'Bool', 'N'],
			"ROTOR_GOV_SWITCH_POS": ["Switch position", b'ROTOR GOV SWITCH POS', b'Bool', 'N'],
			"ROTOR_GOV_ACTIVE": ["Active", b'ROTOR GOV ACTIVE', b'Bool', 'N'],
			"ROTOR_LATERAL_TRIM_PCT": ["Trim percent", b'ROTOR LATERAL TRIM PCT', b'Percent Over 100', 'N'],
			"ROTOR_RPM_PCT": ["Percent max rated rpm", b'ROTOR RPM PCT', b'Percent Over 100', 'N'],
			"ENG_TURBINE_TEMPERATURE": ["Turbine temperature. Applies only to Bell helicopter.", b'ENG TURBINE TEMPERATURE', b'Celsius', 'N'],
			"ENG_TORQUE_PERCENT:index": ["Torque. Returns main rotor torque for Bell helicopter, or the indexed rotor torque of other helicopters.", b'ENG TORQUE PERCENT:index', b'Percent scalar 16K (Ft/lbs * 16384)', 'N'],
			"ENG_FUEL_PRESSURE": ["Fuel pressure. Applies only to Bell helicopter.", b'ENG FUEL PRESSURE', b'PSI', 'N'],
			"ENG_ELECTRICAL_LOAD": ["Electrical load. Applies only to Bell helicopter.", b'ENG ELECTRICAL LOAD', b'Percent', 'N'],
			"ENG_TRANSMISSION_PRESSURE": ["Transmission pressure. Applies only to Bell helicopter.", b'ENG TRANSMISSION PRESSURE', b'PSI', 'N'],
			"ENG_TRANSMISSION_TEMPERATURE": ["Transmission temperature. Applies only to Bell helicopter.", b'ENG TRANSMISSION TEMPERATURE', b'Celsius', 'N'],
			"ENG_ROTOR_RPM:index": ["Rotor rpm. Returns main rotor rpm for Bell helicopter, or the indexed rotor rpm of other helicopters.", b'ENG ROTOR RPM:index', b'Percent scalar 16K (Max rpm * 16384)', 'N'],
			"COLLECTIVE_POSITION": ["The position of the helicopter's collective. 0 is fully up, 100 fully depressed.", b'COLLECTIVE POSITION', b'Percent over 100', 'N'],
		}

	class __SlingsandHoists(RequestHelper):
		list = {
			"NUM_SLING_CABLES": ["The number of sling cables (not hoists) that are configured for the aircraft. Refer to the document Notes on Aircraft Systems.", b'NUM SLING CABLES', b'Number', 'N'],
			"PAYLOAD_STATION_OBJECT:index": ["Places the named object at the payload station identified by the index (starting from 1). The string is the Container name (refer to the title property of Simulation Object Configuration Files).", b'PAYLOAD STATION OBJECT:index', b'String', 'Y- set only'],
			"PAYLOAD_STATION_NUM_SIMOBJECTS:index": ["The number of objects at the payload station (indexed from 1).", b'PAYLOAD STATION NUM SIMOBJECTS:index', b'Number', 'N'],
			"SLING_OBJECT_ATTACHED:index": ["If units are set as boolean, returns True if a sling object is attached. If units are set as a string, returns the container title of the object. There can be multiple sling positions, indexed from 1. The sling positions are set in the Aircraft Configuration File.", b'SLING OBJECT ATTACHED:index', b'Bool/String', 'N'],
			"SLING_CABLE_BROKEN:index": ["True if the cable is broken.", b'SLING CABLE BROKEN:index', b'Bool', 'N'],
			"SLING_CABLE_EXTENDED_LENGTH:index": ["The length of the cable extending from the aircraft.", b'SLING CABLE EXTENDED LENGTH:index', b'Feet', 'Y'],
			"SLING_ACTIVE_PAYLOAD_STATION:index": ["The payload station (identified by the parameter) where objects will be placed from the sling (identified by the index).", b'SLING ACTIVE PAYLOAD STATION:index', b'Number', 'Y'],
			"SLING_HOIST_PERCENT_DEPLOYED:index": ["The percentage of the full length of the sling cable deployed.", b'SLING HOIST PERCENT DEPLOYED:index', b'Percent over 100', 'N'],
			"IS_ATTACHED_TO_SLING": ["Set to true if this object is attached to a sling.", b'IS ATTACHED TO SLING', b'Bool', 'N'],
		}

	class __AircraftMiscellaneousSystemsData(RequestHelper):
		list = {
			"SMOKE_ENABLE": ["Set to True to activate the smoke system, if one is available (for example, on the Extra).", b'SMOKE ENABLE', b'Bool', 'Y'],
			"SMOKESYSTEM_AVAILABLE": ["Smoke system available", b'SMOKESYSTEM AVAILABLE', b'Bool', 'N'],
			"PITOT_HEAT": ["Pitot heat active", b'PITOT HEAT', b'Bool', 'N'],
			"FOLDING_WING_LEFT_PERCENT": ["Left folding wing position, 100 is fully folded", b'FOLDING WING LEFT PERCENT', b'Percent Over 100', 'Y'],
			"FOLDING_WING_RIGHT_PERCENT": ["Right folding wing position, 100 is fully folded", b'FOLDING WING RIGHT PERCENT', b'Percent Over 100', 'Y'],
			"CANOPY_OPEN": ["Percent primary door/exit open", b'CANOPY OPEN', b'Percent Over 100', 'Y'],
			"TAILHOOK_POSITION": ["Percent tail hook extended", b'TAILHOOK POSITION', b'Percent Over 100', 'Y'],
			"EXIT_OPEN:index": ["Percent door/exit open", b'EXIT OPEN:index', b'Percent Over 100', 'Y'],
			"STALL_HORN_AVAILABLE": ["True if stall alarm available", b'STALL HORN AVAILABLE', b'Bool', 'N'],
			"ENGINE_MIXURE_AVAILABLE": ["True if engine mixture is available for prop engines. Obsolete value as mixture is always available. Spelling error in variable name.", b'ENGINE MIXURE AVAILABLE', b'Bool', 'N'],
			"CARB_HEAT_AVAILABLE": ["True if carb heat available", b'CARB HEAT AVAILABLE', b'Bool', 'N'],
			"SPOILER_AVAILABLE": ["True if spoiler system available", b'SPOILER AVAILABLE', b'Bool', 'N'],
			"IS_TAIL_DRAGGER": ["True if the aircraft is a taildragger", b'IS TAIL DRAGGER', b'Bool', 'N'],
			"STROBES_AVAILABLE": ["True if strobe lights are available", b'STROBES AVAILABLE', b'Bool', 'N'],
			"TOE_BRAKES_AVAILABLE": ["True if toe brakes are available", b'TOE BRAKES AVAILABLE', b'Bool', 'N'],
			"PUSHBACK_STATE": ["Type of pushback :; 0 = Straight; 1 = Left; 2 = Right", b'PUSHBACK STATE', b'Enum', 'Y'],
			"ELECTRICAL_MASTER_BATTERY": ["Battery switch position", b'ELECTRICAL MASTER BATTERY', b'Bool', 'Y'],
			"ELECTRICAL_TOTAL_LOAD_AMPS": ["Total load amps", b'ELECTRICAL TOTAL LOAD AMPS', b'Amperes', 'Y'],
			"ELECTRICAL_BATTERY_LOAD": ["Battery load", b'ELECTRICAL BATTERY LOAD', b'Amperes', 'Y'],
			"ELECTRICAL_BATTERY_VOLTAGE": ["Battery voltage", b'ELECTRICAL BATTERY VOLTAGE', b'Volts', 'Y'],
			"ELECTRICAL_MAIN_BUS_VOLTAGE": ["Main bus voltage", b'ELECTRICAL MAIN BUS VOLTAGE', b'Volts', 'Y'],
			"ELECTRICAL_MAIN_BUS_AMPS": ["Main bus current", b'ELECTRICAL MAIN BUS AMPS', b'Amperes', 'Y'],
			"ELECTRICAL_AVIONICS_BUS_VOLTAGE": ["Avionics bus voltage", b'ELECTRICAL AVIONICS BUS VOLTAGE', b'Volts', 'Y'],
			"ELECTRICAL_AVIONICS_BUS_AMPS": ["Avionics bus current", b'ELECTRICAL AVIONICS BUS AMPS', b'Amperes', 'Y'],
			"ELECTRICAL_HOT_BATTERY_BUS_VOLTAGE": ["Voltage available when battery switch is turned off", b'ELECTRICAL HOT BATTERY BUS VOLTAGE', b'Volts', 'Y'],
			"ELECTRICAL_HOT_BATTERY_BUS_AMPS": ["Current available when battery switch is turned off", b'ELECTRICAL HOT BATTERY BUS AMPS', b'Amperes', 'Y'],
			"ELECTRICAL_BATTERY_BUS_VOLTAGE": ["Battery bus voltage", b'ELECTRICAL BATTERY BUS VOLTAGE', b'Volts', 'Y'],
			"ELECTRICAL_BATTERY_BUS_AMPS": ["Battery bus current", b'ELECTRICAL BATTERY BUS AMPS', b'Amperes', 'Y'],
			"ELECTRICAL_GENALT_BUS_VOLTAGE:index": ["Genalt bus voltage (takes engine index)", b'ELECTRICAL GENALT BUS VOLTAGE:index', b'Volts', 'Y'],
			"ELECTRICAL_GENALT_BUS_AMPS:index": ["Genalt bus current (takes engine index)", b'ELECTRICAL GENALT BUS AMPS:index', b'Amperes', 'Y'],
			"CIRCUIT_GENERAL_PANEL_ON": ["Is electrical power available to this circuit", b'CIRCUIT GENERAL PANEL ON', b'Bool', 'N'],
			"CIRCUIT_FLAP_MOTOR_ON": ["Is electrical power available to this circuit", b'CIRCUIT FLAP MOTOR ON', b'Bool', 'N'],
			"CIRCUIT_GEAR_MOTOR_ON": ["Is electrical power available to this circuit", b'CIRCUIT GEAR MOTOR ON', b'Bool', 'N'],
			"CIRCUIT_AUTOPILOT_ON": ["Is electrical power available to this circuit", b'CIRCUIT AUTOPILOT ON', b'Bool', 'N'],
			"CIRCUIT_AVIONICS_ON": ["Is electrical power available to this circuit", b'CIRCUIT AVIONICS ON', b'Bool', 'N'],
			"CIRCUIT_PITOT_HEAT_ON": ["Is electrical power available to this circuit", b'CIRCUIT PITOT HEAT ON', b'Bool', 'N'],
			"CIRCUIT_PROP_SYNC_ON": ["Is electrical power available to this circuit", b'CIRCUIT PROP SYNC ON', b'Bool', 'N'],
			"CIRCUIT_AUTO_FEATHER_ON": ["Is electrical power available to this circuit", b'CIRCUIT AUTO FEATHER ON', b'Bool', 'N'],
			"CIRCUIT_AUTO_BRAKES_ON": ["Is electrical power available to this circuit", b'CIRCUIT AUTO BRAKES ON', b'Bool', 'N'],
			"CIRCUIT_STANDY_VACUUM_ON": ["Is electrical power available to this circuit", b'CIRCUIT STANDY VACUUM ON', b'Bool', 'N'],
			"CIRCUIT_MARKER_BEACON_ON": ["Is electrical power available to this circuit", b'CIRCUIT MARKER BEACON ON', b'Bool', 'N'],
			"CIRCUIT_GEAR_WARNING_ON": ["Is electrical power available to this circuit", b'CIRCUIT GEAR WARNING ON', b'Bool', 'N'],
			"CIRCUIT_HYDRAULIC_PUMP_ON": ["Is electrical power available to this circuit", b'CIRCUIT HYDRAULIC PUMP ON', b'Bool', 'N'],
			"HYDRAULIC_PRESSURE:index": ["Hydraulic system pressure. Indexes start at 1.", b'HYDRAULIC PRESSURE:index', b'Pound force per square foot', 'N'],
			"HYDRAULIC_RESERVOIR_PERCENT:index": ["Hydraulic pressure changes will follow changes to this variable. Indexes start at 1.", b'HYDRAULIC RESERVOIR PERCENT:index', b'Percent Over 100', 'Y'],
			"HYDRAULIC_SYSTEM_INTEGRITY": ["Percent system functional", b'HYDRAULIC SYSTEM INTEGRITY', b'Percent Over 100', 'N'],
			"STRUCTURAL_DEICE_SWITCH": ["True if the aircraft structure deice switch is on", b'STRUCTURAL DEICE SWITCH', b'Bool', 'N'],
			"APPLY_HEAT_TO_SYSTEMS": ["Used when too close to a fire.", b'APPLY HEAT TO SYSTEMS', b'Bool', 'Y'],
			"DROPPABLE_OBJECTS_TYPE:index": ["The type of droppable object at the station number identified by the index.", b'DROPPABLE OBJECTS TYPE:index', b'String', 'Y'],
			"DROPPABLE_OBJECTS_COUNT:index": ["The number of droppable objects at the station number identified by the index.", b'DROPPABLE OBJECTS COUNT:index', b'Number', 'N'],
		}

	class __AircraftMiscellaneousData(RequestHelper):
		list = {
			"TOTAL_WEIGHT": ["Total weight of the aircraft", b'TOTAL WEIGHT', b'Pounds', 'N'],
			"MAX_GROSS_WEIGHT": ["Maximum gross weight of the aircaft", b'MAX GROSS WEIGHT', b'Pounds', 'N'],
			"EMPTY_WEIGHT": ["Empty weight of the aircraft", b'EMPTY WEIGHT', b'Pounds', 'N'],
			"IS_USER_SIM": ["Is this the user loaded aircraft", b'IS USER SIM', b'Bool', 'N'],
			"SIM_DISABLED": ["Is sim disabled", b'SIM DISABLED', b'Bool', 'Y'],
			"G_FORCE": ["Current g force", b'G FORCE', b'GForce', 'Y'],
			"ATC_HEAVY": ["Is this aircraft recognized by ATC as heavy", b'ATC HEAVY', b'Bool', 'Y'],
			"AUTO_COORDINATION": ["Is auto-coordination active", b'AUTO COORDINATION', b'Bool', 'Y'],
			"REALISM": ["General realism percent", b'REALISM', b'Number', 'Y'],
			"TRUE_AIRSPEED_SELECTED": ["True if True Airspeed has been selected", b'TRUE AIRSPEED SELECTED', b'Bool', 'Y'],
			"DESIGN_SPEED_VS0": ["Design speed at VS0", b'DESIGN SPEED VS0', b'Feet per second', 'N'],
			"DESIGN_SPEED_VS1": ["Design speed at VS1", b'DESIGN SPEED VS1', b'Feet per second', 'N'],
			"DESIGN_SPEED_VC": ["Design speed at VC", b'DESIGN SPEED VC', b'Feet per second', 'N'],
			"MIN_DRAG_VELOCITY": ["Minimum drag velocity", b'MIN DRAG VELOCITY', b'Feet per second', 'N'],
			"ESTIMATED_CRUISE_SPEED": ["Estimated cruise speed", b'ESTIMATED CRUISE SPEED', b'Feet per second', 'N'],
			"CG_PERCENT": ["Longitudinal CG position as a percent of reference chord", b'CG PERCENT', b'Percent over 100', 'N'],
			"CG_PERCENT_LATERAL": ["Lateral CG position as a percent of reference chord", b'CG PERCENT LATERAL', b'Percent over 100', 'N'],
			"IS_SLEW_ACTIVE": ["True if slew is active", b'IS SLEW ACTIVE', b'Bool', 'Y'],
			"IS_SLEW_ALLOWED": ["True if slew is enabled", b'IS SLEW ALLOWED', b'Bool', 'Y'],
			"ATC_SUGGESTED_MIN_RWY_TAKEOFF": ["Suggested minimum runway length for takeoff. Used by ATC ", b'ATC SUGGESTED MIN RWY TAKEOFF', b'Feet', 'N'],
			"ATC_SUGGESTED_MIN_RWY_LANDING": ["Suggested minimum runway length for landing. Used by ATC ", b'ATC SUGGESTED MIN RWY LANDING', b'Feet', 'N'],
			"PAYLOAD_STATION_WEIGHT:index": ["Individual payload station weight", b'PAYLOAD STATION WEIGHT:index', b'Pounds', 'Y'],
			"PAYLOAD_STATION_COUNT": ["Number of payload stations", b'PAYLOAD STATION COUNT', b'Number', 'N'],
			"USER_INPUT_ENABLED": ["Is input allowed from the user", b'USER INPUT ENABLED', b'Bool', 'Y'],
			"TYPICAL_DESCENT_RATE": ["Normal descent rate", b'TYPICAL DESCENT RATE', b'Feet per minute', 'N'],
			"VISUAL_MODEL_RADIUS": ["Model radius", b'VISUAL MODEL RADIUS', b'Meters', 'N'],
			"SIGMA_SQRT": ["Sigma sqrt", b'SIGMA SQRT', b'Number', 'N'],
			"DYNAMIC_PRESSURE": ["Dynamic pressure", b'DYNAMIC PRESSURE', b'foot pounds', 'N'],
			"TOTAL_VELOCITY": ["Velocity regardless of direction. For example, if a helicopter is ascending vertically at 100 fps, getting this variable will return 100.", b'TOTAL VELOCITY', b'Feet per second', 'N'],
			"AIRSPEED_SELECT_INDICATED_OR_TRUE": ["The airspeed, whether true or indicated airspeed has been selected.", b'AIRSPEED SELECT INDICATED OR TRUE', b'Knots', 'N'],
			"VARIOMETER_RATE": ["Variometer rate", b'VARIOMETER RATE', b'Feet per second', 'N'],
			"VARIOMETER_SWITCH": ["True if the variometer switch is on", b'VARIOMETER SWITCH', b'Bool', 'N'],
			"PRESSURE_ALTITUDE": ["Altitude reading", b'PRESSURE ALTITUDE', b'Meters', 'N'],
			"MAGNETIC_COMPASS": ["Compass reading", b'MAGNETIC COMPASS', b'Degrees', 'N'],
			"TURN_INDICATOR_RATE": ["Turn indicator reading", b'TURN INDICATOR RATE', b'Radians per second', 'N'],
			"TURN_INDICATOR_SWITCH": ["True if turn indicator switch is on", b'TURN INDICATOR SWITCH', b'Bool', 'N'],
			"YOKE_Y_INDICATOR": ["Yoke position in vertical direction", b'YOKE Y INDICATOR', b'Position', 'N'],
			"YOKE_X_INDICATOR": ["Yoke position in horizontal direction", b'YOKE X INDICATOR', b'Position', 'N'],
			"RUDDER_PEDAL_INDICATOR": ["Rudder pedal position", b'RUDDER PEDAL INDICATOR', b'Position', 'N'],
			"BRAKE_DEPENDENT_HYDRAULIC_PRESSURE": ["Brake dependent hydraulic pressure reading", b'BRAKE DEPENDENT HYDRAULIC PRESSURE', b'foot pounds', 'N'],
			"PANEL_ANTI_ICE_SWITCH": ["True if panel anti-ice switch is on", b'PANEL ANTI ICE SWITCH', b'Bool', 'N'],
			"WING_AREA": ["Total wing area", b'WING AREA', b'Square feet', 'N'],
			"WING_SPAN": ["Total wing span", b'WING SPAN', b'Feet', 'N'],
			"BETA_DOT": ["Beta dot", b'BETA DOT', b'Radians per second', 'N'],
			"LINEAR_CL_ALPHA": ["Linear CL alpha", b'LINEAR CL ALPHA', b'Per radian', 'N'],
			"STALL_ALPHA": ["Stall alpha", b'STALL ALPHA', b'Radians', 'N'],
			"ZERO_LIFT_ALPHA": ["Zero lift alpha", b'ZERO LIFT ALPHA', b'Radians', 'N'],
			"CG_AFT_LIMIT": ["Aft limit of CG", b'CG AFT LIMIT', b'Percent over 100', 'N'],
			"CG_FWD_LIMIT": ["Forward limit of CG", b'CG FWD LIMIT', b'Percent over 100', 'N'],
			"CG_MAX_MACH": ["Max mach CG", b'CG MAX MACH', b'Machs', 'N'],
			"CG_MIN_MACH": ["Min mach CG", b'CG MIN MACH', b'Machs', 'N'],
			"PAYLOAD_STATION_NAME": ["Descriptive name for payload station", b'PAYLOAD STATION NAME', b'String', 'N'],
			"ELEVON_DEFLECTION": ["Elevon deflection", b'ELEVON DEFLECTION', b'Radians', 'N'],
			"EXIT_TYPE": ["One of:; 0: Main; 1: Cargo; 2: Emergency; 3: Unknown", b'EXIT TYPE', b'Enum', 'N'],
			"EXIT_POSX": ["Position of exit relative to datum reference point", b'EXIT POSX', b'Feet', 'N'],
			"EXIT_POSY": ["Position of exit relative to datum reference point", b'EXIT POSY', b'Feet', 'N'],
			"EXIT_POSZ": ["Position of exit relative to datum reference point", b'EXIT POSZ', b'Feet', 'N'],
			"DECISION_HEIGHT": ["Design decision height", b'DECISION HEIGHT', b'Feet', 'N'],
			"DECISION_ALTITUDE_MSL": ["Design decision altitude above mean sea level", b'DECISION ALTITUDE MSL', b'Feet', 'N'],
			"EMPTY_WEIGHT_PITCH_MOI": ["Empty weight pitch moment of inertia", b'EMPTY WEIGHT PITCH MOI', b'slug feet squared', 'N'],
			"EMPTY_WEIGHT_ROLL_MOI": ["Empty weight roll moment of inertia", b'EMPTY WEIGHT ROLL MOI', b'slug feet squared', 'N'],
			"EMPTY_WEIGHT_YAW_MOI": ["Empty weight yaw moment of inertia", b'EMPTY WEIGHT YAW MOI', b'slug feet squared', 'N'],
			"EMPTY_WEIGHT_CROSS_COUPLED_MOI": ["Empty weigth cross coupled moment of inertia", b'EMPTY WEIGHT CROSS COUPLED MOI', b'slug feet squared', 'N'],
			"TOTAL_WEIGHT_PITCH_MOI": ["Total weight pitch moment of inertia", b'TOTAL WEIGHT PITCH MOI', b'slug feet squared', 'N'],
			"TOTAL_WEIGHT_ROLL_MOI": ["Total weight roll moment of inertia", b'TOTAL WEIGHT ROLL MOI', b'slug feet squared', 'N'],
			"TOTAL_WEIGHT_YAW_MOI": ["Total weight yaw moment of inertia", b'TOTAL WEIGHT YAW MOI', b'slug feet squared', 'N'],
			"TOTAL_WEIGHT_CROSS_COUPLED_MOI": ["Total weight cross coupled moment of inertia", b'TOTAL WEIGHT CROSS COUPLED MOI', b'slug feet squared', 'N'],
			"WATER_BALLAST_VALVE": ["True if water ballast valve is available", b'WATER BALLAST VALVE', b'Bool', 'N'],
			"MAX_RATED_ENGINE_RPM": ["Maximum rated rpm", b'MAX RATED ENGINE RPM', b'Rpm', 'N'],
			"FULL_THROTTLE_THRUST_TO_WEIGHT_RATIO": ["Full throttle thrust to weight ratio", b'FULL THROTTLE THRUST TO WEIGHT RATIO', b'Number', 'N'],
			"PROP_AUTO_CRUISE_ACTIVE": ["True if prop auto cruise active", b'PROP AUTO CRUISE ACTIVE', b'Bool', 'N'],
			"PROP_ROTATION_ANGLE": ["Prop rotation angle", b'PROP ROTATION ANGLE', b'Radians', 'N'],
			"PROP_BETA_MAX": ["Prop beta max", b'PROP BETA MAX', b'Radians', 'N'],
			"PROP_BETA_MIN": ["Prop beta min", b'PROP BETA MIN', b'Radians', 'N'],
			"PROP_BETA_MIN_REVERSE": ["Prop beta min reverse", b'PROP BETA MIN REVERSE', b'Radians', 'N'],
			"FUEL_SELECTED_TRANSFER_MODE": ["One of:; -1: off; 0: auto; 1: forward; 2: aft; 3: manual", b'FUEL SELECTED TRANSFER MODE', b'Enum', 'N'],
			"DROPPABLE_OBJECTS_UI_NAME": ["Descriptive name, used in User Interface dialogs, of a droppable object", b'DROPPABLE OBJECTS UI NAME', b'String', 'N'],
			"MANUAL_FUEL_PUMP_HANDLE": ["Position of manual fuel pump handle. 100 is fully deployed.", b'MANUAL FUEL PUMP HANDLE', b'Percent over 100', 'N'],
			"BLEED_AIR_SOURCE_CONTROL": ["One of:; 0: min; 1: auto; 2: off; 3: apu; 4: engines", b'BLEED AIR SOURCE CONTROL', b'Enum', 'N'],
			"ELECTRICAL_OLD_CHARGING_AMPS": ["Legacy, use ELECTRICAL BATTERY LOAD", b'ELECTRICAL OLD CHARGING AMPS', b'Amps', 'N'],
			"HYDRAULIC_SWITCH": ["True if hydraulic switch is on", b'HYDRAULIC SWITCH', b'Bool', 'N'],
			"CONCORDE_VISOR_POSITION_PERCENT": ["0 = up, 1.0 = extended/down", b'CONCORDE VISOR POSITION PERCENT', b'Percent over 100', 'N'],
			"CONCORDE_NOSE_ANGLE": ["0 = up", b'CONCORDE NOSE ANGLE', b'Radians', 'N'],
			"REALISM_CRASH_WITH_OTHERS": ["True indicates crashing with other aircraft is possible.", b'REALISM CRASH WITH OTHERS', b'Bool', 'N'],
			"REALISM_CRASH_DETECTION": ["True indicates crash detection is turned on.", b'REALISM CRASH DETECTION', b'Bool', 'N'],
			"MANUAL_INSTRUMENT_LIGHTS": ["True if instrument lights are set manually", b'MANUAL INSTRUMENT LIGHTS', b'Bool', 'N'],
			"PITOT_ICE_PCT": ["Amount of pitot ice. 100 is fully iced.", b'PITOT ICE PCT', b'Percent over 100', 'N'],
			"SEMIBODY_LOADFACTOR_Y": ["Semibody loadfactor x and z are not supported.", b'SEMIBODY LOADFACTOR Y', b'Number', 'N'],
			"SEMIBODY_LOADFACTOR_YDOT": ["Semibody loadfactory ydot", b'SEMIBODY LOADFACTOR YDOT', b'Per second', 'N'],
			"RAD_INS_SWITCH": ["True if Rad INS switch on", b'RAD INS SWITCH', b'Bool', 'N'],
			"SIMULATED_RADIUS": ["Simulated radius", b'SIMULATED RADIUS', b'Feet', 'N'],
			"STRUCTURAL_ICE_PCT": ["Amount of ice on aircraft structure. 100 is fully iced.", b'STRUCTURAL ICE PCT', b'Percent over 100', 'N'],
			"ARTIFICIAL_GROUND_ELEVATION": ["In case scenery is not loaded for AI planes, this variable can be used to set a default surface elevation.", b'ARTIFICIAL GROUND ELEVATION', b'Feet', 'N'],
			"SURFACE_INFO_VALID": ["True indicates SURFACE CONDITION is meaningful.", b'SURFACE INFO VALID', b'Bool', 'N'],
			"SURFACE_CONDITION": ["One of:; 0: Normal; 1: Wet; 2: Icy; 3: Snow", b'SURFACE CONDITION', b'Enum', 'N'],
			"PUSHBACK_ANGLE": ["Pushback angle (the heading of the tug)", b'PUSHBACK ANGLE', b'Radians', 'N'],
			"PUSHBACK_CONTACTX": ["The towpoint position, relative to the aircrafts datum reference point.", b'PUSHBACK CONTACTX', b'Feet', 'N'],
			"PUSHBACK_CONTACTY": ["Pushback contact position in vertical direction", b'PUSHBACK CONTACTY', b'Feet', 'N'],
			"PUSHBACK_CONTACTZ": ["Pushback contact position in fore/aft direction", b'PUSHBACK CONTACTZ', b'Feet', 'N'],
			"PUSHBACK_WAIT": ["True if waiting for pushback.", b'PUSHBACK WAIT', b'Bool', 'N'],
			"YAW_STRING_ANGLE": ["The yaw string angle. Yaw strings are attached to gliders as visible indicators of the yaw angle. An animation of this is not implemented in ESP.", b'YAW STRING ANGLE', b'Radians', 'N'],
			"YAW_STRING_PCT_EXTENDED": ["Yaw string angle as a percentage", b'YAW STRING PCT EXTENDED', b'Percent over 100', 'N'],
			"INDUCTOR_COMPASS_PERCENT_DEVIATION": ["Inductor compass deviation reading", b'INDUCTOR COMPASS PERCENT DEVIATION', b'Percent over 100', 'N'],
			"INDUCTOR_COMPASS_HEADING_REF": ["Inductor compass heading", b'INDUCTOR COMPASS HEADING REF', b'Radians', 'N'],
			"ANEMOMETER_PCT_RPM": ["Anemometer rpm as a percentage", b'ANEMOMETER PCT RPM', b'Percent over 100', 'N'],
			"ROTOR_ROTATION_ANGLE": ["Main rotor rotation angle (helicopters only)", b'ROTOR ROTATION ANGLE', b'Radians', 'N'],
			"DISK_PITCH_ANGLE": ["Main rotor pitch angle (helicopters only)", b'DISK PITCH ANGLE', b'Radians', 'N'],
			"DISK_BANK_ANGLE": ["Main rotor bank angle (helicopters only)", b'DISK BANK ANGLE', b'Radians', 'N'],
			"DISK_PITCH_PCT": ["Main rotor pitch percent (helicopters only)", b'DISK PITCH PCT', b'Percent over 100', 'N'],
			"DISK_BANK_PCT": ["Main rotor bank percent (helicopters only)", b'DISK BANK PCT', b'Percent over 100', 'N'],
			"DISK_CONING_PCT": ["Main rotor coning percent (helicopters only)", b'DISK CONING PCT', b'Percent over 100', 'N'],
			# "NAV_VOR_LLAF64": ["Nav VOR latitude, longitude, altitude", b'NAV VOR LLAF64', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			# "NAV_GS_LLAF64": ["Nav GS latitude, longitude, altitude", b'NAV GS LLAF64', b'SIMCONNECT_DATA_LATLONALT', 'N'],
			"STATIC_CG_TO_GROUND": ["Static CG to ground", b'STATIC CG TO GROUND', b'Feet', 'N'],
			"STATIC_PITCH": ["Static pitch", b'STATIC PITCH', b'Radians', 'N'],
			"CRASH_SEQUENCE": ["One of:; 0: off; 1: complete; 3: reset; 4: pause; 11: start", b'CRASH SEQUENCE', b'Enum', 'N'],
			"CRASH_FLAG": ["One of:; 0: None; 2: Mountain; 4: General; 6: Building; 8: Splash; 10: Gear up; 12: Overstress; 14: Building; 16: Aircraft; 18: Fuel Truck", b'CRASH FLAG', b'Enum', 'N'],
			"TOW_RELEASE_HANDLE": ["Position of tow release handle. 100 is fully deployed.", b'TOW RELEASE HANDLE', b'Percent over 100', 'N'],
			"TOW_CONNECTION": ["True if a towline is connected to both tow plane and glider.", b'TOW CONNECTION', b'Bool', 'N'],
			"APU_PCT_RPM": ["Auxiliary power unit rpm, as a percentage", b'APU PCT RPM', b'Percent over 100', 'N'],
			"APU_PCT_STARTER": ["Auxiliary power unit starter, as a percentage", b'APU PCT STARTER', b'Percent over 100', 'N'],
			"APU_VOLTS": ["Auxiliary power unit voltage", b'APU VOLTS', b'Volts', 'N'],
			"APU_GENERATOR_SWITCH": ["True if APU generator switch on", b'APU GENERATOR SWITCH', b'Bool', 'N'],
			"APU_GENERATOR_ACTIVE": ["True if APU generator active", b'APU GENERATOR ACTIVE', b'Bool', 'N'],
			"APU_ON_FIRE_DETECTED": ["True if APU on fire", b'APU ON FIRE DETECTED', b'Bool', 'N'],
			"PRESSURIZATION_CABIN_ALTITUDE": ["The current altitude of the cabin pressurization..", b'PRESSURIZATION CABIN ALTITUDE', b'Feet', 'N'],
			"PRESSURIZATION_CABIN_ALTITUDE_GOAL": ["The set altitude of the cabin pressurization.", b'PRESSURIZATION CABIN ALTITUDE GOAL', b'Feet', 'N'],
			"PRESSURIZATION_CABIN_ALTITUDE_RATE": ["The rate at which cabin pressurization changes.", b'PRESSURIZATION CABIN ALTITUDE RATE', b'Feet per second', 'N'],
			"PRESSURIZATION_PRESSURE_DIFFERENTIAL": ["The difference in pressure between the set altitude pressurization and the current pressurization.", b'PRESSURIZATION PRESSURE DIFFERENTIAL', b'foot pounds', 'N'],
			"PRESSURIZATION_DUMP_SWITCH": ["True if the cabin pressurization dump switch is on.", b'PRESSURIZATION DUMP SWITCH', b'Bool', 'N'],
			"FIRE_BOTTLE_SWITCH": ["True if the fire bottle switch is on.", b'FIRE BOTTLE SWITCH', b'Bool', 'N'],
			"FIRE_BOTTLE_DISCHARGED": ["True if the fire bottle is discharged.", b'FIRE BOTTLE DISCHARGED', b'Bool', 'N'],
			"CABIN_NO_SMOKING_ALERT_SWITCH": ["True if the No Smoking switch is on.", b'CABIN NO SMOKING ALERT SWITCH', b'Bool', 'Y'],
			"CABIN_SEATBELTS_ALERT_SWITCH": ["True if the Seatbelts switch is on.", b'CABIN SEATBELTS ALERT SWITCH', b'Bool', 'Y'],
			"GPWS_WARNING": ["True if Ground Proximity Warning System installed.", b'GPWS WARNING', b'Bool', 'N'],
			"GPWS_SYSTEM_ACTIVE": ["True if the Ground Proximity Warning System is active", b'GPWS SYSTEM ACTIVE', b'Bool', 'Y'],
			"CRASH_FLAG": ["One of:; 0: None; 2: Mountain; 4: General; 6: Building; 8: Splash; 10: Gear up; 12: Overstress; 14: Building; 16: Aircraft; 18: Fuel Truck", b'CRASH FLAG', b'Enum', 'N'],
			"IS_ALTITUDE_FREEZE_ON": ["True if the altitude of the aircraft is frozen.", b'IS ALTITUDE FREEZE ON', b'Bool', 'N'],
			"IS_ATTITUDE_FREEZE_ON": ["True if the attitude (pitch, bank and heading) of the aircraft is frozen.", b'IS ATTITUDE FREEZE ON', b'Bool', 'N'],
			# found in sdk
			"SLING_HOOK_IN_PICKUP_MODE:index": [" ", b'SLING HOOK IN PICKUP MODE:index', b'Bool', 'N'],
			"AI_TRAFFIC_STATE": [" ", b'AI TRAFFIC STATE', b'String', 'N'],
			"AI_TRAFFIC_ASSIGNED_PARKING": [" ", b'AI TRAFFIC ASSIGNED PARKING', b'String', 'N'],
			"RECIP_ENG_FUEL_TANKS_USED:index": [" ", b'RECIP ENG FUEL TANKS USED:index', b'Mask', 'Y'],
			"TURB_ENG_TANKS_USED:index": [" ", b'TURB ENG TANKS USED:index', b'Mask', 'N'],
			"ENG_TURBINE_TEMPERATURE:index": [" ", b'ENG TURBINE TEMPERATURE:index', b'Celsius', 'N'],
			"ENG_ELECTRICAL_LOAD:index": [" ", b'ENG ELECTRICAL LOAD:index', b'Percent', 'N'],
			"ENG_TRANSMISSION_PRESSURE:index": [" ", b'ENG TRANSMISSION PRESSURE:index', b'PSI', 'N'],
			"ENG_TRANSMISSION_TEMPERATURE:index": [" ", b'ENG TRANSMISSION TEMPERATURE:index', b'Celsius', 'N'],
			"SURFACE_TYPE": [" ", b'SURFACE TYPE', b'Enum', 'N'],
			"COM_STATUS:index": [" ", b'COM STATUS:index', b'Enum', 'N'],
			"NAV_TOFROM:index": [" ", b'NAV TOFROM:index', b'Enum', 'N'],
			"GPS_APPROACH_MODE": [" ", b'GPS APPROACH MODE', b'Enum', 'N'],
			"GPS_APPROACH_WP_TYPE": [" ", b'GPS APPROACH WP TYPE', b'Enum', 'N'],
			"GPS_APPROACH_SEGMENT_TYPE": [" ", b'GPS APPROACH SEGMENT TYPE', b'Enum', 'N'],
			"GPS_APPROACH_APPROACH_TYPE": [" ", b'GPS APPROACH APPROACH TYPE', b'Enum', 'N'],
			"AMBIENT_PRECIP_STATE": [" ", b'AMBIENT PRECIP STATE', b'Mask', 'N'],
			"CATEGORY": [" ", b'CATEGORY', b'String', 'N'],
			"CONCORDE_VISOR_NOSE_HANDLE": [" ", b'CONCORDE VISOR NOSE HANDLE', b'Enum', 'N'],
			"IS_LATITUDE_LONGITUDE_FREEZE_ON": [" ", b'IS LATITUDE LONGITUDE FREEZE ON', b'Bool', 'N'],
			"TIME_OF_DAY": [" ", b'TIME OF DAY', b'Enum', 'N'],
			"SIMULATION_RATE": [" ", b'SIMULATION RATE', b'Number', 'N'],
			"UNITS_OF_MEASURE": [" ", b'UNITS OF MEASURE', b'Enum', 'N'],
		}

	class __AircraftStringData(RequestHelper):
		list = {
			"ATC_TYPE": ["Type used by ATC", b'ATC TYPE', b'String', 'N'],
			"ATC_MODEL": ["Model used by ATC", b'ATC MODEL', b'String', 'N'],
			"ATC_ID": ["ID used by ATC", b'ATC ID', b'String', 'Y'],
			"ATC_AIRLINE": ["Airline used by ATC", b'ATC AIRLINE', b'String', 'Y'],
			"ATC_FLIGHT_NUMBER": ["Flight Number used by ATC", b'ATC FLIGHT NUMBER', b'String', 'Y'],
			"TITLE": ["Title from aircraft.cfg", b'TITLE', b'String', 'N'],
			"HSI_STATION_IDENT": ["Tuned station identifier", b'HSI STATION IDENT', b'String', 'N'],
			"GPS_WP_PREV_ID": ["ID of previous GPS waypoint", b'GPS WP PREV ID', b'String', 'N'],
			"GPS_WP_NEXT_ID": ["ID of next GPS waypoint", b'GPS WP NEXT ID', b'String', 'N'],
			"GPS_APPROACH_AIRPORT_ID": ["ID of airport", b'GPS APPROACH AIRPORT ID', b'String', 'N'],
			"GPS_APPROACH_APPROACH_ID": ["ID of approach", b'GPS APPROACH APPROACH ID', b'String', 'N'],
			"GPS_APPROACH_TRANSITION_ID": ["ID of approach transition", b'GPS APPROACH TRANSITION ID', b'String', 'N'],
		}

	class __AIControlledAircraft(RequestHelper):
		list = {
			"AI_DESIRED_SPEED": ["Desired speed of the AI object.", b'AI DESIRED SPEED', b'Knots', 'Y'],
			# "AI_WAYPOINT_LIST": ["List of waypoints that an AI controlled object should follow.", b'AI WAYPOINT LIST', b'SIMCONNECT_DATA_WAYPOINT', 'Y'],
			"AI_CURRENT_WAYPOINT": ["Current waypoint in the list", b'AI CURRENT WAYPOINT', b'Number', 'Y'],
			"AI_DESIRED_HEADING": ["Desired heading of the AI object.", b'AI DESIRED HEADING', b'Degrees', 'Y'],
			"AI_GROUNDTURNTIME": ["Time to make a 90 degree turn.", b'AI GROUNDTURNTIME', b'Seconds', 'Y'],
			"AI_GROUNDCRUISESPEED": ["Cruising speed.", b'AI GROUNDCRUISESPEED', b'Knots', 'Y'],
			"AI_GROUNDTURNSPEED": ["Turning speed.", b'AI GROUNDTURNSPEED', b'Knots', 'Y'],
			"AI_TRAFFIC_ISIFR": ["Request whether this aircraft is IFR or VFR See Note 1.", b'AI TRAFFIC ISIFR', b'Boolean', 'N'],
			"AI_TRAFFIC_CURRENT_AIRPORT": ["ICAO code of current airport. See Note 1.", b'AI TRAFFIC CURRENT AIRPORT', b'String', 'N'],
			"AI_TRAFFIC_ASSIGNED_RUNWAY": ["Assigned runway name (for example: \"32R\"). See Note 1.", b'AI TRAFFIC ASSIGNED RUNWAY', b'String', 'N'],
			"AI_TRAFFIC_FROMAIRPORT": ["ICAO code of the departure airport in the current schedule. See Note 2.", b'AI TRAFFIC FROMAIRPORT', b'String', 'N'],
			"AI_TRAFFIC_TOAIRPORT": ["ICAO code of the destination airport in the current schedule. See Note 2.", b'AI TRAFFIC TOAIRPORT', b'String', 'N'],
			"AI_TRAFFIC_ETD": ["Estimated time of departure for the current schedule entry, given as the number of seconds difference from the current simulation time. This can be negative if ETD is earlier than the current simulation time. See Note 2.", b'AI TRAFFIC ETD', b'Seconds', 'N'],
			"AI_TRAFFIC_ETA": ["Estimated time of arrival for the current schedule entry, given as the number of seconds difference from the current simulated time. This can be negative if ETA is earlier than the current simulated time. See Note 2.", b'AI TRAFFIC ETA', b'Seconds', 'N'],
		}

	class __CarrierOperations(RequestHelper):
		list = {
			"LAUNCHBAR_POSITION": ["Installed on aircraft before takeoff from a carrier catapult. Note that gear cannot retract with this extended. 100 = fully extended. Refer to the document Notes on Aircraft Systems.", b'LAUNCHBAR POSITION', b'Percent over 100', 'N'],
			"LAUNCHBAR_SWITCH": ["If this is set to True the launch bar switch has been engaged.", b'LAUNCHBAR SWITCH', b'Bool', 'N'],
			"LAUNCHBAR_HELD_EXTENDED": ["This will be True if the launchbar is fully extended, and can be used, for example, to change the color of an instrument light.", b'LAUNCHBAR HELD EXTENDED', b'Bool', 'N'],
			"NUMBER_OF_CATAPULTS": ["Maximum of 4. A model can contain more than 4 catapults, but only the first four will be read and recognized by the simulation.", b'NUMBER OF CATAPULTS', b'Number', 'N'],
			"CATAPULT_STROKE_POSITION:index": ["Catapults are indexed from 1. This value will be 0 before the catapult fires, and then up to 100 as the aircraft is propelled down the catapult. The aircraft may takeoff before the value reaches 100 (depending on the aircraft weight, power applied, and other factors), in which case this value will not be further updated. This value could be used to drive a bogie animation.", b'CATAPULT STROKE POSITION:index', b'Number', 'N'],
			"HOLDBACK_BAR_INSTALLED": ["Holdback bars allow build up of thrust before takeoff from a catapult, and are installed by the deck crew of an aircraft carrier.", b'HOLDBACK BAR INSTALLED', b'Bool', 'N'],
			"BLAST_SHIELD_POSITION:index": ["Indexed from 1, 100 is fully deployed, 0 flat on deck", b'BLAST SHIELD POSITION:index', b'Percent over 100', 'N'],
			"CABLE_CAUGHT_BY_TAILHOOK": ["A number 1 through 4 for the cable number caught by the tailhook. Cable 1 is the one closest to the stern of the carrier. A value of 0 indicates no cable was caught.", b'CABLE CAUGHT BY TAILHOOK', b'Number', 'N'],
			"TAILHOOK_HANDLE": ["True if the tailhook handle is engaged.", b'TAILHOOK HANDLE', b'Bool', 'N'],
			"SURFACE_RELATIVE_GROUND_SPEED": ["The speed of the aircraft relative to the speed of the first surface directly underneath it. Use this to retrieve, for example, an aircraft's taxiing speed while it is moving on a moving carrier. It also applies to airborne aircraft, for example when a helicopter is successfully hovering above a moving ship, this value should be zero. The returned value will be the same as GROUND VELOCITY if the first surface beneath it is not moving.", b'SURFACE RELATIVE GROUND SPEED', b'Feet per second', 'N'],
		}

	class __Racing(RequestHelper):
		list = {
			"RECIP_ENG_DETONATING:index": ["Indexed from 1. Set to True if the engine is detonating.", b'RECIP ENG DETONATING:index', b'Bool', 'N'],
			"RECIP_ENG_CYLINDER_HEALTH:index": ["Index high 16 bits is engine number, low 16 cylinder number, both indexed from 1.", b'RECIP ENG CYLINDER HEALTH:index', b'Percent over 100', 'N'],
			"RECIP_ENG_NUM_CYLINDERS": ["Indexed from 1. The number of engine cylinders.", b'RECIP ENG NUM CYLINDERS', b'Number', 'N'],
			"RECIP_ENG_NUM_CYLINDERS_FAILED": ["Indexed from 1. The number of cylinders that have failed.", b'RECIP ENG NUM CYLINDERS FAILED', b'Number', 'N'],
			"RECIP_ENG_ANTIDETONATION_TANK_VALVE:index": ["Indexed from 1, each engine can have one antidetonation tank. Installed on racing aircraft. Refer to the document Notes on Aircraft Systems.", b'RECIP ENG ANTIDETONATION TANK VALVE:index', b'Bool', 'Y'],
			"RECIP_ENG_ANTIDETONATION_TANK_QUANTITY:index": ["Indexed from 1. Refer to the Mission Creation documentationfor the procedure for refilling tanks.", b'RECIP ENG ANTIDETONATION TANK QUANTITY:index', b'Gallons', 'Y'],
			"RECIP_ENG_ANTIDETONATION_TANK_MAX_QUANTITY:index": ["Indexed from 1. This value set in the Aircraft Configuration File.", b'RECIP ENG ANTIDETONATION TANK MAX QUANTITY:index', b'Gallons', 'N'],
			"RECIP_ENG_NITROUS_TANK_VALVE:index": ["Indexed from 1. Each engine can have one Nitrous fuel tank installed.", b'RECIP ENG NITROUS TANK VALVE:index', b'Bool', 'Y'],
			"RECIP_ENG_NITROUS_TANK_QUANTITY:index": ["Indexed from 1. Refer to the Mission Creation documentationfor the procedure for refilling tanks.", b'RECIP ENG NITROUS TANK QUANTITY:index', b'Gallons', 'Y'],
			"RECIP_ENG_NITROUS_TANK_MAX_QUANTITY:index": ["Indexed from 1. This value set in the Aircraft Configuration File.", b'RECIP ENG NITROUS TANK MAX QUANTITY:index', b'Gallons', 'N'],
		}

	class __EnvironmentData(RequestHelper):
		list = {
			"ABSOLUTE_TIME": ["Time, as referenced from 12:00 AM January 1, 0000", b'ABSOLUTE TIME', b'Seconds', 'N'],
			"ZULU_TIME": ["Greenwich Mean Time (GMT)", b'ZULU TIME', b'Seconds', 'N'],
			"ZULU_DAY_OF_WEEK": ["GMT day of week", b'ZULU DAY OF WEEK', b'Number', 'N'],
			"ZULU_DAY_OF_MONTH": ["GMT day of month", b'ZULU DAY OF MONTH', b'Number', 'N'],
			"ZULU_MONTH_OF_YEAR": ["GMT month of year", b'ZULU MONTH OF YEAR', b'Number', 'N'],
			"ZULU_DAY_OF_YEAR": ["GMT day of year", b'ZULU DAY OF YEAR', b'Number', 'N'],
			"ZULU_YEAR": ["GMT year", b'ZULU YEAR', b'Number', 'N'],
			"LOCAL_TIME": ["Local time", b'LOCAL TIME', b'Seconds', 'N'],
			"LOCAL_DAY_OF_WEEK": ["Local day of week", b'LOCAL DAY OF WEEK', b'Number', 'N'],
			"LOCAL_DAY_OF_MONTH": ["Local day of month", b'LOCAL DAY OF MONTH', b'Number', 'N'],
			"LOCAL_MONTH_OF_YEAR": ["Local month of year", b'LOCAL MONTH OF YEAR', b'Number', 'N'],
			"LOCAL_DAY_OF_YEAR": ["Local day of year", b'LOCAL DAY OF YEAR', b'Number', 'N'],
			"LOCAL_YEAR": ["Local year", b'LOCAL YEAR', b'Number', 'N'],
			"TIME_ZONE_OFFSET": ["Local time difference from GMT", b'TIME ZONE OFFSET', b'Seconds', 'N'],
		}

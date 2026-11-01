import struct

class ForzaTelemetryPacket:
    """
    A structural parsing model for decoding the 324-byte 
    Forza Horizon 5 'Data Out' V2 (Car Dash) UDP telemetry packet.
    """
    
    # Python struct format string representing the byte layout:
    # i = 32-bit int, I = 32-bit unsigned int, f = 32-bit float, B = 8-bit unsigned byte
    # Padding syntax (e.g., 16x) skips unmapped intermediate physics/suspension registers safely.
    PACKET_FORMAT = (
        "<"        # Little Endian byte ordering alignment
        "i"        # 0   : IsRaceOn
        "I"        # 4   : TimestampMS
        "f"        # 8   : EngineMaxRpm
        "f"        # 12  : EngineIdleRpm
        "f"        # 16  : CurrentEngineRpm
        "16x"      # 20  : [Padded Out Skip] Angular/Velocity X, Y, Z vectors
        "f"        # 36  : AccelerationX (Lateral)
        "4x"       # 40  : [Padded Out Skip] AccelerationY
        "f"        # 44  : AccelerationZ (Longitudinal)
        "20x"      # 48  : [Padded Out Skip] Suspension vectors
        "ffff"     # 68  : SlipRatioFL, SlipRatioFR, SlipRatioRL, SlipRatioRR
        "120x"     # 84  : [Padded Out Skip] Wheel speeds, depth maps, position matrices
        "ffff"     # 204 : TireTempFL, TireTempFR, TireTempRL, TireTempRR
        "24x"      # 220 : [Padded Out Skip] Boost, Power, Torque registers
        "f"        # 244 : Speed (Meters per Second)
        "44x"      # 248 : [Padded Out Skip] Race loop/Lap calculation stats
        "f"        # 292 : Fuel Volume Scale (0.0 to 1.0)
        "19x"      # 296 : [Padded Out Skip] Core distance/Input metrics
        "B"        # 315 : DamageEngine (0-255)
        "2x"       # 316 : [Padded Out Skip] Steering / Shock absorber wear logs
        "B"        # 318 : DamageTransmission (0-255)
        "B"        # 319 : Gear Index (0=R, 1-8=Forward)
        "4x"       # 320 : [Padded Out Skip] Final tail-end structural buffer alignment padding
    )

    def __init__(self, raw_bytes: bytes):
        """
        Takes a raw 324-byte UDP datagram payload and unpacks it into clean instance attributes.
        """
        # Ensure packet meets length constraints before trying to parse
        if len(raw_bytes) < 324:
            raise ValueError(f"Invalid telemetry format data frame length: expected 324 bytes, got {len(raw_bytes)}")

        # Unpack the binary buffer matrix straight into a data tuple
        unpacked_data = struct.unpack(self.PACKET_FORMAT, raw_bytes[:324])

        # Assign raw mapped fields to descriptive variables
        self.is_race_on = bool(unpacked_data[0])
        self.timestamp_ms = unpacked_data[1]
        self.engine_max_rpm = unpacked_data[2]
        self.engine_idle_rpm = unpacked_data[3]
        self.current_engine_rpm = unpacked_data[4]
        
        self.accel_x = unpacked_data[5] # Raw m/s^2 lateral forces
        self.accel_z = unpacked_data[6] # Raw m/s^2 longitudinal forces
        
        self.slip_ratio_fl = unpacked_data[7]
        self.slip_ratio_fr = unpacked_data[8]
        self.slip_ratio_rl = unpacked_data[9]
        self.slip_ratio_rr = unpacked_data[10]
        
        self.tire_temp_fl = unpacked_data[11]
        self.tire_temp_fr = unpacked_data[12]
        self.tire_temp_rl = unpacked_data[13]
        self.tire_temp_rr = unpacked_data[14]
        
        self.speed_ms = unpacked_data[15] # Raw velocity metric float
        self.fuel_raw = unpacked_data[16]
        
        self.damage_engine = unpacked_data[17]
        self.damage_transmission = unpacked_data[18]
        self.gear_raw = unpacked_data[19]

    # --- ADVANCED CONVERSIONS & HELPER METHODS ---

    @property
    def speed_mph(self) -> int:
        """Converts raw velocity data from meters/second into standard MPH."""
        return int(self.speed_ms * 2.23694)

    @property
    def speed_kmh(self) -> int:
        """Converts raw velocity data from meters/second into standard km/h."""
        return int(self.speed_ms * 3.6)

    @property
    def gear_display(self) -> str:
        """Maps raw mechanical gear indexes cleanly to a text dashboard HUD character."""
        if self.gear_raw == 0:
            return "R"
        elif self.gear_raw == 9: # Some versions track neutral as 9 or 0 depending on state
            return "N"
        return str(self.gear_raw)

    @property
    def fuel_percentage(self) -> float:
        """Translates engine fuel scales from a 0.0-1.0 fraction float into a clean 0-100% reading."""
        return round(max(0.0, min(100.0, self.fuel_raw * 100.0)), 1)

    @property
    def g_force_lateral(self) -> float:
        """Translates horizontal velocity shifts from m/s² into standard Earth Gravity Units (G)."""
        return round(self.accel_x / 9.80665, 2)

    @property
    def g_force_longitudinal(self) -> float:
        """Translates forward/braking forces from m/s² into standard Earth Gravity Units (G)."""
        return round(self.accel_z / 9.80665, 2)

    def to_dict(self) -> dict:
        """Exports parsed, readable diagnostic states into a clean JSON-friendly dictionary profile."""
        return {
            "race_active": self.is_race_on,
            "rpm": int(self.current_engine_rpm),
            "max_rpm": int(self.engine_max_rpm),
            "speed": self.speed_mph,
            "gear": self.gear_display,
            "fuel": self.fuel_percentage,
            "gforce": {
                "lat": self.g_force_lateral,
                "long": self.g_force_longitudinal
            },
            "tire_temps": {
                "fl": int(self.tire_temp_fl), "fr": int(self.tire_temp_fr),
                "rl": int(self.tire_temp_rl), "rr": int(self.tire_temp_rr)
            },
            "damage": {
                "engine": round((self.damage_engine / 255.0) * 100, 1),
                "transmission": round((self.damage_transmission / 255.0) * 100, 1)
            }
        }
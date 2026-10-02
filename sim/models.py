"""
Multi-Domain Tactical Decision-Making Trainer - Simulation Models
Defines all domain entities, coordinate systems, roles, and event definitions.
"""

import time
import math
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

# User Types & Exercise Status
class UserType:
    TRAINEE = "TRAINEE"
    INSTRUCTOR = "INSTRUCTOR"

class ExerciseStatus:
    LOBBY = "LOBBY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

# Role definitions
class Role:
    INSTRUCTOR = "INSTRUCTOR"
    COMMANDER = "COMMANDER"
    PLATOON_ALPHA = "PLATOON_ALPHA"
    PLATOON_BRAVO = "PLATOON_BRAVO"
    JTAC_INTEL = "JTAC_INTEL"
    EW_CYBER = "EW_CYBER"

    ALL_TRAINEE_ROLES = [COMMANDER, PLATOON_ALPHA, PLATOON_BRAVO, JTAC_INTEL, EW_CYBER]

class DifficultyLevel:
    STANDARD = "STANDARD"       # Moderate latency, occasional dropout
    CONTESTED = "CONTESTED"     # Frequent VHF jamming, GPS spoofing active
    SEVERE = "SEVERE"           # Deep comms blackouts, cyber disruptions, decoy radar signatures

@dataclass
class ScenarioConfig:
    scenario_id: str = "broken_uplink"
    title: str = "Operation Broken Uplink"
    duration_minutes: int = 10
    max_users: int = 6
    difficulty: str = DifficultyLevel.CONTESTED
    enable_gps_spoofing: bool = True
    enable_cyber_disruptions: bool = True
    base_latency_sec: float = 1.2
    dropout_rate_pct: int = 25

@dataclass
class UserProfile:
    user_id: str
    callsign: str
    user_type: str = UserType.TRAINEE
    role: str = Role.COMMANDER
    is_ready: bool = False
    connected_at: float = field(default_factory=time.time)
    ip_address: str = "127.0.0.1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Domain types
class Domain:
    LAND = "LAND"
    AIR = "AIR"
    CYBER = "CYBER"
    EW = "EW"

# Faction alignments
class Allegiance:
    BLUE = "BLUE"       # Friendly forces
    RED = "RED"         # Hostile forces (OPFOR)
    NEUTRAL = "NEUTRAL" # Civilians / Non-combatants
    UNKNOWN = "UNKNOWN" # Suspected / Unconfirmed

# Unit categories
class UnitType:
    INFANTRY = "INFANTRY"
    ARMOR = "ARMOR"
    HQ = "HQ"
    RECON = "RECON"
    UAV = "UAV"
    CAS_AIRCRAFT = "CAS_AIRCRAFT"
    EW_JAMMER = "EW_JAMMER"
    RADAR = "RADAR"
    DECOY = "DECOY"

@dataclass
class Vector2D:
    x: float  # Normalized tactical grid X (0.0 to 1000.0 meters or km)
    y: float  # Normalized tactical grid Y (0.0 to 1000.0)

    def distance_to(self, other: "Vector2D") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def to_mgrs_mock(self) -> str:
        # Realistic MGRS string representation for tactical immersion
        easting = int(self.x * 100) % 10000
        northing = int(self.y * 100) % 10000
        return f"38T KM {easting:04d} {northing:04d}"

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(self.x, 2), "y": round(self.y, 2)}

@dataclass
class TacticalUnit:
    id: str
    name: str
    callsign: str
    allegiance: str             # Allegiance.BLUE / RED / UNKNOWN
    domain: str                 # Domain.LAND / AIR / etc
    unit_type: str              # UnitType.*
    position: Vector2D
    velocity: Vector2D = field(default_factory=lambda: Vector2D(0.0, 0.0))
    heading: float = 0.0        # Degrees 0-360
    speed: float = 0.0          # m/s
    health: float = 100.0       # 0.0 - 100.0%
    ammo: float = 100.0         # 0.0 - 100.0%
    status: str = "OPERATIONAL" # OPERATIONAL, ENGAGED, PINNED, DESTROYED
    is_active: bool = True
    assigned_role: Optional[str] = None  # Role responsible for this unit
    radar_cross_section: float = 1.0
    comms_online: bool = True
    last_report_time: float = field(default_factory=time.time)
    spoofed: bool = False       # If unit is an injected ghost/decoy
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mgrs"] = self.position.to_mgrs_mock()
        d["position"] = self.position.to_dict()
        d["velocity"] = self.velocity.to_dict()
        return d

@dataclass
class EWJammingZone:
    id: str
    name: str
    position: Vector2D
    radius: float               # Radius in grid units
    frequency_band: str         # VHF (Voice), UHF (Data/BFT), SATCOM, GPS
    power: float                # 0.0 - 1.0 jamming strength
    active: bool = True
    spoofing: bool = False      # If true, performs GPS / telemetry spoofing rather than pure denial
    spoof_offset: Vector2D = field(default_factory=lambda: Vector2D(120.0, -85.0))

    def covers(self, point: Vector2D) -> bool:
        if not self.active:
            return False
        return self.position.distance_to(point) <= self.radius

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position.to_dict(),
            "radius": round(self.radius, 1),
            "frequency_band": self.frequency_band,
            "power": round(self.power, 2),
            "active": self.active,
            "spoofing": self.spoofing,
            "spoof_offset": self.spoof_offset.to_dict()
        }

@dataclass
class CyberDisruption:
    id: str
    target_role: str            # Affected role, or 'ALL'
    subsystem: str              # 'COP' (tactical map), 'BFT', 'DRONE_FEED', 'RADIO', 'TERMINAL'
    disruption_type: str        # 'BLACKOUT', 'CORRUPTION', 'DELAY', 'FALSE_ALERT'
    severity: float             # 0.0 - 1.0
    start_time: float
    duration: float             # In seconds, or -1 for manual toggle
    active: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TacticalOrder:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    issuer_role: str = ""
    timestamp: float = field(default_factory=time.time)
    sim_time: float = 0.0
    unit_id: str = ""
    order_type: str = "MOVE"    # MOVE, ENGAGE, HOLD, SMOKE_COVER, RTB, REQUEST_CAS, REQUEST_ARTILLERY
    target_location: Optional[Vector2D] = None
    target_unit_id: Optional[str] = None
    rationale: str = ""         # Trainee decision rationale captured for AAR
    status: str = "ISSUED"      # ISSUED, IN_TRANSIT, EXECUTING, COMPLETED, INTERCEPTED
    diverted_by_jamming: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CommsMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    sender_role: str = ""
    channel: str = "TAC-1"      # TAC-1 (Command Net), TAC-2 (Fires/CAS), SQUAD-A, SQUAD-B
    timestamp: float = field(default_factory=time.time)
    sim_time: float = 0.0
    raw_content: str = ""
    perceived_content: str = "" # After degradation / distortion
    is_corrupted: bool = False
    is_dropped: bool = False
    delivery_delay: float = 0.0 # Delay in seconds
    delivered_at: Optional[float] = None
    recipients_received: List[str] = field(default_factory=list)
    msg_type: str = "SITREP"    # SITREP, CONTACT, 9-LINE, ORDER, CHATTER
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

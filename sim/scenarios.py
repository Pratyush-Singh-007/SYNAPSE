"""
Multi-Domain Tactical Decision-Making Trainer - Pre-configured Tactical Scenarios
"""

from typing import Dict, List, Any
from sim.models import (
    TacticalUnit, EWJammingZone, CyberDisruption, Vector2D,
    Role, Allegiance, UnitType, Domain
)

def create_operation_broken_uplink() -> Dict[str, Any]:
    """
    Scenario: Operation Broken Uplink
    A multi-domain combined arms assault through a contested mountain valley.
    Enemy has deployed Krasukha-style EW jamming, GPS spoofing, and cyber disruption.
    """
    units: Dict[str, TacticalUnit] = {
        # FRIENDLY BLUE FORCES
        "blue_hq": TacticalUnit(
            id="blue_hq",
            name="Alpha Coy HQ",
            callsign="WARLORD-6",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.HQ,
            position=Vector2D(150.0, 220.0),
            assigned_role=Role.COMMANDER,
            metadata={"ammo_pct": 100, "fuel_pct": 100, "doctrine": "DEFEND_FOB"}
        ),
        "blue_plt1": TacticalUnit(
            id="blue_plt1",
            name="1st Platoon (Mech)",
            callsign="IRONCLAD-1",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.ARMOR,
            position=Vector2D(310.0, 360.0),
            assigned_role=Role.PLATOON_ALPHA,
            heading=75.0,
            speed=4.0,
            metadata={"personnel": 28, "vehicles": 4, "ammo_pct": 95}
        ),
        "blue_plt2": TacticalUnit(
            id="blue_plt2",
            name="2nd Platoon (Infantry)",
            callsign="STALWART-2",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.INFANTRY,
            position=Vector2D(290.0, 680.0),
            assigned_role=Role.PLATOON_BRAVO,
            heading=85.0,
            speed=3.0,
            metadata={"personnel": 34, "vehicles": 3, "ammo_pct": 90}
        ),
        "blue_uav": TacticalUnit(
            id="blue_uav",
            name="Sentinel-1 MQ-9 UAV",
            callsign="HAWKEYE-9",
            allegiance=Allegiance.BLUE,
            domain=Domain.AIR,
            unit_type=UnitType.UAV,
            position=Vector2D(520.0, 460.0),
            assigned_role=Role.JTAC_INTEL,
            heading=120.0,
            speed=25.0,
            metadata={"altitude_ft": 14000, "sensor_mode": "FLIR_THERMAL", "fuel_hours": 6.5}
        ),
        "blue_ew": TacticalUnit(
            id="blue_ew",
            name="Tactical EW Intercept Vehicle",
            callsign="SPECTRE-4",
            allegiance=Allegiance.BLUE,
            domain=Domain.EW,
            unit_type=UnitType.RECON,
            position=Vector2D(200.0, 190.0),
            assigned_role=Role.EW_CYBER,
            metadata={"frequencies_monitored": ["VHF_PRC117", "UHF_BFT", "SATCOM_LINK"]}
        ),

        # HOSTILE RED FORCES (OPFOR)
        "red_armor": TacticalUnit(
            id="red_armor",
            name="Hostile Mechanized Company",
            callsign="VIPER-MAIN",
            allegiance=Allegiance.RED,
            domain=Domain.LAND,
            unit_type=UnitType.ARMOR,
            position=Vector2D(840.0, 420.0),
            heading=260.0,
            speed=6.0,
            metadata={"vehicles": 6, "threat_level": "CRITICAL"}
        ),
        "red_atgm": TacticalUnit(
            id="red_atgm",
            name="Concealed ATGM Ambush Team",
            callsign="GHOST-1",
            allegiance=Allegiance.RED,
            domain=Domain.LAND,
            unit_type=UnitType.INFANTRY,
            position=Vector2D(640.0, 620.0),
            heading=240.0,
            speed=0.0,
            metadata={"concealment": "HIGH_TREELINE", "weapon": "KORNET-EM"}
        ),
        "red_ew_station": TacticalUnit(
            id="red_ew_station",
            name="Enemy EW Jamming Complex (Krasukha)",
            callsign="DISRUPTOR-ALPHA",
            allegiance=Allegiance.RED,
            domain=Domain.EW,
            unit_type=UnitType.EW_JAMMER,
            position=Vector2D(760.0, 480.0),
            heading=0.0,
            speed=0.0,
            metadata={"emitter_power_kw": 250, "frequency_range": "MULTI_BAND"}
        )
    }

    # EW Jamming Zones
    jammers = [
        EWJammingZone(
            id="jam_krasukha_vhf",
            name="Sector Central VHF/Voice Jammer",
            position=Vector2D(760.0, 480.0),
            radius=320.0,
            frequency_band="VHF",
            power=0.9,
            active=False # Starts inactive, powers up at T+01:30
        ),
        EWJammingZone(
            id="jam_gps_spoofer",
            name="Valley Pass GPS Spoofing Emitter",
            position=Vector2D(580.0, 390.0),
            radius=260.0,
            frequency_band="GPS",
            power=0.85,
            active=False, # Activates at T+03:00
            spoofing=True,
            spoof_offset=Vector2D(90.0, 140.0) # Distorts apparent GPS coordinates
        )
    ]

    # Pre-programmed Scenario Injects (Can also be triggered manually by Instructor)
    injects = [
        {
            "id": "inj_01",
            "sim_time": 90.0, # T+01:30
            "type": "TOGGLE_JAMMER",
            "target_id": "jam_krasukha_vhf",
            "active": True,
            "title": "EW Suppression Wave Initiated",
            "description": "Enemy Krasukha-4 emitter powers on. High-power VHF jamming detected across central grid. Tactical voice radio net severely degraded.",
            "instructor_note": "Observe if Platoon Alpha shifts to UHF backup or relies on visual pyrotechnic signals."
        },
        {
            "id": "inj_02",
            "sim_time": 180.0, # T+03:00
            "type": "TOGGLE_JAMMER",
            "target_id": "jam_gps_spoofer",
            "active": True,
            "title": "GPS Spoofing Emitter Activated",
            "description": "Enemy deceptive EW begins transmitting false satellite timing signals. Blue force trackers inside pass begin drifting.",
            "instructor_note": "Trainees who don't verify against terrain contours will navigate directly into the ATGM ambush line."
        },
        {
            "id": "inj_03",
            "sim_time": 270.0, # T+04:30
            "type": "CYBER_ATTACK",
            "target_role": Role.COMMANDER,
            "subsystem": "BFT",
            "disruption_type": "BLACKOUT",
            "duration": 60.0,
            "title": "Cyber Breach: Command BFT Terminal Stalled",
            "description": "Malicious code injected via satellite gateway forces Commander's Common Operational Picture (COP) to freeze.",
            "instructor_note": "Tests Commander's willingness to delegate execution authority under doctrine of Mission Command."
        },
        {
            "id": "inj_04",
            "sim_time": 360.0, # T+06:00
            "type": "INJECT_GHOST_CONTACT",
            "ghost_unit": {
                "id": "ghost_decoy_tank",
                "name": "Radar False Return (Decoy Armor)",
                "callsign": "PHANTOM-ECHO",
                "allegiance": Allegiance.RED,
                "domain": Domain.LAND,
                "unit_type": UnitType.ARMOR,
                "position": {"x": 420.0, "y": 720.0},
                "heading": 310.0,
                "speed": 0.0,
                "spoofed": True,
                "metadata": {"signature": "CORNER_REFLECTOR_HEAT_SOURCE"}
            },
            "title": "Contradictory Intel: Decoy Armor Contact Injected",
            "description": "Radar false return appears in Sector South, conflicting with ground reconnaissance reports from Platoon Bravo.",
            "instructor_note": "Checks if JTAC requests CAS on a false decoy target or cross-verifies with thermal drone camera."
        }
    ]

    return {
        "id": "broken_uplink",
        "title": "Operation Broken Uplink",
        "theater": "Mountain Defile / Highway 4",
        "description": "Multi-Domain Combined Arms Assault through EW-Saturated Mountain Pass",
        "difficulty_default": "CONTESTED",
        "recommended_duration_min": 10,
        "max_users": 6,
        "map_bounds": {"min_x": 0.0, "max_x": 1000.0, "min_y": 0.0, "max_y": 1000.0},
        "initial_units": units,
        "jammers": jammers,
        "scheduled_injects": injects
    }

def create_operation_urban_aegis() -> Dict[str, Any]:
    """
    Scenario: Operation Urban Aegis
    High-density urban terrain with signal multipath, cellular tower hijacking,
    and concealed insurgent ATGM teams with low-altitude drone jamming.
    """
    units: Dict[str, TacticalUnit] = {
        "blue_hq": TacticalUnit(
            id="blue_hq",
            name="Combat Outpost Bravo",
            callsign="TITAN-BASE",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.HQ,
            position=Vector2D(180.0, 180.0),
            assigned_role=Role.COMMANDER,
            metadata={"ammo_pct": 100, "status": "FORTIFIED"}
        ),
        "blue_plt1": TacticalUnit(
            id="blue_plt1",
            name="1st Platoon (Urban Assault)",
            callsign="STRIKER-1",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.INFANTRY,
            position=Vector2D(350.0, 420.0),
            assigned_role=Role.PLATOON_ALPHA,
            heading=90.0,
            speed=3.0,
            metadata={"personnel": 32, "ammo_pct": 90}
        ),
        "blue_plt2": TacticalUnit(
            id="blue_plt2",
            name="2nd Platoon (Mechanized)",
            callsign="VANGUARD-2",
            allegiance=Allegiance.BLUE,
            domain=Domain.LAND,
            unit_type=UnitType.ARMOR,
            position=Vector2D(280.0, 620.0),
            assigned_role=Role.PLATOON_BRAVO,
            heading=60.0,
            speed=4.0,
            metadata={"personnel": 26, "ammo_pct": 95}
        ),
        "blue_uav": TacticalUnit(
            id="blue_uav",
            name="Micro-UAV Swarm Leader",
            callsign="HORNET-LEAD",
            allegiance=Allegiance.BLUE,
            domain=Domain.AIR,
            unit_type=UnitType.UAV,
            position=Vector2D(480.0, 500.0),
            assigned_role=Role.JTAC_INTEL,
            heading=180.0,
            speed=20.0,
            metadata={"altitude_ft": 4500, "mode": "URBAN_FLIR"}
        ),
        "blue_ew": TacticalUnit(
            id="blue_ew",
            name="SIGINT Mobile Direction Finder",
            callsign="VOYAGER-7",
            allegiance=Allegiance.BLUE,
            domain=Domain.EW,
            unit_type=UnitType.RECON,
            position=Vector2D(220.0, 240.0),
            assigned_role=Role.EW_CYBER,
            metadata={"frequencies": ["GSM_900", "UHF_COALITION"]}
        ),
        "red_armor": TacticalUnit(
            id="red_armor",
            name="Hostile T-72 Armor Platoon",
            callsign="RED-TIGER",
            allegiance=Allegiance.RED,
            domain=Domain.LAND,
            unit_type=UnitType.ARMOR,
            position=Vector2D(780.0, 480.0),
            heading=270.0,
            speed=5.0,
            metadata={"threat": "HIGH"}
        ),
        "red_atgm": TacticalUnit(
            id="red_atgm",
            name="Rooftop Sniper / ATGM Cell",
            callsign="SHADOW-CELL",
            allegiance=Allegiance.RED,
            domain=Domain.LAND,
            unit_type=UnitType.INFANTRY,
            position=Vector2D(590.0, 510.0),
            heading=220.0,
            speed=0.0,
            metadata={"concealment": "ROOFTOP_URBAN"}
        )
    }

    jammers = [
        EWJammingZone(
            id="jam_urban_multipath",
            name="Cellular & Tactical UHF Broad Jammer",
            position=Vector2D(650.0, 500.0),
            radius=280.0,
            frequency_band="UHF",
            power=0.8,
            active=False
        ),
        EWJammingZone(
            id="jam_gps_city",
            name="City Square GPS Deception Node",
            position=Vector2D(460.0, 460.0),
            radius=220.0,
            frequency_band="GPS",
            power=0.9,
            active=False,
            spoofing=True,
            spoof_offset=Vector2D(-120.0, 80.0)
        )
    ]

    injects = [
        {
            "id": "inj_u1",
            "sim_time": 60.0,
            "type": "TOGGLE_JAMMER",
            "target_id": "jam_urban_multipath",
            "active": True,
            "title": "Urban Canyon Comms Degradation",
            "description": "Hostile jamming array activates from high-rise antenna array. Digital BFT telemetry links severed in downtown sector."
        },
        {
            "id": "inj_u2",
            "sim_time": 150.0,
            "type": "TOGGLE_JAMMER",
            "target_id": "jam_gps_city",
            "active": True,
            "title": "City Center GPS Spoofing Active",
            "description": "Deceptive GPS signals force navigation units to show 1st Platoon 120m north into civilian residential sector."
        }
    ]

    return {
        "id": "urban_aegis",
        "title": "Operation Urban Aegis",
        "theater": "Dense Metro Complex / Sector Delta",
        "description": "High-density urban combat with commercial tower jamming and GPS urban canyon spoofing",
        "difficulty_default": "SEVERE",
        "recommended_duration_min": 12,
        "max_users": 6,
        "map_bounds": {"min_x": 0.0, "max_x": 1000.0, "min_y": 0.0, "max_y": 1000.0},
        "initial_units": units,
        "jammers": jammers,
        "scheduled_injects": injects
    }

def list_available_scenarios() -> List[Dict[str, Any]]:
    return [
        {
            "id": "broken_uplink",
            "title": "Operation Broken Uplink",
            "theater": "Mountain Defile / Highway 4",
            "description": "Combined arms mechanized advance through Krasukha EW suppression and GPS pass spoofing.",
            "recommended_duration_min": 10,
            "max_users": 6,
            "difficulty": "CONTESTED"
        },
        {
            "id": "urban_aegis",
            "title": "Operation Urban Aegis",
            "theater": "Metro Complex / Sector Delta",
            "description": "Close-quarters urban assault with severe RF multipath, cellular disruption, and civilian sensor noise.",
            "recommended_duration_min": 12,
            "max_users": 6,
            "difficulty": "SEVERE"
        }
    ]

def load_scenario_by_id(scenario_id: str = "broken_uplink") -> Dict[str, Any]:
    if scenario_id == "urban_aegis":
        return create_operation_urban_aegis()
    return create_operation_broken_uplink()

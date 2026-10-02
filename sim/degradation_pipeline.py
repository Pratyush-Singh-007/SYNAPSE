"""
Multi-Domain Tactical Decision-Making Trainer - Degradation Pipeline
Calculates signal degradation, packet latency, dropouts, telemetry spoofing,
and builds role-customized 'Perceived Truth' states from Server Ground Truth.
"""

import copy
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from sim.models import (
    TacticalUnit, EWJammingZone, CyberDisruption, CommsMessage,
    TacticalOrder, Vector2D, Role, Allegiance, UnitType
)

class DegradationPipeline:
    def __init__(self):
        # Global degradation settings (adjustable by instructor)
        self.base_latency_sec: float = 0.5
        self.packet_loss_rate: float = 0.05
        self.gps_spoofing_active: bool = False
        self.active_cyber_attacks: List[CyberDisruption] = []
        self.delayed_message_queue: List[Tuple[float, CommsMessage]] = [] # (delivery_timestamp, message)
        self.stale_unit_cache: Dict[str, Dict[str, Any]] = {} # role -> unit_id -> last_known_state
        self.ghost_contacts: List[TacticalUnit] = [] # Injected decoy radar/thermal signatures

    def add_cyber_disruption(self, disruption: CyberDisruption):
        self.active_cyber_attacks.append(disruption)

    def remove_cyber_disruption(self, disruption_id: str):
        self.active_cyber_attacks = [c for c in self.active_cyber_attacks if c.id != disruption_id]

    def add_ghost_contact(self, contact: TacticalUnit):
        contact.spoofed = True
        self.ghost_contacts.append(contact)

    def clear_ghost_contacts(self):
        self.ghost_contacts.clear()

    def calculate_rf_interference(self, pos: Vector2D, band: str, jammers: List[EWJammingZone]) -> float:
        """
        Calculates cumulative RF interference factor (0.0 to 1.0+) at a given grid position.
        """
        total_interference = 0.0
        for jammer in jammers:
            if not jammer.active:
                continue
            if jammer.frequency_band == band or jammer.frequency_band == "ALL":
                dist = jammer.position.distance_to(pos)
                if dist <= jammer.radius:
                    # Inverse square or linear falloff within radius
                    factor = 1.0 - (dist / max(1.0, jammer.radius))
                    total_interference += factor * jammer.power
        return min(1.0, total_interference)

    def is_comms_denied(self, unit_pos: Vector2D, jammers: List[EWJammingZone], role: str) -> Tuple[bool, float]:
        """
        Returns (is_denied, interference_level) for voice/data at position.
        """
        # Check active cyber disruptions targeting this role
        for cyber in self.active_cyber_attacks:
            if cyber.active and (cyber.target_role == role or cyber.target_role == "ALL"):
                if cyber.subsystem in ["RADIO", "TERMINAL"] and cyber.disruption_type == "BLACKOUT":
                    return True, 1.0

        # Check EW jamming
        interference = self.calculate_rf_interference(unit_pos, "VHF", jammers)
        interference += self.calculate_rf_interference(unit_pos, "UHF", jammers)
        interference = min(1.0, interference)

        if interference >= 0.75:
            return True, interference
        # Stochastic packet drop based on interference
        if interference > 0.2 and random.random() < interference:
            return True, interference

        return False, interference

    def degrade_text_message(self, raw_text: str, degradation_level: float) -> str:
        """
        Simulates tactical digital radio text corruption:
        Drops characters, introduces noise (*, #, ?), or replaces critical coordinates.
        """
        if degradation_level <= 0.1:
            return raw_text

        chars = list(raw_text)
        corrupted_chars = []
        noise_glyphs = ['*', '#', '?', '%', '~', '_', '§']

        for c in chars:
            if c.isspace():
                corrupted_chars.append(c)
                continue
            if random.random() < (degradation_level * 0.7):
                if random.random() < 0.6:
                    corrupted_chars.append(random.choice(noise_glyphs))
                else:
                    # Drop character entirely
                    pass
            else:
                corrupted_chars.append(c)

        result = "".join(corrupted_chars)
        if degradation_level > 0.6:
            result += " [SIGNAL DEGRADED - PARITY FAIL]"
        return result

    def process_outbound_message(
        self,
        msg: CommsMessage,
        sender_pos: Vector2D,
        jammers: List[EWJammingZone],
        current_sim_time: float
    ) -> Optional[CommsMessage]:
        """
        Applies delay, dropout, or corruption to an in-flight radio or tactical message.
        """
        denied, interference = self.is_comms_denied(sender_pos, jammers, msg.sender_role)

        # Complete blackout check
        if denied and interference >= 0.85:
            msg.is_dropped = True
            msg.perceived_content = "[TRANSMISSION BLOCKED - COMMS BLACKOUT]"
            return msg

        # Calculate latency
        added_latency = self.base_latency_sec + (interference * 6.0)
        # Check cyber delay
        for cyber in self.active_cyber_attacks:
            if cyber.active and (cyber.target_role == msg.sender_role or cyber.target_role == "ALL"):
                if cyber.disruption_type == "DELAY":
                    added_latency += cyber.severity * 10.0

        msg.delivery_delay = added_latency
        msg.delivered_at = current_sim_time + added_latency

        # Check corruption
        if interference > 0.25 or any(c.active and c.disruption_type == "CORRUPTION" for c in self.active_cyber_attacks):
            corruption_severity = max(interference, 0.4)
            msg.is_corrupted = True
            msg.perceived_content = self.degrade_text_message(msg.raw_content, corruption_severity)
        else:
            msg.perceived_content = msg.raw_content

        return msg

    def build_perceived_view_for_role(
        self,
        ground_truth_units: Dict[str, TacticalUnit],
        jammers: List[EWJammingZone],
        role: str,
        current_sim_time: float
    ) -> Dict[str, Any]:
        """
        Projects ground truth into what a specific role actually sees on their tactical terminal.
        """
        # INSTRUCTOR sees complete ground truth with no degradation
        if role == Role.INSTRUCTOR:
            units_dict = {uid: u.to_dict() for uid, u in ground_truth_units.items()}
            return {
                "role": role,
                "sim_time": current_sim_time,
                "is_ground_truth": True,
                "units": units_dict,
                "ghost_contacts": [g.to_dict() for g in self.ghost_contacts],
                "active_jammers": [j.to_dict() for j in jammers],
                "active_cyber": [c.to_dict() for c in self.active_cyber_attacks],
                "network_status": {"voice": "ONLINE", "bft": "ONLINE", "latency_ms": 25}
            }

        # Trainee roles: Apply selective visibility and degradation
        perceived_units = {}
        role_cache = self.stale_unit_cache.setdefault(role, {})

        # Check if GPS / Telemetry spoofing is active in any zone
        active_gps_spoofer = next((j for j in jammers if j.active and j.spoofing), None)
        cyber_bft_down = any(c.active and c.subsystem == "BFT" and c.disruption_type == "BLACKOUT" for c in self.active_cyber_attacks)

        for uid, unit in ground_truth_units.items():
            if not unit.is_active:
                continue

            # Check if this unit is owned/operated directly by this role
            is_own_unit = (unit.assigned_role == role)
            
            # Friendly Blue units vs Hostile Red units
            if unit.allegiance == Allegiance.BLUE:
                if is_own_unit:
                    # Immediate squad awareness is always current
                    unit_copy = copy.deepcopy(unit)
                    
                    # But GPS spoofing can deceive navigation if inside a spoofing jammer!
                    if active_gps_spoofer and active_gps_spoofer.covers(unit.position):
                        unit_copy.position.x += active_gps_spoofer.spoof_offset.x
                        unit_copy.position.y += active_gps_spoofer.spoof_offset.y
                        unit_copy.metadata["gps_spoofed"] = True
                        unit_copy.metadata["gps_accuracy"] = "DEGRADED - MGRS UNCERTAIN"

                    perceived_units[uid] = unit_copy.to_dict()
                    role_cache[uid] = {
                        "unit": unit_copy.to_dict(),
                        "last_updated_sim_time": current_sim_time
                    }
                else:
                    # Adjacent blue units: Received via BFT / Radio
                    # Calculate if link between unit and this player is jammed
                    dist_to_jam = self.calculate_rf_interference(unit.position, "UHF", jammers)
                    
                    if cyber_bft_down or dist_to_jam > 0.8:
                        # Stale position! Show last cached position with lag badge
                        if uid in role_cache:
                            cached = copy.deepcopy(role_cache[uid]["unit"])
                            stale_for = current_sim_time - role_cache[uid]["last_updated_sim_time"]
                            cached["status"] = f"COMMS LOST (Stale {int(stale_for)}s)"
                            cached["metadata"]["stale"] = True
                            cached["metadata"]["stale_seconds"] = int(stale_for)
                            perceived_units[uid] = cached
                        else:
                            # Not yet known or disappeared
                            pass
                    else:
                        # Fresh BFT update
                        unit_copy = copy.deepcopy(unit)
                        # Check GPS spoofing
                        if active_gps_spoofer and active_gps_spoofer.covers(unit.position):
                            unit_copy.position.x += active_gps_spoofer.spoof_offset.x
                            unit_copy.position.y += active_gps_spoofer.spoof_offset.y
                            unit_copy.metadata["gps_spoofed"] = True

                        perceived_units[uid] = unit_copy.to_dict()
                        role_cache[uid] = {
                            "unit": unit_copy.to_dict(),
                            "last_updated_sim_time": current_sim_time
                        }

            elif unit.allegiance == Allegiance.RED:
                # OPFOR: Only visible if within line-of-sight of a friendly unit OR drone feed
                detected = False
                detected_by_uav = False

                # JTAC role has direct UAV sensor feed
                if role == Role.JTAC_INTEL or role == Role.COMMANDER:
                    # Check if UAV is alive and operational
                    uav = next((u for u in ground_truth_units.values() if u.unit_type == UnitType.UAV and u.is_active), None)
                    if uav:
                        # Drone has 350m sensor radius
                        if uav.position.distance_to(unit.position) <= 350.0:
                            detected = True
                            detected_by_uav = True

                # Ground unit visual detection (150m radius)
                if not detected:
                    for f_uid, f_unit in ground_truth_units.items():
                        if f_unit.allegiance == Allegiance.BLUE and f_unit.position.distance_to(unit.position) <= 150.0:
                            detected = True
                            break

                if detected:
                    red_copy = copy.deepcopy(unit)
                    # If detected by UAV in a jammed zone, position is jittered/confused
                    if detected_by_uav:
                        uav_jam = self.calculate_rf_interference(red_copy.position, "UHF", jammers)
                        if uav_jam > 0.4:
                            red_copy.position.x += (random.random() - 0.5) * 40.0
                            red_copy.position.y += (random.random() - 0.5) * 40.0
                            red_copy.metadata["target_lock"] = "INTERMITTENT"

                    perceived_units[uid] = red_copy.to_dict()

        # Add Ghost Decoys (if JTAC or Commander is targeted by decoy spoofing)
        if role in [Role.COMMANDER, Role.JTAC_INTEL, Role.PLATOON_ALPHA]:
            for ghost in self.ghost_contacts:
                perceived_units[ghost.id] = ghost.to_dict()

        # Calculate network connection health for this role's terminal
        # Find player's main representative unit position
        rep_unit = next((u for u in ground_truth_units.values() if u.assigned_role == role and u.is_active), None)
        rep_pos = rep_unit.position if rep_unit else Vector2D(500.0, 500.0)
        denied, interference = self.is_comms_denied(rep_pos, jammers, role)

        voice_status = "ONLINE"
        if denied:
            voice_status = "JAMMED / OFFLINE"
        elif interference > 0.4:
            voice_status = "DEGRADED (HIGH NOISE)"

        bft_status = "ONLINE"
        if cyber_bft_down:
            bft_status = "CYBER SEVERED"
        elif interference > 0.6:
            bft_status = "INTERMITTENT"

        return {
            "role": role,
            "sim_time": current_sim_time,
            "is_ground_truth": False,
            "units": perceived_units,
            "active_jammers": [j.to_dict() for j in jammers if role == Role.EW_CYBER], # Only EW specialist sees emitter data!
            "network_status": {
                "voice": voice_status,
                "bft": bft_status,
                "interference_pct": int(interference * 100),
                "latency_ms": int(self.base_latency_sec * 1000 + (interference * 4500))
            }
        }

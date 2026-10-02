"""
Multi-Domain Tactical Decision-Making Trainer - Scenario Simulation Engine
Coordinates simulation clock, unit physics/behavior, degradation pipeline,
instructor interventions, and AAR logging.
"""

import time
import math
import copy
from typing import Dict, List, Optional, Any, Callable
from sim.models import (
    TacticalUnit, EWJammingZone, CyberDisruption, CommsMessage,
    TacticalOrder, Vector2D, Role, Allegiance, UnitType
)
from sim.models import (
    TacticalUnit, EWJammingZone, CyberDisruption, CommsMessage,
    TacticalOrder, Vector2D, Role, Allegiance, UnitType,
    ScenarioConfig, UserProfile, ExerciseStatus, DifficultyLevel, UserType
)
from sim.degradation_pipeline import DegradationPipeline
from sim.aar_engine import AAREngine
from sim.scenarios import load_scenario_by_id, list_available_scenarios

class ScenarioEngine:
    def __init__(self, aar_engine: Optional[AAREngine] = None):
        self.aar_engine = aar_engine or AAREngine()
        self.degradation = DegradationPipeline()
        
        self.status: str = ExerciseStatus.LOBBY
        self.config: ScenarioConfig = ScenarioConfig()
        self.participants: Dict[str, UserProfile] = {}

        self.sim_time: float = 0.0
        self.is_paused: bool = False
        self.time_scale: float = 1.0
        self.last_tick_wall_time: float = time.time()

        self.units: Dict[str, TacticalUnit] = {}
        self.jammers: List[EWJammingZone] = []
        self.scheduled_injects: List[Dict[str, Any]] = []
        self.executed_inject_ids: set = set()

        self.orders: List[TacticalOrder] = []
        self.messages: List[CommsMessage] = []
        self.active_players: Dict[str, Dict[str, Any]] = {} # role -> {connection_id, last_seen}

        # Load initial scenario
        self.load_scenario("broken_uplink")

    def load_scenario(self, scenario_id: str):
        preset = load_scenario_by_id(scenario_id)
        self.scenario_id = preset.get("id", "broken_uplink")
        self.scenario_title = preset["title"]
        self.scenario_theater = preset.get("theater", "Contested Theater")
        self.scenario_description = preset.get("description", "Multi-Domain Tactical Scenario")
        self.units = copy.deepcopy(preset["initial_units"])
        self.jammers = copy.deepcopy(preset["jammers"])
        self.scheduled_injects = copy.deepcopy(preset["scheduled_injects"])
        self.executed_inject_ids.clear()
        self.sim_time = 0.0
        self.orders.clear()
        self.messages.clear()
        self.degradation = DegradationPipeline()

        self.config.scenario_id = self.scenario_id
        self.config.title = self.scenario_title
        self.apply_difficulty_settings()

        if hasattr(self, "aar_engine") and self.aar_engine is not None:
            self.aar_engine.scenario_title = self.scenario_title
            self.aar_engine.events.clear()
        else:
            self.aar_engine = AAREngine(self.scenario_title)

    def apply_difficulty_settings(self):
        diff = self.config.difficulty
        if diff == DifficultyLevel.STANDARD:
            self.degradation.base_latency_sec = 0.3
            self.degradation.packet_loss_rate = 0.08
            for j in self.jammers:
                if j.spoofing:
                    j.active = False
        elif diff == DifficultyLevel.CONTESTED:
            self.degradation.base_latency_sec = 1.2
            self.degradation.packet_loss_rate = 0.25
        elif diff == DifficultyLevel.SEVERE:
            self.degradation.base_latency_sec = 2.8
            self.degradation.packet_loss_rate = 0.50

    def update_config(self, new_config: Dict[str, Any]):
        if "scenario_id" in new_config and new_config["scenario_id"] != self.config.scenario_id:
            self.load_scenario(new_config["scenario_id"])
        
        if "duration_minutes" in new_config:
            self.config.duration_minutes = int(new_config["duration_minutes"])
        if "difficulty" in new_config:
            self.config.difficulty = new_config["difficulty"]
            self.apply_difficulty_settings()
        if "max_users" in new_config:
            self.config.max_users = int(new_config["max_users"])

    def join_user(self, user_id: str, callsign: str, user_type: str = UserType.TRAINEE, role: str = Role.COMMANDER) -> UserProfile:
        user = UserProfile(
            user_id=user_id,
            callsign=callsign,
            user_type=user_type,
            role=role,
            is_ready=False
        )
        self.participants[user_id] = user
        self.register_player(role, user_id)
        return user

    def remove_user(self, user_id: str):
        if user_id in self.participants:
            del self.participants[user_id]

    def toggle_user_ready(self, user_id: str) -> bool:
        if user_id in self.participants:
            self.participants[user_id].is_ready = not self.participants[user_id].is_ready
            return self.participants[user_id].is_ready
        return False

    def start_exercise(self):
        self.status = ExerciseStatus.RUNNING
        self.sim_time = 0.0
        self.aar_engine.record_event(
            event_type="EXERCISE_STARTED",
            sim_time=0.0,
            actor="INSTRUCTOR",
            title=f"Exercise Commenced: {self.scenario_title}",
            description=f"Status: ACTIVE // Duration: {self.config.duration_minutes}m // Difficulty: {self.config.difficulty}"
        )

    def complete_exercise(self):
        self.status = ExerciseStatus.COMPLETED
        self.aar_engine.record_event(
            event_type="EXERCISE_COMPLETED",
            sim_time=self.sim_time,
            actor="SYSTEM",
            title="Exercise Terminated // Ready for AAR",
            description="Exercise duration reached or called by EXCON. Transitioning to debriefing phase."
        )

    def register_player(self, role: str, player_id: str):
        self.active_players[role] = {
            "player_id": player_id,
            "connected_at": time.time(),
            "last_active": time.time()
        }
        self.aar_engine.record_event(
            event_type="ROLE_ASSUMED",
            sim_time=self.sim_time,
            actor=role,
            title=f"Commander Assumed Role: {role}",
            description=f"Tactical terminal online for operational station {role}."
        )

    def unregister_player(self, role: str, player_id: Optional[str] = None):
        if role in self.active_players:
            if player_id is None or self.active_players[role].get("player_id") == player_id:
                del self.active_players[role]

    def inject_contradictory_intel(self, channel: str = "TAC-1", custom_text: str = ""):
        """
        Injects deliberate contradictory sitrep / intelligence reports
        to test trainee decision-making under conflicting information.
        """
        import random
        presets = [
            ("VIPER-OVERWATCH", "URGENT SITREP: Visual observation confirms enemy armor company in full retreat eastward through defile! Highway 4 is CLEAR!"),
            ("HAWKEYE-9 (UAV)", "SENSOR DISCREPANCY: FLIR shows 4 heavy armor signatures advancing rapidly toward Sector West defile. Disregard retreat sitreps!"),
            ("STALWART-2 (OP)", "OBSERVATION POST SITREP: Heavy dust clouds North, enemy appears to be deploying decoy thermal radar corner reflectors in Grid 38T KM 4400 6200."),
            ("SIGINT-LEAD", "INTERCEPT WARNING: Enemy Krasukha jamming station active on 45 MHz. Deceptive voice intrusions detected on Tac-Net!")
        ]
        sender, text = random.choice(presets)
        if custom_text:
            text = custom_text

        msg = CommsMessage(
            id=f"MSG-{len(self.messages) + 1:04d}",
            channel=channel,
            sender_role=sender,
            msg_type="CONTRADICTORY_SITREP",
            raw_content=text,
            perceived_content=text,
            sim_time=self.sim_time,
            delivered_at=self.sim_time,
            metadata={"callsign": sender}
        )
        self.messages.append(msg)
        self.aar_engine.record_event(
            event_type="CONTRADICTORY_INTEL_INJECTED",
            sim_time=self.sim_time,
            actor="INSTRUCTOR",
            title=f"Contradictory Intel Feed [{sender}]",
            description=f'Deliberate conflicting report injected: "{text}"',
            severity="WARNING"
        )

    def issue_order(self, role: str, unit_id: str, order_type: str, target: Optional[Vector2D], rationale: str = "") -> TacticalOrder:
        order = TacticalOrder(
            issuer_role=role,
            sim_time=self.sim_time,
            unit_id=unit_id,
            order_type=order_type,
            target_location=target,
            rationale=rationale
        )
        self.orders.append(order)

        # Check if unit exists
        unit = self.units.get(unit_id)
        divergence = 0.0
        if unit and target:
            # Check if this order was issued based on spoofed coordinates
            active_spoofer = next((j for j in self.jammers if j.active and j.spoofing), None)
            if active_spoofer and active_spoofer.covers(unit.position):
                divergence = math.sqrt(active_spoofer.spoof_offset.x**2 + active_spoofer.spoof_offset.y**2)

            # Assign movement toward target
            dx = target.x - unit.position.x
            dy = target.y - unit.position.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 1.0:
                speed = 5.0 if unit.unit_type in [UnitType.ARMOR, UnitType.RECON] else 2.5
                unit.velocity = Vector2D((dx / dist) * speed, (dy / dist) * speed)
                unit.heading = math.degrees(math.atan2(dy, dx))
                unit.metadata["target_destination"] = {"x": target.x, "y": target.y}

        # Log event in AAR
        severity = "WARNING" if divergence > 50.0 else "INFO"
        self.aar_engine.record_event(
            event_type="ORDER_ISSUED",
            sim_time=self.sim_time,
            actor=role,
            title=f"{order_type} Order Issued to {unit.callsign if unit else unit_id}",
            description=f"Target: {target.to_mgrs_mock() if target else 'N/A'}. Divergence: {int(divergence)}m.",
            severity=severity,
            rationale=rationale,
            divergence=divergence
        )
        return order

    def transmit_message(self, sender_role: str, channel: str, content: str, msg_type: str = "SITREP") -> CommsMessage:
        # Determine sender location
        sender_unit = next((u for u in self.units.values() if u.assigned_role == sender_role and u.is_active), None)
        sender_pos = sender_unit.position if sender_unit else Vector2D(500.0, 500.0)

        msg = CommsMessage(
            sender_role=sender_role,
            channel=channel,
            sim_time=self.sim_time,
            raw_content=content,
            msg_type=msg_type
        )

        # Process through degradation pipeline
        processed_msg = self.degradation.process_outbound_message(msg, sender_pos, self.jammers, self.sim_time)
        self.messages.append(processed_msg)

        # AAR logging
        if processed_msg.is_dropped:
            self.aar_engine.record_event(
                event_type="COMMS_DROPPED",
                sim_time=self.sim_time,
                actor=sender_role,
                title=f"Radio Transmission Blocked on {channel}",
                description=f"Original Message: '{content[:40]}...'. Lost due to EW jamming.",
                severity="WARNING"
            )
        else:
            self.aar_engine.record_event(
                event_type="COMMS_SENT",
                sim_time=self.sim_time,
                actor=sender_role,
                title=f"Transmission on {channel} (Delay: {processed_msg.delivery_delay:.1f}s)",
                description=f"Delivered: '{processed_msg.perceived_content}'"
            )

        return processed_msg

    # INSTRUCTOR ACTIONS
    def trigger_inject_by_id(self, inject_id: str):
        inject = next((i for i in self.scheduled_injects if i["id"] == inject_id), None)
        if not inject:
            return

        self._execute_inject(inject)
        self.executed_inject_ids.add(inject_id)

    def toggle_jammer(self, jammer_id: str, active: Optional[bool] = None) -> Optional[EWJammingZone]:
        jammer = next((j for j in self.jammers if j.id == jammer_id), None)
        if jammer:
            jammer.active = not jammer.active if active is None else active
            self.aar_engine.record_event(
                event_type="JAMMER_TOGGLED",
                sim_time=self.sim_time,
                actor=Role.INSTRUCTOR,
                title=f"EW Emitter {jammer.name} {'ACTIVATED' if jammer.active else 'DEACTIVATED'}",
                description=f"Frequency: {jammer.frequency_band}, Power: {int(jammer.power*100)}%, Radius: {jammer.radius}m",
                severity="WARNING" if jammer.active else "INFO"
            )
        return jammer

    def update_jammer_position(self, jammer_id: str, new_x: float, new_y: float):
        jammer = next((j for j in self.jammers if j.id == jammer_id), None)
        if jammer:
            jammer.position = Vector2D(new_x, new_y)

    def trigger_cyber_attack(self, target_role: str, subsystem: str, disruption_type: str, duration: float = 60.0):
        cyber = CyberDisruption(
            id=f"cyber_{int(time.time()*1000)%10000}",
            target_role=target_role,
            subsystem=subsystem,
            disruption_type=disruption_type,
            severity=1.0,
            start_time=self.sim_time,
            duration=duration,
            description=f"Hostile cyber payload triggered against {target_role} ({subsystem})"
        )
        self.degradation.add_cyber_disruption(cyber)
        self.aar_engine.record_event(
            event_type="CYBER_ATTACK_LAUNCHED",
            sim_time=self.sim_time,
            actor=Role.INSTRUCTOR,
            title=f"Cyber Exploit Executed: {subsystem} on {target_role}",
            description=f"Type: {disruption_type}, Duration: {duration}s.",
            severity="CRITICAL"
        )

    def _execute_inject(self, inject: Dict[str, Any]):
        inj_type = inject["type"]
        if inj_type == "TOGGLE_JAMMER":
            self.toggle_jammer(inject["target_id"], inject.get("active", True))
        elif inj_type == "CYBER_ATTACK":
            self.trigger_cyber_attack(
                target_role=inject["target_role"],
                subsystem=inject["subsystem"],
                disruption_type=inject["disruption_type"],
                duration=inject.get("duration", 60.0)
            )
        elif inj_type == "INJECT_GHOST_CONTACT":
            ghost_dict = inject["ghost_unit"]
            ghost = TacticalUnit(
                id=ghost_dict["id"],
                name=ghost_dict["name"],
                callsign=ghost_dict["callsign"],
                allegiance=ghost_dict["allegiance"],
                domain=ghost_dict["domain"],
                unit_type=ghost_dict["unit_type"],
                position=Vector2D(ghost_dict["position"]["x"], ghost_dict["position"]["y"]),
                heading=ghost_dict.get("heading", 0.0),
                speed=ghost_dict.get("speed", 0.0),
                spoofed=True,
                metadata=ghost_dict.get("metadata", {})
            )
            self.degradation.add_ghost_contact(ghost)

        self.aar_engine.record_event(
            event_type="INJECT_TRIGGERED",
            sim_time=self.sim_time,
            actor="EXCON_SCRIPT",
            title=inject["title"],
            description=inject["description"],
            severity="WARNING"
        )

    def tick(self, dt: float):
        """
        Main simulation step. dt is real wall-clock delta seconds.
        """
        if self.is_paused:
            return

        sim_dt = dt * self.time_scale
        self.sim_time += sim_dt

        # Check scheduled injects
        for inject in self.scheduled_injects:
            if inject["id"] not in self.executed_inject_ids:
                if self.sim_time >= inject["sim_time"]:
                    self._execute_inject(inject)
                    self.executed_inject_ids.add(inject["id"])

        # Update cyber attacks expiration
        active_cybers = []
        for c in self.degradation.active_cyber_attacks:
            if c.duration > 0 and (self.sim_time - c.start_time) >= c.duration:
                # Expired
                self.aar_engine.record_event(
                    event_type="CYBER_RESTORED",
                    sim_time=self.sim_time,
                    actor="SYSTEM",
                    title=f"Cyber Countermeasures Restored {c.subsystem}",
                    description=f"Systems restored on {c.target_role} terminal."
                )
            else:
                active_cybers.append(c)
        self.degradation.active_cyber_attacks = active_cybers

        # Update unit positions
        for uid, unit in self.units.items():
            if not unit.is_active:
                continue

            # Update position based on velocity
            if unit.velocity.x != 0.0 or unit.velocity.y != 0.0:
                unit.position.x += unit.velocity.x * sim_dt
                unit.position.y += unit.velocity.y * sim_dt

                # Check if reached destination
                dest = unit.metadata.get("target_destination")
                if dest:
                    d_pos = Vector2D(dest["x"], dest["y"])
                    if unit.position.distance_to(d_pos) < 5.0:
                        unit.velocity = Vector2D(0.0, 0.0)
                        unit.metadata.pop("target_destination", None)

            # Circular loiter pattern for UAV
            if unit.unit_type == UnitType.UAV and unit.assigned_role == Role.JTAC_INTEL:
                unit.heading = (unit.heading + 8.0 * sim_dt) % 360.0
                rad = math.radians(unit.heading)
                orbit_center = Vector2D(520.0, 460.0)
                orbit_radius = 120.0
                unit.position.x = orbit_center.x + math.cos(rad) * orbit_radius
                unit.position.y = orbit_center.y + math.sin(rad) * orbit_radius

            # Hostile armor advance toward Blue lines
            if uid == "red_armor" and unit.is_active:
                if unit.position.x > 380.0:
                    unit.position.x -= 2.0 * sim_dt # Slow methodical advance

        # Check line of sight engagements
        self._check_combat_engagements(sim_dt)

    def _check_combat_engagements(self, sim_dt: float):
        red_armor = self.units.get("red_armor")
        blue_plt1 = self.units.get("blue_plt1")

        if red_armor and blue_plt1 and red_armor.is_active and blue_plt1.is_active:
            dist = red_armor.position.distance_to(blue_plt1.position)
            if dist < 180.0:
                # Direct fire engagement!
                blue_plt1.status = "ENGAGED"
                red_armor.status = "ENGAGED"

                # If Platoon 1 is in a jammed zone and cannot reach HQ, casualty rate increases
                denied, _ = self.degradation.is_comms_denied(blue_plt1.position, self.jammers, Role.PLATOON_ALPHA)
                damage_rate = 1.8 if denied else 0.8
                blue_plt1.health = max(0.0, blue_plt1.health - (damage_rate * sim_dt))

                if blue_plt1.health <= 0.0 and blue_plt1.is_active:
                    blue_plt1.is_active = False
                    blue_plt1.status = "DESTROYED / COMBAT INEFFECTIVE"
                    self.aar_engine.record_event(
                        event_type="UNIT_CASUALTY",
                        sim_time=self.sim_time,
                        actor="OPFOR",
                        title="1st Platoon Overrun / Combat Ineffective",
                        description="Blue Platoon Alpha suffered catastrophic casualties while radio comms were severed.",
                        severity="CRITICAL"
                    )

        # Check exercise duration expiration
        max_duration_sec = self.config.duration_minutes * 60.0
        if self.status == ExerciseStatus.RUNNING and self.sim_time >= max_duration_sec:
            self.complete_exercise()

    def get_role_state(self, role: str) -> Dict[str, Any]:
        """
        Returns the customized state dictionary for the specified role.
        """
        state = self.degradation.build_perceived_view_for_role(
            self.units,
            self.jammers,
            role,
            self.sim_time
        )
        state["scenario_id"] = self.config.scenario_id
        state["scenario_title"] = self.scenario_title
        state["scenario_theater"] = getattr(self, "scenario_theater", "Contested Operational Area")
        state["scenario_description"] = getattr(self, "scenario_description", "Multi-Domain Tactical Scenario")
        state["exercise_status"] = self.status
        state["sim_paused"] = self.is_paused
        state["time_scale"] = self.time_scale
        state["time_remaining_sec"] = max(0.0, (self.config.duration_minutes * 60.0) - self.sim_time)
        state["active_players"] = list(self.active_players.keys())
        state["participants"] = [p.to_dict() for p in self.participants.values()]
        state["config"] = {
            "scenario_id": self.config.scenario_id,
            "title": self.config.title,
            "duration_minutes": self.config.duration_minutes,
            "max_users": self.config.max_users,
            "difficulty": self.config.difficulty
        }
        state["available_scenarios"] = list_available_scenarios()

        # Include recent messages delivered to this role
        recent_msgs = []
        for m in self.messages[-30:]:
            # If message was delivered prior to or at current sim time
            if m.delivered_at and m.delivered_at <= self.sim_time:
                recent_msgs.append(m.to_dict())
            elif role == Role.INSTRUCTOR:
                # Instructor sees all messages including delayed/dropped ones
                recent_msgs.append(m.to_dict())

        state["messages"] = recent_msgs
        state["orders"] = [o.to_dict() for o in self.orders[-20:]]

        # For Instructor: Attach complete ground truth vs perceived delta summary
        if role == Role.INSTRUCTOR:
            state["scheduled_injects"] = self.scheduled_injects
            state["executed_inject_ids"] = list(self.executed_inject_ids)
            state["aar_metrics"] = self.aar_engine.compute_metrics()

        return state


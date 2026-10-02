"""
Unit and Integration Tests for Scenario Simulation & Degradation Engine
"""

import unittest
from sim.models import Role, Vector2D, UnitType, Allegiance
from sim.scenario_engine import ScenarioEngine
from sim.aar_engine import AAREngine

class TestTacticalTrainer(unittest.TestCase):
    def setUp(self):
        self.aar = AAREngine("Test Operation")
        self.sim = ScenarioEngine(self.aar)

    def test_initial_state(self):
        self.assertIn("blue_hq", self.sim.units)
        self.assertIn("red_armor", self.sim.units)
        self.assertEqual(len(self.sim.jammers), 2)

    def test_role_filtering(self):
        # Instructor sees all units (Ground Truth)
        instructor_view = self.sim.get_role_state(Role.INSTRUCTOR)
        self.assertTrue(instructor_view["is_ground_truth"])
        self.assertIn("red_armor", instructor_view["units"])

        # Commander initial view: OPFOR red_armor is initially hidden outside direct sight
        # or detected only if within sensor range
        cmd_view = self.sim.get_role_state(Role.COMMANDER)
        self.assertFalse(cmd_view["is_ground_truth"])
        self.assertIn("blue_hq", cmd_view["units"])

    def test_ew_jamming_degradation(self):
        # Activate Krasukha jammer
        jammer = self.sim.toggle_jammer("jam_krasukha_vhf", active=True)
        self.assertTrue(jammer.active)

        # Transmit message inside jamming zone
        msg = self.sim.transmit_message(
            sender_role=Role.PLATOON_ALPHA,
            channel="TAC-1",
            content="GRID 4501 8812 HOSTILE CONTACT ARMORED VEHICLES ADVANCING"
        )
        self.assertIsNotNone(msg)
        # Verify AAR captured comms event
        self.assertTrue(any("COMMS" in e.event_type for e in self.aar.events))

    def test_order_issuance_and_divergence(self):
        # Move Platoon Alpha
        target = Vector2D(400.0, 400.0)
        order = self.sim.issue_order(
            role=Role.COMMANDER,
            unit_id="blue_plt1",
            order_type="MOVE",
            target=target,
            rationale="Advance to secure defile road junction before enemy armor arrives"
        )
        self.assertEqual(order.order_type, "MOVE")
        self.assertEqual(order.issuer_role, Role.COMMANDER)

        # Advance sim clock
        self.sim.tick(5.0)
        unit = self.sim.units["blue_plt1"]
        # Unit should have moved toward destination
        self.assertGreater(unit.position.x, 310.0)

    def test_aar_report_generation(self):
        # Advance simulation
        for _ in range(10):
            self.sim.tick(1.0)

        metrics = self.aar.compute_metrics()
        self.assertIn("command_effectiveness_score", metrics)
        self.assertIn("doctrine_rating", metrics)

        html = self.aar.generate_html_report()
        self.assertIn("AFTER ACTION REVIEW", html)
        self.assertIn("Effectiveness Score", html)

    def test_room_and_configuration_lifecycle(self):
        # User joins
        user = self.sim.join_user("client_123", "VIPER-1", role=Role.COMMANDER)
        self.assertEqual(user.callsign, "VIPER-1")
        self.assertIn("client_123", self.sim.participants)

        # Toggle ready
        is_ready = self.sim.toggle_user_ready("client_123")
        self.assertTrue(is_ready)

        # Update configuration
        self.sim.update_config({
            "scenario_id": "urban_aegis",
            "duration_minutes": 15,
            "difficulty": "SEVERE",
            "max_users": 8
        })
        self.assertEqual(self.sim.config.duration_minutes, 15)
        self.assertEqual(self.sim.config.difficulty, "SEVERE")

        # Start exercise
        self.sim.start_exercise()
        self.assertEqual(self.sim.status, "RUNNING")

        # Complete exercise
        self.sim.complete_exercise()
        self.assertEqual(self.sim.status, "COMPLETED")

if __name__ == "__main__":
    unittest.main()

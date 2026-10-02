"""
In-memory Protocol and Server Integration Tests
Validates HTTP request routing, RFC-6455 WebSocket handshaking,
and AAR endpoint response bodies without needing external network sockets.
"""

import unittest
import asyncio
from server import TacticalTrainerServer, MAGIC_WS_GUID, WebSocketConnection
import hashlib
import base64
import json

class MockStreamWriter:
    def __init__(self):
        self.data = bytearray()
        self.closed = False

    def write(self, b: bytes):
        self.data.extend(b)

    async def drain(self):
        pass

    def close(self):
        self.closed = True

class TestServerProtocol(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.server = TacticalTrainerServer(host="127.0.0.1", port=8000)

    async def test_http_index_handling(self):
        reader = asyncio.StreamReader()
        reader.feed_data(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        reader.feed_eof()
        writer = MockStreamWriter()

        await self.server.handle_http("GET", "/", writer)
        response_text = writer.data.decode("utf-8", errors="ignore")
        self.assertIn("HTTP/1.1 200 OK", response_text)
        self.assertIn("MULTI-DOMAIN DMUU TRAINER", response_text)

    async def test_http_aar_generation(self):
        reader = asyncio.StreamReader()
        reader.feed_data(b"GET /aar HTTP/1.1\r\nHost: localhost\r\n\r\n")
        reader.feed_eof()
        writer = MockStreamWriter()

        await self.server.handle_http("GET", "/aar", writer)
        response_text = writer.data.decode("utf-8", errors="ignore")
        self.assertIn("HTTP/1.1 200 OK", response_text)
        self.assertIn("AFTER ACTION REVIEW", response_text)
        self.assertIn("Effectiveness Score", response_text)

    async def test_http_api_aar_json(self):
        writer = MockStreamWriter()
        await self.server.handle_http("GET", "/api/aar.json", writer)
        response_text = writer.data.decode("utf-8", errors="ignore")
        self.assertIn("HTTP/1.1 200 OK", response_text)
        self.assertIn('"command_effectiveness_score"', response_text)

    async def test_http_download_pdf_report(self):
        writer = MockStreamWriter()
        await self.server.handle_http("GET", "/api/aar/download-pdf?room=ALPHA-6", writer)
        self.assertIn(b"Content-Type: application/pdf", writer.data)
        self.assertIn(b"%PDF-1.4", writer.data)
        self.assertIn(b"%%EOF", writer.data)

    async def test_multi_room_isolation(self):
        room_a = self.server.get_or_create_room("ROOM-A")
        room_b = self.server.get_or_create_room("ROOM-B")

        self.assertNotEqual(id(room_a), id(room_b))
        room_a.join_user("user_1", "WARLORD-1", "TRAINEE", "COMMANDER")
        room_b.join_user("user_2", "TITAN-2", "TRAINEE", "PLATOON_ALPHA")

        self.assertIn("user_1", room_a.participants)
        self.assertNotIn("user_1", room_b.participants)
        self.assertIn("user_2", room_b.participants)
        self.assertNotIn("user_2", room_a.participants)

    async def test_contradictory_intel_inject(self):
        room = self.server.get_or_create_room("ROOM-TEST")
        initial_msg_count = len(room.messages)
        room.inject_contradictory_intel("TAC-1", "TEST CONTRADICTORY SITREP")
        self.assertEqual(len(room.messages), initial_msg_count + 1)
        self.assertEqual(room.messages[-1].msg_type, "CONTRADICTORY_SITREP")
        self.assertIn("TEST CONTRADICTORY SITREP", room.messages[-1].raw_content)

    async def test_websocket_rfc6455_handshake(self):
        key = "dGhlIHNhbXBsZSBub25jZQ=="
        expected_accept = base64.b64encode(hashlib.sha1((key + MAGIC_WS_GUID).encode()).digest()).decode()

        writer = MockStreamWriter()
        reader = asyncio.StreamReader()
        # Feed client close frame to terminate read loop
        reader.feed_data(bytearray([0x88, 0x00])) # Close opcode 0x8
        reader.feed_eof()

        await self.server.upgrade_websocket(reader, writer, key)
        resp = writer.data.decode("utf-8", errors="ignore")
        self.assertIn("101 Switching Protocols", resp)
        self.assertIn(f"Sec-WebSocket-Accept: {expected_accept}", resp)

if __name__ == "__main__":
    unittest.main()

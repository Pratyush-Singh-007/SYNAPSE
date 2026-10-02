"""
Multi-Domain Tactical Decision-Making Trainer - Asynchronous Server
Zero-external-dependency HTTP and RFC-6455 WebSocket server using Python 3 asyncio.
Provides multi-room multiplayer state sync, degradation feeds, and AAR reporting with PDF export.
"""

import os
import sys
import time
import json
import base64
import hashlib
import struct
import asyncio
import mimetypes
import traceback
from typing import Dict, Set, Optional, Tuple, List, Any

from sim.models import Role, Vector2D
from sim.scenario_engine import ScenarioEngine
from sim.aar_engine import AAREngine

MAGIC_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def safe_json_dumps(obj: Any, **kwargs) -> str:
    def default_serializer(o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    return json.dumps(obj, default=default_serializer, **kwargs)

class WebSocketConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.role: str = Role.COMMANDER
        self.client_id: str = f"client_{id(self)}"
        self.is_closed: bool = False
        self.room_code: str = "ALPHA-6"
        self.callsign: str = "WARLORD-6"
        self.user_type: str = "TRAINEE"

    async def send_text(self, text: str):
        if self.is_closed:
            return
        payload = text.encode("utf-8")
        payload_len = len(payload)

        # Build frame: FIN=1, Opcode=1 (Text) -> 0x81
        frame = bytearray([0x81])

        if payload_len <= 125:
            frame.append(payload_len)
        elif payload_len <= 65535:
            frame.append(126)
            frame.extend(struct.pack("!H", payload_len))
        else:
            frame.append(127)
            frame.extend(struct.pack("!Q", payload_len))

        frame.extend(payload)
        try:
            self.writer.write(frame)
            await self.writer.drain()
        except Exception:
            self.is_closed = True

    async def read_frame(self) -> Optional[str]:
        try:
            header = await self.reader.readexactly(2)
        except (asyncio.IncompleteReadError, ConnectionResetError):
            return None

        byte1, byte2 = header[0], header[1]
        fin = (byte1 & 0x80) != 0
        opcode = byte1 & 0x0F
        has_mask = (byte2 & 0x80) != 0
        payload_len = byte2 & 0x7F

        if opcode == 0x8:  # Connection Close
            return None

        if payload_len == 126:
            ext_len = await self.reader.readexactly(2)
            payload_len = struct.unpack("!H", ext_len)[0]
        elif payload_len == 127:
            ext_len = await self.reader.readexactly(8)
            payload_len = struct.unpack("!Q", ext_len)[0]

        mask = None
        if has_mask:
            mask = await self.reader.readexactly(4)

        payload = await self.reader.readexactly(payload_len)
        if has_mask and mask:
            unmasked = bytearray(payload_len)
            for i in range(payload_len):
                unmasked[i] = payload[i] ^ mask[i % 4]
            payload = unmasked

        if opcode == 0x1:  # Text frame
            return payload.decode("utf-8", errors="replace")
        elif opcode == 0x9:  # Ping
            pong = bytearray([0x8A, 0x00])
            self.writer.write(pong)
            await self.writer.drain()
            return await self.read_frame()

        return None

class TacticalTrainerServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.rooms: Dict[str, ScenarioEngine] = {}
        self.clients: Set[WebSocketConnection] = set()
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        # Ensure default room is created
        self.get_or_create_room("ALPHA-6")

    def get_or_create_room(self, room_code: str = "ALPHA-6") -> ScenarioEngine:
        code = (room_code or "ALPHA-6").strip().upper()
        if code not in self.rooms:
            aar = AAREngine(f"Operation Broken Uplink [{code}]")
            self.rooms[code] = ScenarioEngine(aar)
        return self.rooms[code]

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            line = await reader.readline()
            if not line:
                writer.close()
                return

            req_line = line.decode("utf-8", errors="ignore").strip()
            parts = req_line.split()
            if len(parts) < 2:
                writer.close()
                return

            method, path = parts[0], parts[1]
            headers: Dict[str, str] = {}

            while True:
                header_line = await reader.readline()
                if not header_line or header_line == b"\r\n":
                    break
                h_str = header_line.decode("utf-8", errors="ignore").strip()
                if ":" in h_str:
                    k, v = h_str.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            # Check if WebSocket Upgrade
            if headers.get("upgrade", "").lower() == "websocket" and "sec-websocket-key" in headers:
                await self.upgrade_websocket(reader, writer, headers.get("sec-websocket-key", ""))
            else:
                await self.handle_http(method, path, writer)
        except Exception as e:
            traceback.print_exc()
            try:
                writer.close()
            except Exception:
                pass

    async def upgrade_websocket(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, key: str):
        # Calculate RFC-6455 response
        accept_raw = key + MAGIC_WS_GUID
        accept_sha = hashlib.sha1(accept_raw.encode("utf-8")).digest()
        accept_b64 = base64.b64encode(accept_sha).decode("utf-8")

        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_b64}\r\n\r\n"
        )
        writer.write(response.encode("utf-8"))
        await writer.drain()

        ws = WebSocketConnection(reader, writer)
        self.clients.add(ws)
        engine = self.get_or_create_room(ws.room_code)
        engine.register_player(ws.role, ws.client_id)

        try:
            # Send initial welcome state
            initial_state = engine.get_role_state(ws.role)
            await ws.send_text(safe_json_dumps({"type": "STATE_UPDATE", "data": initial_state}))

            while not ws.is_closed:
                msg_text = await ws.read_frame()
                if msg_text is None:
                    break
                await self.process_client_message(ws, msg_text)
        finally:
            self.clients.discard(ws)
            if ws.room_code in self.rooms:
                room_eng = self.rooms[ws.room_code]
                room_eng.remove_user(ws.client_id)
                room_eng.unregister_player(ws.role, ws.client_id)
            try:
                writer.close()
            except Exception:
                pass

    async def process_client_message(self, ws: WebSocketConnection, text: str):
        try:
            data = json.loads(text)
            action = data.get("action")

            if action == "LOGIN":
                room_code = (data.get("room_code") or "ALPHA-6").strip().upper()
                callsign = data.get("callsign", "OPERATOR").strip()
                user_type = data.get("user_type", "TRAINEE")
                role = data.get("role", Role.COMMANDER)

                # If switching room, clean up from old room
                if ws.room_code != room_code and ws.room_code in self.rooms:
                    old_eng = self.rooms[ws.room_code]
                    old_eng.remove_user(ws.client_id)
                    old_eng.unregister_player(ws.role, ws.client_id)

                ws.room_code = room_code
                ws.callsign = callsign
                ws.user_type = user_type
                ws.role = role

                engine = self.get_or_create_room(ws.room_code)
                engine.join_user(ws.client_id, callsign, user_type, role)
                state = engine.get_role_state(ws.role)
                await ws.send_text(safe_json_dumps({"type": "STATE_UPDATE", "data": state}))
                return

            engine = self.get_or_create_room(ws.room_code)

            if action == "SELECT_ROLE":
                new_role = data.get("role", Role.COMMANDER)
                engine.unregister_player(ws.role, ws.client_id)
                ws.role = new_role
                if ws.client_id in engine.participants:
                    engine.participants[ws.client_id].role = new_role
                engine.register_player(ws.role, ws.client_id)
                state = engine.get_role_state(ws.role)
                await ws.send_text(safe_json_dumps({"type": "STATE_UPDATE", "data": state}))

            elif action == "UPDATE_CONFIG":
                config_data = data.get("config", {})
                engine.update_config(config_data)

            elif action == "TOGGLE_READY":
                engine.toggle_user_ready(ws.client_id)

            elif action == "START_EXERCISE":
                engine.start_exercise()

            elif action == "END_EXERCISE":
                engine.complete_exercise()

            elif action == "ISSUE_ORDER":
                unit_id = data.get("unit_id")
                order_type = data.get("order_type", "MOVE")
                target_raw = data.get("target")
                rationale = data.get("rationale", "")
                target = Vector2D(target_raw["x"], target_raw["y"]) if target_raw else None
                engine.issue_order(ws.role, unit_id, order_type, target, rationale)

            elif action == "TRANSMIT_COMMS":
                channel = data.get("channel", "TAC-1")
                content = data.get("content", "")
                msg_type = data.get("msg_type", "SITREP")
                engine.transmit_message(ws.role, channel, content, msg_type)

            elif action == "INSTRUCTOR_ACTION":
                sub_action = data.get("sub_action")
                if sub_action == "TRIGGER_INJECT":
                    engine.trigger_inject_by_id(data.get("inject_id"))
                elif sub_action == "TOGGLE_JAMMER":
                    engine.toggle_jammer(data.get("jammer_id"), data.get("active"))
                elif sub_action == "MOVE_JAMMER":
                    engine.update_jammer_position(
                        data.get("jammer_id"),
                        float(data.get("x", 500)),
                        float(data.get("y", 500))
                    )
                elif sub_action == "CYBER_ATTACK":
                    engine.trigger_cyber_attack(
                        target_role=data.get("target_role", "ALL"),
                        subsystem=data.get("subsystem", "BFT"),
                        disruption_type=data.get("disruption_type", "BLACKOUT"),
                        duration=float(data.get("duration", 60.0))
                    )
                elif sub_action == "CONTRADICTORY_INTEL":
                    engine.inject_contradictory_intel(
                        channel=data.get("channel", "TAC-1"),
                        custom_text=data.get("text", "")
                    )
                elif sub_action == "SIM_CONTROL":
                    cmd = data.get("command")
                    if cmd == "PAUSE":
                        engine.is_paused = True
                    elif cmd == "RESUME":
                        engine.is_paused = False
                    elif cmd == "RESET":
                        engine.load_scenario(engine.config.scenario_id)

        except Exception as e:
            traceback.print_exc()

    def _extract_room_from_query(self, path: str) -> str:
        if "?" in path:
            query = path.split("?", 1)[1]
            for param in query.split("&"):
                if param.startswith("room="):
                    return param.split("=", 1)[1].strip().upper()
        return "ALPHA-6"

    async def handle_http(self, method: str, path: str, writer: asyncio.StreamWriter):
        clean_path = path.split("?")[0].lstrip("/")
        room_code = self._extract_room_from_query(path)
        engine = self.get_or_create_room(room_code)

        if not clean_path or clean_path == "index.html":
            file_path = os.path.join(self.static_dir, "index.html")
        elif clean_path == "aar" or clean_path == "aar.html":
            aar_html = engine.aar_engine.generate_html_report().encode("utf-8")
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(aar_html)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + aar_html
            writer.write(resp)
            await writer.drain()
            writer.close()
            return
        elif clean_path == "api/aar.json":
            metrics = engine.aar_engine.compute_metrics()
            events = [e.to_dict() for e in engine.aar_engine.events]
            body = json.dumps({"room": room_code, "metrics": metrics, "events": events}, indent=2).encode("utf-8")
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + body
            writer.write(resp)
            await writer.drain()
            writer.close()
            return
        elif clean_path == "api/aar/download-pdf":
            # True PDF report export!
            pdf_bytes = engine.aar_engine.generate_pdf_report()
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/pdf\r\n"
                f'Content-Disposition: attachment; filename="AAR_{room_code}_Report.pdf"\r\n'
                f"Content-Length: {len(pdf_bytes)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + pdf_bytes
            writer.write(resp)
            await writer.drain()
            writer.close()
            return
        elif clean_path == "api/aar/download-report":
            aar_html = engine.aar_engine.generate_html_report().encode("utf-8")
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html; charset=utf-8\r\n"
                f'Content-Disposition: attachment; filename="AAR_{room_code}_Report.html"\r\n'
                f"Content-Length: {len(aar_html)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + aar_html
            writer.write(resp)
            await writer.drain()
            writer.close()
            return
        elif clean_path == "api/scenarios":
            from sim.scenarios import list_available_scenarios
            body = json.dumps(list_available_scenarios(), indent=2).encode("utf-8")
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + body
            writer.write(resp)
            await writer.drain()
            writer.close()
            return
        else:
            file_path = os.path.join(self.static_dir, clean_path)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            not_found = b"HTTP/1.1 404 Not Found\r\nContent-Length: 13\r\nConnection: close\r\n\r\n404 Not Found"
            writer.write(not_found)
            await writer.drain()
            writer.close()
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        header = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {mime_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode("utf-8")

        writer.write(header + content)
        await writer.drain()
        writer.close()

    async def simulation_loop(self):
        """
        Runs at 10 Hz to update physics, injects, and broadcast customized states per room.
        """
        last_time = time.time()
        while True:
            await asyncio.sleep(0.1)  # 100ms tick (10 Hz)
            now = time.time()
            dt = now - last_time
            last_time = now

            try:
                # Tick each active simulation room
                for room_engine in list(self.rooms.values()):
                    room_engine.tick(dt)

                # Broadcast tailored states to all connected clients
                if self.clients:
                    state_cache: Dict[Tuple[str, str], str] = {}
                    for client in list(self.clients):
                        if client.is_closed:
                            continue
                        cache_key = (client.room_code, client.role)
                        if cache_key not in state_cache:
                            engine = self.get_or_create_room(client.room_code)
                            st = engine.get_role_state(client.role)
                            state_cache[cache_key] = safe_json_dumps({"type": "STATE_UPDATE", "data": st})

                        payload_json = state_cache[cache_key]
                        asyncio.create_task(client.send_text(payload_json))
            except Exception as e:
                traceback.print_exc()

    async def start(self):
        # Auto-port detection fallback to avoid occupied/blocked ports
        candidate_ports = [self.port, 8000, 8088, 7777, 3000]
        server = None
        bound_port = self.port

        for p in candidate_ports:
            try:
                server = await asyncio.start_server(self.handle_connection, self.host, p)
                bound_port = p
                self.port = p
                break
            except Exception as e:
                print(f"[TACTICAL TRAINER] Port {p} unavailable ({e}), trying next candidate...")

        if server is None:
            raise RuntimeError(f"Could not bind server to any candidate port: {candidate_ports}")

        print("======================================================================")
        print(" IMMERSIVE MULTI-DOMAIN DECISION-MAKING TRAINER (DMUU)                ")
        print(" For Degraded & Contested Communication Environments                 ")
        print("======================================================================")
        print(f" Tactical Terminal: http://localhost:{self.port}")
        print(f" Live AAR Debrief:  http://localhost:{self.port}/aar")
        print(f" Download PDF AAR:  http://localhost:{self.port}/api/aar/download-pdf")
        print(f" API Metrics JSON:  http://localhost:{self.port}/api/aar.json")
        print("======================================================================")

        asyncio.create_task(self.simulation_loop())
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = TacticalTrainerServer(host="0.0.0.0", port=port)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("[TACTICAL TRAINER] Server shutdown.")

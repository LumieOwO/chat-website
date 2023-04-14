import socket
from threading import Thread
import hashlib
import base64
import struct
import typing


class WebsocketController:
    _MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._clients = []
        self._websocket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return None

    def start(self) -> None:
        self._websocket_server.bind((self._host, self._port))
        self._websocket_server.listen(1)
        Thread(target=self._listen_to_connection).start()
        return None

    def _listen_to_connection(self) -> None:
        while True:
            conn, addr = self._websocket_server.accept()
            Thread(target=self._handle_connection, args=[conn]).start()
        return None

    def _parse_websocket_message(self, data: bytes) -> typing.Union[str, None]:
        opcode = data[0] & 0x0F
        if opcode == 8:
            return None

        payload_len = data[1] & 0x7F
        if payload_len == 126:
            payload_len = struct.unpack(">H", data[2:4])[0]
            payload_offset = 4
        elif payload_len == 127:
            payload_len = struct.unpack(">Q", data[2:10])[0]
            payload_offset = 10
        else:
            payload_offset = 2

        masking_key = data[payload_offset : payload_offset + 4]
        payload = data[payload_offset + 4 :]

        unmasked_payload = bytearray(len(payload))
        for i in range(len(payload)):
            unmasked_payload[i] = payload[i] ^ masking_key[i % 4]

        message = unmasked_payload.decode()
        return message

    def _handle_connection(self, conn: socket.socket) -> None:
        headers = {}
        request = conn.recv(1024).decode()
        for line in request.split("\r\n")[1:]:
            if line:
                key, value = line.split(": ")
                headers[key] = value

        if headers.get("Upgrade", "") != "websocket":
            conn.close()
            return None

        key = headers["Sec-WebSocket-Key"]
        key += self._MAGIC_STRING
        sha1 = hashlib.sha1(bytes(key, "utf-8"))
        accept_key = base64.b64encode(sha1.digest()).decode()

        response = "HTTP/1.1 101 Switching Protocols\r\n"
        response += "Upgrade: websocket\r\n"
        response += "Connection: Upgrade\r\n"
        response += f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
        conn.sendall(response.encode())
        self._clients.append(conn)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = self._parse_websocket_message(data)
            if message is None:
                break
            response_opcode = 0x81
            response_payload = bytes(f"42/msg{message}","utf-8")
            response_header = bytes([response_opcode])
            response_header += bytes([len(response_payload)])
            encoded = response_header + response_payload
            for client in self._clients:
                client.sendall(encoded)
                 
        self._clients.remove(conn)
        return None

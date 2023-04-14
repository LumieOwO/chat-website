import socket
from threading import Thread


class WebpageController:
    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        self._host: str = host
        self._port: str = port
        self._endpoints: dict = {}

    def add_endpoint(
        self, endpoint: str, html_file: str, METHOD=["GET"], function_hook=None
    ) -> None:
        self._endpoints[endpoint] = [html_file, METHOD, function_hook]
        return None

    def start(self) -> None:
        self._socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        Thread(target=self._listen_to_connection()).start()
        return None

    def _handle_request(self, req: str) -> str:
        parsed_req: str = req.split()
        for endpoint in self._endpoints:
            if (
                endpoint == parsed_req[1]
                and parsed_req[0] in self._endpoints[endpoint][1]
            ):
                html_file: str = self._endpoints[endpoint][0]
                if self._endpoints[endpoint][2] != None:
                    Thread(target=self._endpoints[endpoint][2]()).start()
                with open(html_file) as htmlf:
                    html_file: str = htmlf.read()
                response: str = (
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_file}"
                )
                return response
        response: str = (
            "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n404 Not Found"
        )
        return response

    def _handle_connection(self, conn: socket.socket) -> None:
        with conn:
            request = conn.recv(1048576)
            data: str = self._handle_request(request.decode())
            conn.sendall(data.encode("utf-8"))
            conn.close()
        return None

    def _listen_to_connection(self) -> None:
        while True:
            self._socket.listen()
            conn, addr = self._socket.accept()
            Thread(target=self._handle_connection, args=[conn]).start()

from threading import Thread
from websocketr.websocket_controller import WebsocketController
from webpage.webpage_controller import WebpageController
if __name__ == "__main__":
    WSC = WebsocketController("127.0.0.2", 8000)
    WSC.start()
    WPC = WebpageController("127.0.0.1", 80)
    WPC.add_endpoint(endpoint="/",html_file="html/index.html")
    Thread(target=WPC.start()).start()
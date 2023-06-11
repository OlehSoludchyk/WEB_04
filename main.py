from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mimetypes
import pathlib
import socket
import json
from datetime import datetime
import threading


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)


    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def socket_udp():
    IP = ''
    PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = IP, PORT
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            current_time = datetime.now()
            message_data = json.loads(data.decode())
            save_message_json(message_data, current_time)


    except KeyboardInterrupt:
        print('Destroy server.')
    finally:
        sock.close()


def save_message_json(message_data, current_time):
    json_path = 'storage/data.json'
    json_data = {}

    if pathlib.Path(json_path).exists():
        with open(json_path, 'r') as fh:
            json_data = json.load(fh)

    json_data[current_time.isoformat()] = message_data

    with open(json_path, 'w') as fh:
        json.dump(json_data, fh)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print('Server running...')
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    http_thread = threading.Thread(target=run)
    socket_thread = threading.Thread(target=socket_udp)

    http_thread.start()
    socket_thread.start()
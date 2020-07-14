import os
import json
from http.server import SimpleHTTPRequestHandler
from DialProgram import DialProgram

# Useful stuff from: https://stackoverflow.com/a/46332163


class StargateHttpHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join('web', relpath)
        return fullpath

    def do_POST(self):
        print(('POST: {}'.format(self.path)))

        if self.path == '/shutdown':
            os.system('systemctl poweroff')
            self.send_response(200, 'OK')
            return
        
        if self.path == '/reboot':
            os.system('systemctl reboot')
            self.send_response(200, 'OK')
            return
        
        # https://unix.stackexchange.com/questions/21089/how-to-use-command-line-to-change-volume
        
        if self.path == '/volumeup':
            os.system('amixer set PCM 5%+')
            self.send_response(200, 'OK')
            return
        
        if self.path == '/volumedown':
            os.system('amixer set PCM 5%-')
            self.send_response(200, 'OK')
            return

        if self.path == '/dialstatus':
            if DialProgram.is_dialing:
                self.send_response(200, '1')
            else:
                self.send_response(204, '0')
            return

        if self.path != '/update':
            self.send_error(404)
            return

        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body)
        self.send_response(200, 'OK')
        self.end_headers()
        StargateHttpHandler.logic.execute_command(data)

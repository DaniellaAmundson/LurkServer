#!/usr/bin/python3

import socket
from sys import argv
import threading
from lurkGame import *
from signal import signal, SIGPIPE, SIG_DFL


signal(SIGPIPE, SIG_DFL)


class LurkServer:
    def __init__(self, sock):
        self.sock = sock
        self.threads = []
        self.running = False
        self.game = Game()

    def run(self):
        self.running = True
        self.game.playing = True
        self.sock.listen(10)
        while self.running:
            c, addr = self.sock.accept()
            thr = threading.Thread(None, self.game.startPlayer, None, args=(c,))
            self.threads.append(thr)
            thr.start()

        self.shutdown()

    def shutdown(self):
        self.running = False
        self.game.playing = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            for thr in self.threads:
                thr.join()

        except:
            pass


if __name__ == "__main__":
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 5002
    if len(argv) > 1:
        port = int(argv[1])

    skt.bind(("", port))
    server = LurkServer(skt)
    try:
        server.run()

    except:
        skt.shutdown(socket.SHUT_RDWR)
        skt.close()
        server.shutdown()

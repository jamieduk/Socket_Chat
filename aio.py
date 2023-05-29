import asyncio
import websockets
import logging
import socket
import sys

import warnings

# ...

async def client():
    warnings.filterwarnings("ignore", category=DeprecationWarning)  # Suppress DeprecationWarning
    print("Starting Message-Box By (c) J~Net 2023")

class MessageBoxApp:
    def __init__(self):
        self.local_host=None
        self.local_port=None
        self.remote_host=None
        self.remote_port=None

    def check_address_in_use(self, host, port):
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result=sock.connect_ex((host, port))
            if result == 0:
                return True  # Address is in use
            else:
                return False  # Address is available
        finally:
            sock.close()

    async def start_host(self):
        try:
            async with websockets.serve(
                self.handle_client, self.local_host, self.local_port,
                ping_interval=25, reuse_address=True
            ):
                print(f"Host is listening on {self.local_host}:{self.local_port}")
                await asyncio.Future()  # Run forever
        except OSError as e:
            if 'address already in use' not in str(e):
                logging.error("Error connecting to remote host: %s", str(e))
            await asyncio.sleep(1)  # Wait and try reconnecting

    async def handle_client(self, websocket, path):
        try:
            while True:
                message=await websocket.recv()
                print("Received message:", message)
                response=input("Enter Message For Host (or 'q' to quit): ")
                if response == 'q':
                    break
                await websocket.send(response)
        except websockets.ConnectionClosed:
            logging.info("Client Connection Closed.")
            await self.start_host()  # Reconnect

    def set_local_host(self):
        self.local_host=input("Enter Local Host IP: ")
        with open('local_host.txt', 'w') as file:
            file.write(self.local_host)

    def set_local_port(self):
        self.local_port=int(input("Enter local port:  (Default is 3312) "))
        with open('local_port.txt', 'w') as file:
            file.write(str(self.local_port))

    def set_remote_host_ip(self):
        self.remote_host=input("Enter Remote Host IP: ")
        with open('remote_host.txt', 'w') as file:
            file.write(self.remote_host)

    def set_remote_port(self):
        self.remote_port=int(input("Enter Remote Port: (Default is 3312) "))
        with open('remote_port.txt', 'w') as file:
            file.write(str(self.remote_port))

    def read_from_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    async def connect_to_remote_host(self):
        self.remote_host=self.read_from_file('remote_host.txt')
        self.remote_port=self.read_from_file('remote_port.txt')

        if not self.remote_host or not self.remote_port:
            print("Remote host IP and port are not set. Please configure them.")
            self.set_remote_host_ip()
            self.set_remote_port()

        while True:
            try:
                # Create a connection to the remote host
                uri=f"ws://{self.remote_host}:{self.remote_port}"
                async with websockets.connect(uri, ping_interval=25) as websocket:
                    while True:
                        message=input("Enter a message to send to the remote host (or 'q' to quit): ")
                        if message == 'q':
                            break
                        await websocket.send(message)
                        print("Message sent.")
                        response=await websocket.recv()
                        print("Received Response From Remote Host:", response)
            except (websockets.WebSocketException, ConnectionRefusedError):
                pass  # Ignore the exceptions and continue looping
            except Exception as e:
                if 'There is no current event loop' not in str(e):
                    logging.error("Error Connecting To Remote Host: %s", str(e))
                await asyncio.sleep(1)  # Wait and try reconnecting

    def run(self):
        self.local_host=self.read_from_file('local_host.txt')
        self.local_port=self.read_from_file('local_port.txt')

        if not self.local_host or not self.local_port:
            self.set_local_host()
            self.set_local_port()

        # Check if the address and port are already in use
        if self.check_address_in_use(self.local_host, int(self.local_port)):
            print(f"The address {self.local_host}:{self.local_port} is already in use.")
            sys.exit(1)

        loop=asyncio.get_event_loop()  # Get the default event loop
        loop.run_until_complete(self.main_loop())

    async def main_loop(self):
        while True:
            choice=input("Menu:\n"
                           "1. Connect to remote host\n"
                           "2. Host for incoming connections\n"
                           "3. Set remote host IP\n"
                           "4. Set remote port\n"
                           "5. Set local host\n"
                           "6. Set local port\n"
                           "Enter your choice (1-6): ")

            if choice == '1':
                await self.connect_to_remote_host()
            elif choice == '2':
                await self.start_host()
            elif choice == '3':
                self.set_remote_host_ip()
            elif choice == '4':
                self.set_remote_port()
            elif choice == '5':
                self.set_local_host()
            elif choice == '6':
                self.set_local_port()
            else:
                print("Invalid choice. Please try again.")


app=MessageBoxApp()
app.run()


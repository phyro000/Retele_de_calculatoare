import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return f"OK - record add"

    def get(self, key):
        with self.lock:
            return self.data.get(key, "ERROR invalid key")

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return "OK value deleted"
            return "ERROR invalid key"

    def list_all(self):
        with self.lock:
            pairs = ",".join(f"{k}={v}" for k, v in self.data.items())
            return f"DATA|{pairs}"

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key in self.data:
                self.data[key] = value
                return "Data updated"
            return "ERROR invalid key"

    def pop(self, key):
        with self.lock:
            if key in self.data:
                return f"Data {self.data.pop(key)}"
            return "ERROR invalid key"

state = State()

def process_command(command):
    parts = command.split()
    if len(parts) < 1:
        return "Invalid command format"

    cmd = parts[0].upper()

    if cmd == "ADD" and len(parts) > 2:
        return state.add(parts[1], ' '.join(parts[2:]))
    elif cmd == "GET" and len(parts) == 2:
        return state.get(parts[1])
    elif cmd == "REMOVE" and len(parts) == 2:
        return state.remove(parts[1])
    elif cmd == "LIST":
        return state.list_all()
    elif cmd == "COUNT":
        return state.count()
    elif cmd == "CLEAR":
        return state.clear()
    elif cmd == "UPDATE" and len(parts) > 2:
        return state.update(parts[1], ' '.join(parts[2:]))
    elif cmd == "POP" and len(parts) == 2:
        return state.pop(parts[1])
    elif cmd == "QUIT":
        return "QUIT"

    return f"ERROR unknown command '{cmd}'"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                response = process_command(command)

                if response == "QUIT":
                    client_socket.sendall(f"{len('Connection closed')} Connection closed".encode('utf-8'))
                    break

                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

            except Exception as e:
                client_socket.sendall(f"Error: {str(e)}".encode('utf-8'))
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
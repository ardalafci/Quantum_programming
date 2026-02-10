import socket, json, random
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def get_probs(st, base):
    qml.StatePrep(np.array(st), wires=0)
    if base == 'x': qml.Hadamard(wires=0)
    return qml.probs(wires=0)

def intercept(st):
    base = random.choice(['+', 'x'])
    probs = get_probs(st, base)
    res = np.random.choice([0, 1], p=probs)
    if base == 'x':
        new_st = np.array([1/np.sqrt(2), 1/np.sqrt(2)] if res == 0 else [1/np.sqrt(2), -1/np.sqrt(2)], dtype=complex)
    else:
        new_st = np.array([1, 0] if res == 0 else [0, 1], dtype=complex)
    return new_st

def start_eve():
    bob_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bob_s.connect(('127.0.0.1', 65432))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 65433))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            raw = b""
            while True:
                chunk = conn.recv(4096)
                raw += chunk
                if len(chunk) < 4096: break
            data = json.loads(raw.decode())
            states = [np.array([complex(c[0], c[1]) for c in s_list]) for s_list in data['states']]
            crashed = [[[float(c.real), float(c.imag)] for c in intercept(sv)] for sv in states]
            bob_s.sendall(json.dumps({'states': crashed}).encode())
            conn.sendall(bob_s.recv(32768))

if __name__ == "__main__":
    start_eve()
import socket, json, sys, random, time
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def prepare(bit, base):
    if bit == 1: qml.PauliX(wires=0)
    if base == 'x': qml.Hadamard(wires=0)
    return qml.state()

def encrypt(msg, key):
    binary_msg = ''.join(format(ord(c), '08b') for c in msg)
    if not key: return "0" * len(binary_msg)
    return "".join(str(int(binary_msg[i]) ^ key[i % len(key)]) for i in range(len(binary_msg)))

def run_alice():
    target_port = 65433 if (len(sys.argv) > 1 and sys.argv[1] == "casus") else 65432
    n = 50
    bits = [random.choice([0,1]) for _ in range(n)]
    bases = [random.choice(['+','x']) for _ in range(n)]
    states = [[[float(c.real), float(c.imag)] for c in prepare(bits[i], bases[i])] for i in range(n)]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', target_port))
        
        # 1. Qubitleri yolla
        s.sendall(json.dumps({'states': states}).encode())
        
        # 2. Bob'dan bazları bekle (Burada socket bloklanacaktır)
        raw_resp = s.recv(32768)
        resp = json.loads(raw_resp.decode())
        
        # 3. Sifting ve Şifreleme
        match_indices = [i for i in range(n) if bases[i] == resp['bases'][i]]
        alice_key = [bits[i] for i in match_indices]
        enc_text = encrypt("ARDA", alice_key)
        
        # 4. Bob'un hazır olması için minik bir bekleme ve ikinci paketi yolla
        time.sleep(0.1)
        s.sendall(json.dumps({'match_indices': match_indices, 'encrypted_text': enc_text}).encode())
        
        analysis = [(1 if bits[i] != resp['results'][i] else 0) if bases[i] == resp['bases'][i] else -1 for i in range(n)]
        print(json.dumps(analysis))

if __name__ == "__main__":
    run_alice()
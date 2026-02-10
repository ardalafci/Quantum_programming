import socket, json, random
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def measure_q(st, ba):
    qml.StatePrep(np.array(st), wires=0)
    if ba == 'x': qml.Hadamard(wires=0)
    return qml.expval(qml.PauliZ(wires=0))

def decrypt(encrypted, key):
    try:
        binary_dec = "".join(str(int(encrypted[i]) ^ key[i % len(key)]) for i in range(len(encrypted)))
        chars = [chr(int(binary_dec[i:i+8], 2)) for i in range(0, len(binary_dec), 8)]
        return "".join(chars)
    except: return "???"

def recv_json(conn):
    # Boş olmayan ilk veriyi yakalayana kadar bekle
    raw = b""
    while not raw:
        raw = conn.recv(131072)
    
    # Verinin devamı varsa onları da topla
    conn.setblocking(False)
    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk: break
            raw += chunk
    except BlockingIOError:
        pass
    finally:
        conn.setblocking(True)
        
    return json.loads(raw.decode())

def start_bob():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 65432))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            # 1. Qubitleri al ve ölç
            data = recv_json(conn)
            states = [np.array([complex(c[0], c[1]) for c in s_list]) for s_list in data['states']]
            bob_bases = [random.choice(['+','x']) for _ in range(len(states))]
            bob_results = [0 if measure_q(st, ba) > 0.5 else 1 for st, ba in zip(states, bob_bases)]
            
            # 2. Bazları gönder
            conn.sendall(json.dumps({'bases': bob_bases, 'results': bob_results}).encode())
            
            # 3. Şifreli mesajı ve indeksleri bekle
            final_data = recv_json(conn)
            indices = final_data['match_indices']
            enc_text = final_data['encrypted_text']
            
            # 4. Çöz ve bas
            final_key = [bob_results[i] for i in indices]
            decrypted = decrypt(enc_text, final_key)
            print(f"SONUÇ_MESAJ:{decrypted}")

if __name__ == "__main__":
    start_bob()
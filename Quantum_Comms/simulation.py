import subprocess, time, json, matplotlib.pyplot as plt

def run_distributed_scenario(with_eve=False):
    bob_proc = subprocess.Popen(['python3', 'bob.py'], stdout=subprocess.PIPE, text=True)
    time.sleep(2) 
    eve_proc = None
    if with_eve:
        eve_proc = subprocess.Popen(['python3', 'eve.py'])
        time.sleep(2)
        alice_cmd = ['python3', 'alice.py', 'casus']
    else:
        alice_cmd = ['python3', 'alice.py']

    result = subprocess.run(alice_cmd, capture_output=True, text=True)
    time.sleep(1)
    bob_proc.terminate()
    bob_out, _ = bob_proc.communicate()
    msg = "Bilinmiyor"
    for line in bob_out.split('\n'):
        if "SONUÇ_MESAJ:" in line: msg = line.split("SONUÇ_MESAJ:")[1]
    if eve_proc: eve_proc.terminate()
    return json.loads(result.stdout.strip().split('\n')[-1]), msg

if __name__ == "__main__":
    print("[*] Dağıtık Kuantum Simülasyonu Başlıyor...")
    res_s, msg_s = run_distributed_scenario(False)
    print(f"[+] Güvenli Hat Mesajı: {msg_s}")
    res_e, msg_e = run_distributed_scenario(True)
    print(f"[!] Casuslu Hat Mesajı: {msg_e}")

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1); plt.title("GÜVENLİ SENARYO")
    plt.bar(range(len(res_s)), [1 if x>=0 else 0.2 for x in res_s], color=['green' if x==0 else 'red' if x==1 else 'lightgray' for x in res_s])
    plt.subplot(2, 1, 2); plt.title("EVE MÜDAHALESİ (CASUS)")
    plt.bar(range(len(res_e)), [1 if x>=0 else 0.2 for x in res_e], color=['green' if x==0 else 'red' if x==1 else 'lightgray' for x in res_e])
    plt.tight_layout(); plt.show()
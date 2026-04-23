# generate_logs.py
import random, datetime
IPS = ["192.168.1.10", "192.168.1.42", "10.0.0.5", "203.0.113.7"]
EVENTS = [
    "{ip} - - [{ts}] \"GET /admin HTTP/1.1\" 403",
    "{ip} - - [{ts}] \"POST /login HTTP/1.1\" 401 - failed password",
    "{ip} sshd: Failed password for root from {ip} port 22",
    "{ip} kernel: UFW BLOCK IN=eth0 SRC={ip} DST=10.0.0.1",
    "{ip} sudo: lateral move attempt detected",
]
logs = []
for i in range(5000):
    ts = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0, 86400))
    ip = random.choice(IPS)
    line = random.choice(EVENTS).format(ip=ip, ts=ts.strftime("%d/%b/%Y:%H:%M:%S"))
    logs.append(line)
with open("server.log", "w") as f:
    f.write("\n".join(logs))
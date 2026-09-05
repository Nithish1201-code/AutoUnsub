import time

from sweeper.config import load_credentials
from sweeper.imap_scan import connect, scan_inbox


credentials = load_credentials()

start = time.perf_counter()

conn = connect(
    credentials["address"],
    credentials["app_password"]
)

connected = time.perf_counter()

if not conn:
    raise SystemExit(1)

results = scan_inbox(
    conn,
    days=7,
    limit=5
)

scanned = time.perf_counter()

print()
print(f"found {len(results)} messages")
print()

for result in results:
    print(result)

conn.logout()

logged_out = time.perf_counter()

print()
print(f"connect: {connected - start:.2f}s")
print(f"scan:    {scanned - connected:.2f}s")
print(f"logout:  {logged_out - scanned:.2f}s")
print(f"total:   {logged_out - start:.2f}s")
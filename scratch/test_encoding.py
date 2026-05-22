import sys
import os

print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8')}")
print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING')}")
print(f"stdout encoding: {sys.stdout.encoding}")
print(f"stderr encoding: {sys.stderr.encoding}")

try:
    print("Test rocket emoji: \U0001f680")
except Exception as e:
    print(f"Stdout print failed: {e}", file=sys.stderr)

try:
    print("Test rocket emoji (stderr): \U0001f680", file=sys.stderr)
except Exception as e:
    print(f"Stderr print failed: {e}", file=sys.stderr)

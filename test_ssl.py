#!/usr/bin/env python3
import os
import sys

print("=== SSL Certificate Test ===")
ssl_cert = "/app/ssl/cert.pem"
ssl_key = "/app/ssl/key.pem"

print(f"Cert path: {ssl_cert}")
print(f"Key path: {ssl_key}")
print(f"Cert exists: {os.path.exists(ssl_cert)}")
print(f"Key exists: {os.path.exists(ssl_key)}")

if os.path.exists(ssl_cert):
    print(f"Cert file size: {os.path.getsize(ssl_cert)} bytes")
if os.path.exists(ssl_key):
    print(f"Key file size: {os.path.getsize(ssl_key)} bytes")

print("============================")
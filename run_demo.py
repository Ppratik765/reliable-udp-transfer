import subprocess
import time
import os
import sys

def main():
    print("===========================================")
    print(" Starting UDP Reliable Data Transfer Demo ")
    print("===========================================")
    
    server_path = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
    client_path = os.path.join(os.path.dirname(__file__), 'client', 'client.py')
    
    print("\n--- Launching Server ---")
    server_proc = subprocess.Popen([sys.executable, server_path])
    
    # Give server a moment to start up and bind to the port
    time.sleep(1.0)
    
    print("\n--- Launching Client ---")
    client_proc = subprocess.Popen([sys.executable, client_path])
    
    # Wait for client to finish its transfer
    client_proc.wait()
    
    # Server will exit automatically 2 seconds after receiving the final ACK 
    # (if the final ACK wasn't dropped, or after it resends and succeeds).
    server_proc.wait()
    
    print("\nDemo completed successfully. The SHA-256 hashes should match!")

if __name__ == "__main__":
    main()

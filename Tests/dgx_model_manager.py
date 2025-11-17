#!/usr/bin/env python3

import paramiko
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DGXModelManager:
    """Manage Ollama models on remote DGX via SSH"""
    
    def __init__(self):
        self.host = os.getenv("LOCAL_DGX_IP", "172.16.10.250").strip('"')
        self.user = os.getenv("LOCAL_DGX_USER", "terasky").strip('"')
        self.password = os.getenv("LOCAL_DGX_PASS", "terasky").strip('"')
        self.ollama_port = 11434
    
    def ssh_execute(self, command):
        """Execute command on DGX via SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, username=self.user, password=self.password)
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            ssh.close()
            return output, error
            
        except Exception as e:
            return "", str(e)
    
    def list_models(self):
        """List available Ollama models"""
        try:
            url = f"http://{self.host}:{self.ollama_port}/api/tags"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            else:
                print(f"API returned status: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name):
        """Pull a model on DGX"""
        print(f"Pulling {model_name} on DGX...")
        output, error = self.ssh_execute(f"ollama pull {model_name}")
        
        if error:
            print(f"Error: {error}")
            return False
        else:
            print(f"Success: {output}")
            return True
    
    def check_ollama_status(self):
        """Check if Ollama is running"""
        output, error = self.ssh_execute("pgrep -f ollama")
        return bool(output.strip())
    
    def start_ollama(self):
        """Start Ollama service"""
        print("Starting Ollama on DGX...")
        output, error = self.ssh_execute("nohup ollama serve > /dev/null 2>&1 &")
        return not bool(error)
    
    def recommend_models_for_ragas(self):
        """Get recommended models for RAGAS evaluation"""
        recommendations = [
            ("llama3.1", "Best overall for evaluation tasks"),
            ("llama3.1:8b", "Good speed/quality balance"),
            ("mistral", "Fast and efficient"),
            ("qwen2.5", "Excellent reasoning capabilities")
        ]
        
        current_models = [m['name'] for m in self.list_models()]
        
        print("Recommended models for RAGAS:")
        for model, desc in recommendations:
            status = "✓ Installed" if any(model in m for m in current_models) else "○ Available"
            print(f"  {status} {model}: {desc}")
        
        return recommendations

def main():
    """Interactive model management"""
    
    manager = DGXModelManager()
    
    print(f"=== DGX Model Manager ===")
    print(f"Host: {manager.host}")
    print(f"User: {manager.user}")
    
    # Check Ollama status
    if not manager.check_ollama_status():
        print("Ollama not running. Starting...")
        if manager.start_ollama():
            print("✓ Ollama started")
        else:
            print("✗ Failed to start Ollama")
            return
    else:
        print("✓ Ollama is running")
    
    # List current models
    models = manager.list_models()
    print(f"\nInstalled models ({len(models)}):")
    for model in models:
        name = model.get('name', 'Unknown')
        size = model.get('size', 0)
        size_gb = round(size / (1024**3), 1) if size > 0 else 0
        print(f"  - {name} ({size_gb}GB)")
    
    # Show recommendations
    print()
    manager.recommend_models_for_ragas()
    
    # Interactive model pulling
    print("\nPull a model? (y/n): ", end="")
    if input().lower() == 'y':
        print("Enter model name (e.g., llama3.1): ", end="")
        model_name = input().strip()
        if model_name:
            manager.pull_model(model_name)

if __name__ == "__main__":
    main()
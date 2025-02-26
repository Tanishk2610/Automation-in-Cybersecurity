#!/usr/bin/env python3
import subprocess
import time
import logging
import json
import sys

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# ---------------------------
# Scope Enforcement Configuration
# ---------------------------
ALLOWED_DOMAINS = ['google.com', 'example.com']
# For simplicity, we are only checking domains here.
# You could extend this to include IP ranges if needed.

def is_in_scope(target: str) -> bool:
    """Check if the target domain is within the allowed scope."""
    for allowed in ALLOWED_DOMAINS:
        if allowed in target:
            return True
    return False

# ---------------------------
# Security Tool Execution Functions
# ---------------------------
def run_nmap(target: str) -> str:
    """Execute an Nmap scan on the target."""
    try:
        logger.info(f"Running Nmap scan on {target}")
        command = f"nmap -Pn -p- {target}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout
        logger.info(f"Nmap output (truncated): {output[:200]}")
        return output
    except Exception as e:
        logger.error(f"Nmap scan error: {e}")
        return f"Error: {e}"

def run_gobuster(target: str) -> str:
    """Execute a Gobuster scan to discover directories on the target."""
    try:
        logger.info(f"Running Gobuster scan on {target}")
        command = f"gobuster dir -u http://{target} -w /usr/share/wordlists/dirb/common.txt"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout
        logger.info(f"Gobuster output (truncated): {output[:200]}")
        return output
    except Exception as e:
        logger.error(f"Gobuster scan error: {e}")
        return f"Error: {e}"

# ---------------------------
# CyberAgent Class Definition
# ---------------------------
class CyberAgent:
    def __init__(self, initial_target: str):
        self.initial_target = initial_target
        self.tasks = []      # List to hold tasks
        self.results = {}    # Dictionary to hold results per task
        self.setup_scope()
        self.setup_initial_tasks()
    
    def setup_scope(self):
        """Log the allowed scope."""
        logger.info(f"Allowed domains: {ALLOWED_DOMAINS}")
    
    def setup_initial_tasks(self):
        """
        Break down the high-level instruction into tasks.
        For the instruction: "Scan google.com for open ports and discover directories"
        we create an initial Nmap task. The Gobuster task is added dynamically.
        """
        if not is_in_scope(self.initial_target):
            logger.error("Target out of scope!")
            sys.exit(1)
        self.tasks.append({
            'tool': 'nmap',
            'target': self.initial_target,
            'retries': 3,
            'description': 'Run Nmap scan'
        })
    
    def run(self):
        """Process the tasks sequentially until completion."""
        while self.tasks:
            task = self.tasks.pop(0)
            logger.info(f"Executing task: {task['description']} on {task['target']}")
            output = self.execute_task_with_retries(task)
            self.results[task['description']] = output
            
            # Dynamically add new tasks based on scan results.
            if task['tool'] == 'nmap':
                # Example: If port 80 is found open, add a Gobuster task.
                if "80/tcp open" in output:
                    logger.info("Port 80 is open. Adding Gobuster task to discover directories.")
                    self.tasks.append({
                        'tool': 'gobuster',
                        'target': task['target'],
                        'retries': 3,
                        'description': 'Run Gobuster scan for directories'
                    })
            # Further dynamic task management can be implemented here.
        
        self.generate_report()

    def execute_task_with_retries(self, task: dict) -> str:
        """Execute a task and retry upon failure up to a defined limit."""
        retries = task.get('retries', 3)
        for attempt in range(1, retries + 1):
            logger.info(f"Attempt {attempt} for task: {task['description']}")
            if task['tool'] == 'nmap':
                output = run_nmap(task['target'])
            elif task['tool'] == 'gobuster':
                output = run_gobuster(task['target'])
            else:
                output = "Unknown tool"
            if "Error" not in output:
                logger.info(f"Task '{task['description']}' succeeded.")
                return output
            else:
                logger.warning(f"Task '{task['description']}' failed on attempt {attempt}. Retrying...")
                time.sleep(2)
        logger.error(f"Task '{task['description']}' failed after {retries} attempts.")
        return f"Failed after {retries} attempts."

    def generate_report(self):
        """Generate a JSON report of all executed tasks and their outputs."""
        report = {
            'results': self.results,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        report_file = f"cyber_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=4)
        logger.info(f"Final report generated: {report_file}")

# ---------------------------
# Main Execution
# ---------------------------
def main():
    # For demonstration, we set the target to "google.com".
    # In practice, you could obtain this from user input or a frontend.
    initial_target = "google.com"
    agent = CyberAgent(initial_target)
    agent.run()

if __name__ == '__main__':
    main()

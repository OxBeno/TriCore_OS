#!/usr/bin/env python3
import subprocess
import os
from typing import Union
import requests
import sys
import json
import google.generativeai as genai
import sys

# This is the API endpoint for the Gemini 2.5 Flash model
API_KEY = "YOUR_API_KEY"

# إعداد المكتبة
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


DEFAULT_SYSTEM_PROMPT = (
    "You are an expert on Linux, bash, and zsh shell commands. "
    "Your sole purpose is to receive a natural language query and return "
    "ONLY the single, most appropriate shell command. "
    "Do not provide any explanation, markdown, code blocks, or any text "
    "other than the command itself. "
    "If the request is ambiguous, dangerous, or cannot be fulfilled, "
    "return a comment starting with #: \n# Cannot fulfill request."
)

def run_data_analysis_agent(file_path): #this is usless for now
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."

    if not file_path.lower().endswith('.csv'):
        return f"Error: File '{file_path}' is not a CSV file."

    eda_final_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EDA_final.py')
    
    if os.path.exists(eda_final_path):
        try:
            result = subprocess.run(
                [sys.executable, eda_final_path, file_path],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                return f"Data analysis completed successfully for file: {file_path}\n{result.stdout}"
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Analysis timed out (10 minute limit)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return f"Error: 'EDA_final.py' not found in the current directory."

def run_security_monitor():
    """Run security monitoring - placeholder for future implementation"""
    return "# Security monitor received request.\n# Note: Security monitoring features are under development.\n# This is a placeholder for future security features."


def get_shell_command(query, system_prompt_override=None):
 
    if query.strip() == "run quick scan":
        return run_security_monitor()

    #set the system prompt
    current_system_prompt = system_prompt_override if system_prompt_override else DEFAULT_SYSTEM_PROMPT

    try:
        #start the model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=current_system_prompt
        )

        response = model.generate_content(query)
        
        #clean the response
        command = response.text.strip()
        command = command.replace("```powershell", "").replace("```bash", "").replace("```", "").strip()
        
        return command

    except Exception as e:
        return f"# Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_query = input("Enter your query: ")
        command_output = get_shell_command(test_query)
        print(f"Query: {test_query}\nCommand: {command_output}")
    else:
        user_query = " ".join(sys.argv[1:])
        command = get_shell_command(user_query)
        print(command)














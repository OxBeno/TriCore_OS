import subprocess
import os
from typing import Union
import requests
import sys
import json

# This is the API endpoint for the Gemini 2.5 Flash model
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key="

API_KEY = "AIzaSyBWHGGVBR4zNMro603V-UfddGHMqJjk5yw"

# This system prompt is CRITICAL.
# It tells the AI to ONLY return a shell command.
# (ده البرومبت الديفولت)
DEFAULT_SYSTEM_PROMPT = (
    "You are an expert on Linux, bash, and zsh shell commands. "
    "Your sole purpose is to receive a natural language query and return "
    "ONLY the single, most appropriate shell command. "
    "Do not provide any explanation, markdown, code blocks, or any text "
    "other than the command itself. "
    "If the request is ambiguous, dangerous, or cannot be fulfilled, "
    "return a comment starting with #: \n# Cannot fulfill request."
)

def run_data_analysis_agent(file_path):
    """(ملحوظة: الوظيفة دي مبقاش ليها استخدام مباشر من هنا، بس هنسيبها)"""
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

# --- (*** التعديل هنا ***) ---
def get_shell_command(query, system_prompt_override=None):
    """
    Calls the Gemini API to get a shell command or an explanation.
    (جديد) بيستقبل برومبت مخصوص لو موجود
    """
    
    # --- (جديد) تحديد البرومبت اللي هيتبعت ---
    if system_prompt_override:
        current_system_prompt = system_prompt_override
    else:
        current_system_prompt = DEFAULT_SYSTEM_PROMPT

    # --- (*** تم الحذف ***) ---
    # (تم شيل الكود القديم بتاع "make data analysis" لأن الـ GUI هو اللي بقى مسؤول عن ده)
    # if query.startswith('make data analysis '):
    #     ...
        
    # (جديد) لو الكويري هي "run quick scan" (بتاعة زرار السيكيورتي)
    if query == "run quick scan":
        return run_security_monitor()

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [{"text": query}]
            }
        ],
        "systemInstruction": {
            # (جديد) استخدم البرومبت اللي اتحدد
            "parts": [{"text": current_system_prompt}]
        }
    }

    try:
        response = requests.post(f"{API_URL}{API_KEY}", headers=headers, data=json.dumps(payload), timeout=10)

        if response.status_code != 200:
            return f"# Error: API request failed with status {response.status_code}\n# {response.text}"

        response_json = response.json()

        if (
            "candidates" in response_json and
            len(response_json["candidates"]) > 0 and
            "content" in response_json["candidates"][0] and
            "parts" in response_json["candidates"][0]["content"] and
            len(response_json["candidates"][0]["content"]["parts"]) > 0 and
            "text" in response_json["candidates"][0]["content"]["parts"][0]
        ):
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "# Error: Could not parse AI response."

    except requests.exceptions.RequestException as e:
        return f"# Error: Network request failed: {e}"
    except Exception as e:
        return f"# Error: An unexpected error occurred: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_query = input("Enter your query: ")
        command_output = get_shell_command(test_query)
        print(f"Query: {test_query}\nCommand: {command_output}")
    else:
        user_query = " ".join(sys.argv[1:])
        command = get_shell_command(user_query)
        print(command)

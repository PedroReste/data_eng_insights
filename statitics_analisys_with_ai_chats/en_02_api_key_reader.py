# api_key_reader.py
import os
from typing import Optional

def read_api_key_from_file(file_path: str) -> Optional[str]:
    """
    Read API key from text file with format 'open_router:api_key_here'
    
    Args:
        file_path (str): Path to the API key file
    
    Returns:
        str: API key or None if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            
            # Handle different possible formats
            if content.startswith('open_router:'):
                return content.split('open_router:')[1].strip()
            elif ':' in content:
                return content.split(':', 1)[1].strip()
            else:
                return content.strip()
                
    except FileNotFoundError:
        print(f"❌ API key file not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading API key: {e}")
        return None

def read_api_key_from_content(file_content: str) -> Optional[str]:
    """
    Read API key from file content string
    
    Args:
        file_content (str): Content of the API key file
    
    Returns:
        str: API key or None if not found
    """
    try:
        content = file_content.strip()
        
        # Handle different possible formats
        if content.startswith('open_router:'):
            return content.split('open_router:')[1].strip()
        elif ':' in content:
            return content.split(':', 1)[1].strip()
        else:
            return content.strip()
            
    except Exception as e:
        print(f"❌ Error parsing API key: {e}")
        return None

def get_api_key_from_env() -> Optional[str]:
    """
    Get API key from environment variable
    
    Returns:
        str: API key or None if not found
    """
    return os.getenv('OPENROUTER_API_KEY')
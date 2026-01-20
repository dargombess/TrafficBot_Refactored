"""
config_saver.py - Save Config to File (Persistent Storage)
"""

import os
from datetime import datetime


def save_config_to_file(config_module):
    """
    Save current config values to bot_config.py file
    """
    config_file = "bot_config.py"
    
    # Backup original file first
    if os.path.exists(config_file):
        backup_file = f"bot_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[BACKUP] Config saved to: {backup_file}")
    
    # Read current file
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get all config attributes
    config_vars = {k: v for k, v in vars(config_module).items() 
                   if not k.startswith('_') and k.isupper()}
    
    # Update lines
    new_lines = []
    updated_keys = set()
    
    for line in lines:
        # Skip comments and empty lines at start
        if line.strip().startswith('#') or not line.strip():
            new_lines.append(line)
            continue
        
        # Check if line is a config assignment
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            
            if key in config_vars:
                # Update with current value
                value = config_vars[key]
                
                # Format value properly
                if isinstance(value, str):
                    new_line = f'{key} = "{value}"\n'
                elif isinstance(value, bool):
                    new_line = f'{key} = {value}\n'
                elif isinstance(value, (int, float)):
                    new_line = f'{key} = {value}\n'
                elif isinstance(value, dict):
                    new_line = f'{key} = {value}\n'
                elif isinstance(value, list):
                    new_line = f'{key} = {value}\n'
                else:
                    new_line = line  # Keep original if unknown type
                
                new_lines.append(new_line)
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any new config vars that weren't in file
    for key, value in config_vars.items():
        if key not in updated_keys:
            if isinstance(value, str):
                new_lines.append(f'\n{key} = "{value}"\n')
            elif isinstance(value, bool):
                new_lines.append(f'\n{key} = {value}\n')
            elif isinstance(value, (int, float)):
                new_lines.append(f'\n{key} = {value}\n')
            elif isinstance(value, dict):
                new_lines.append(f'\n{key} = {value}\n')
            elif isinstance(value, list):
                new_lines.append(f'\n{key} = {value}\n')
    
    # Write back to file
    with open(config_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"[SAVE] Config saved to {config_file}")
    return True


def get_config_summary(config_module):
    """Get summary of current config"""
    summary = []
    config_vars = {k: v for k, v in vars(config_module).items() 
                   if not k.startswith('_') and k.isupper()}
    
    for key, value in sorted(config_vars.items()):
        if isinstance(value, str) and len(value) > 50:
            summary.append(f"{key} = {value[:47]}...")
        else:
            summary.append(f"{key} = {value}")
    
    return "\n".join(summary)

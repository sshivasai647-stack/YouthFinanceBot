import os

def generate_tree(startpath, exclude_dirs):
    with open("project_structure.txt", "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(startpath):
            # Ignore hidden directories and specific folders
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f'{indent}{os.path.basename(root)}/\n')
            
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                # Ignore python cache files and the script itself
                if not file.endswith('.pyc') and file != "get_tree.py":
                    f.write(f'{subindent}{file}\n')

# Add any other folders you want to ignore to this list
ignore_list = ['node_modules', '__pycache__', 'venv', 'env', 'build']
generate_tree('.', ignore_list)
print("Done! Open project_structure.txt")
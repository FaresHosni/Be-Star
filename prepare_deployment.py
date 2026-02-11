import os
import zipfile

def zip_project(output_filename="bestar_platform.zip"):
    # Define directories and files to include
    include_roots = ["backend", "frontend"]
    include_files = ["docker-compose.yml"]
    
    # Define exclusions
    excludes = {
        "dirs": ["node_modules", "venv", "__pycache__", ".git", ".idea", ".vscode", "dist", "build"],
        "files": [".DS_Store", "Thumbs.db"]
    }

    print(f"Creating {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add root files
        for file in include_files:
            if os.path.exists(file):
                print(f"Adding {file}")
                zipf.write(file, arcname=file)
        
        # Add directories
        for root_dir in include_roots:
            if not os.path.exists(root_dir):
                print(f"Warning: {root_dir} not found")
                continue
                
            for root, dirs, files in os.walk(root_dir):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in excludes["dirs"]]
                
                for file in files:
                    if file not in excludes["files"] and not file.endswith(".pyc"):
                        file_path = os.path.join(root, file)
                        # Keep the path relative to the project root
                        print(f"Adding {file_path}")
                        zipf.write(file_path, arcname=file_path)

    print(f"Successfully created {output_filename}")

if __name__ == "__main__":
    zip_project()

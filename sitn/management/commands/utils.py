import subprocess
from pathlib import Path

def get_pg_dump_path():
    """
    Checks if pg_dump in PATH, if not, asks for binaries path.
    """
    try:
        result = subprocess.check_output(["pg_dump", "--version"])
        print("pg_dump was successfully found, version:", result.decode().strip())
        return ''
    except FileNotFoundError:
        print("👀 pg_dump not found in PATH!")
        input_path = Path(input("Provide pg_dump folder path:\n"))
        if not Path.is_dir(Path(input_path)):
            print(f"Error, {input_path} is not a folder")
            exit(1)
        return f"{input_path.as_posix()}/"

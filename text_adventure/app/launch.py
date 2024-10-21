import subprocess

# Launch the Python script in a new cmd window on Windows
def main():
    subprocess.Popen(['zsh', '-c', 'python3 app.py'])

if __name__ == "__main__":
    main()

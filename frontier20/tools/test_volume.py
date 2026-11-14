"""Keep only our desktop regression runner's Windows audio session muted."""
from pathlib import Path
import subprocess

def configure(process):
    return subprocess.Popen([
        'powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(Path(__file__).with_name('set_test_volume.ps1')),
        '-TargetProcessId',str(process.pid)],stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)

def verify(helper):
    try:output=helper.communicate(timeout=12)[0].decode('utf8',errors='replace').strip()
    except subprocess.TimeoutExpired:
        helper.terminate();helper.wait(timeout=3)
        raise RuntimeError('Windows test volume helper timed out')
    if helper.returncode:raise RuntimeError('Windows test volume failed: '+output)
    if output:print(output,flush=True)

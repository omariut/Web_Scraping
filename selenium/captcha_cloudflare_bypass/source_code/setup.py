import sys
from cx_Freeze import setup, Executable
import os
os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), "cacert.pem")
# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["undetected_chromedriver", "certifi"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="main",
    version="0.1",
    description="My GUI application!",
    executables=[Executable("main.py", base=base)],
)

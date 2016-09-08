import sys
from cx_Freeze import setup, Executable

setup(
    name="Online Enrollment Statistic Calculator",
    version="2.0",
    description="Online Enrollment Statistic Calculator",
    executables=[Executable("OnlineEnrollmentCalc.py")])

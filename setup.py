import os
import platform

curr_os = platform.platform()
if curr_os.startswith('Windows'):
    os.system('shell/windows.sh')
elif curr_os.startswith('Linux'):
    os.system('shell/linux.sh')
else:
    raise NotImplementedError # LOL

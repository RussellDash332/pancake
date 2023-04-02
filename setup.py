import os
import platform

curr_os = platform.platform()
if curr_os.startswith('Windows'):   os.system('setup/windows.sh')
elif curr_os.startswith('Linux'):   os.system('setup/linux.sh')
else:                               raise NotImplementedError # LOL
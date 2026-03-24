import sys
from subprocess import Popen, PIPE, STDOUT
from io import StringIO

moveServo = './moveServo.sh'
serial = '/dev/ttyACM0'
pos=Popen([moveServo, 'get', serial, '8']).wait()
out = StringIO()
print(int(pos))
for line in pos.stdout:
    if print_output:
        print(line, end='')
    else:
        out.write(line)

pos.stdout.close()
return_code = pos.wait()

if not return_code == 0:
    raise RuntimeError(
        'The process call "{}" returned with code {}. The return code is not 0, thus an error '
        'occurred.'.format(list(command), return_code))

stdout_string = out.getvalue()
out.close()

print(stdout_string)
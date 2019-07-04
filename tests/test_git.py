from sh import git

# print(git.show("HEAD"))
result = git.log('--decorate=no', '-1')
# str = str.encode('utf-8')
result = str(result)
print(result)
# print(git('describe'))

import re
def escape_ansi(line):
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)
    

print(escape_ansi(result))
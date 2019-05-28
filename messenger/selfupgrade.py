import sh
from sh import git
import time
import os, sys
from distutils.dir_util import copy_tree

aggregated = ""

def CheckForUpdate(workingDir):
    print("Fetching most recent code from source..." + workingDir)

    # Fetch most up to date version of code.
    p = git("--git-dir=" + workingDir + ".git/", "--work-tree=" + workingDir, "fetch", _out=None, _out_bufsize=0, _tty_in=True)

    print("Fetch complete.")
    time.sleep(2)
    print("Checking status for " + workingDir + "...")
    statusCheck = git("--git-dir=" + workingDir + ".git/", "--work-tree=" + workingDir, "status")

    if "Your branch is up-to-date" in statusCheck:
        print("Status check passes.")
        print("Code up to date.")
        return False
    else:
        print("Code update available.")
        return True

if __name__ == "__main__":
    from os.path import expanduser
    home = expanduser("~")
    print(home) #user의 home
    
    print(os.getcwd())
    
    
    #TODO 프로그램이 실행된 경로를 찾아서 .. 프로젝트 시작 경로를 찾아서 업데이트하도록 한다
    current_pwd = os.getcwd() + '/'
    backup_path = current_pwd + '/../config_backup_' + 'telegram_id'
    
    # config 폴더를 다른곳에 백업해둔 뒤 업데이트 후 다시 덮어 쓰도록 한다
    copy_tree(current_pwd+'/configs', backup_path)
    
    if CheckForUpdate(current_pwd):
        print("Resetting code...")
        # resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--hard", "origin/dev")
        # resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--soft", "origin/dev")
        # print(str(resetCheck))
        
    copy_tree(backup_path, current_pwd+'/configs')
    
    su = ''
    if(current_pwd.find('/home/pi/') == 0):
        #라즈베리파이로 인식한다
        su = 'sudo '

    pip_command = '{}pip install -U -r requirements.txt'.format(su)
    os.popen(pip_command)
    
    restart_command = '{}kill `cat ./ant.pid` | {}./run.sh'.format(su, su)
    os.popen(restart_command)
    
    
    
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
    #TODO 프로그램이 실행된 경로를 찾아서 .. 프로젝트 시작 경로를 찾아서 업데이트하도록 한다
    gitDir = "/home/pi/Ants-Auto-Trading-Bot/"
    backup_path = '/home/pi/config_backup'
    
    # config 폴더를 다른곳에 백업해둔 뒤 업데이트 후 다시 덮어 쓰도록 한다
    copy_tree(gitDir+'configs', backup_path)
    
    if CheckForUpdate(gitDir):
        print("Resetting code...")
        # resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--hard", "origin/dev")
        resetCheck = git("--git-dir=" + gitDir + ".git/", "--work-tree=" + gitDir, "reset", "--hard", "origin/dev")
        print(str(resetCheck))
        
    copy_tree(backup_path, gitDir+'configs')
    
    
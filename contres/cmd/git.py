import subprocess
import os
from datetime import datetime as dt


def manage_git(args):
    print('No command specified. For help run\ncontres upload -h ')


def git_init(args):
    path = args.path if args.path is not None else os.getcwd()
    repo_url = args.url

    if repo_url is None:
        print('Specify the URL of the remote repository.')
        print('It has to exist and be empty.')
        print('Specify the host, namespace and name like: https://gitlab.com/your_name/project_name')
        while repo_url is None:
            repo_url = input('Base URL : ')

    create_git_repository(path, repo_url=repo_url) 


def check_git_installed():
    try:
        result = subprocess.run(['git', '--version'], capture_output=True)
        if result.stderr != b'':
            raise FileNotFoundError
    except FileNotFoundError:
        return False
    return True

def create_git_repository(path, repo_url=None):
    if not check_git_installed():
        print('Cannot init a git repository. git is not installed.')
        return 

    old_path = os.getcwd()

    # jump into repo root
    os.chdir(path)
    subprocess.run(['git', 'init'])
    if repo_url is not None:
        result = subprocess.run(['git', 'remote', 'add', 'origin', repo_url], capture_output=True)
        if result.stderr != b'':
            print('Error: \n %s\n\nHave you created %s online?' % (result.stderr.decode(), repo_url))
            os.chdir(old_path)
            return
    
    # finished.
    print('Initialized git repository.\nUse git directly or contres git upload to push.')
    os.chdir(old_path)
    

def git_push(args):
    # get the arguments
    add = args.add
    if add is None:
        add = 'all'
    elif 'all' in add or '.' in add:
        add = 'all'
    path = args.path if args.path is not None else os.getcwd()
    message = args.message
    
    # run 
    upload(path, add=add, message=message)


def upload(path, add='all', message=None):
    if not check_git_installed():
        print('Seems like git is not installed.')
        return
    
    if message is None:
        message = "Contres CLI upload %s" % dt.utcnow()

    # add and commit
    if isinstance(all, list):
        cmd = ['git', 'add', *add]
    elif add == 'all' or add == '.':
        cmd = ['git', 'add', '.']
    else:
        cmd = ['git', 'add', add]

    try:
        result = subprocess.run(cmd, capture_output=True)
        if result.stderr != b'':
            raise Exception(result.stderr.decode())
    except Exception as e:
        print('Cannot add files.\n%s' % str(e))
    
    try:
        subprocess.run(['git', 'commit', '-m', '"%s"' % message])
        result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], capture_output=True)
        if result.stderr != b'':
            raise Exception(result.stderr.decode())
    except Exception as e:
        print('Upload failed.\n%s' % str(e))
    print('Upload finished.')


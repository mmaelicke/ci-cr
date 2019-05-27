import os
from contres.config import CI_BACKEND_URL


def _replace(path, source, target):
    with open(path, 'r') as f:
        codetxt = f.read()
    codetxt = codetxt.replace(source, target)
    with open(path, 'w') as f:
        f.write(codetxt)


def _change_file(active, path=None):
    if path is None:
        path = os.getcwd()
    run_path = os.path.join(path, 'run', 'contres.py')
    if not os.path.exists(run_path):
        print('CR folder run not found. Initialize here with:')
        print('contres init')
    else:
        _replace(run_path, 'activated = %s' % (not active), 'activated = %s' % active)
        print('Upload to %s %s' % (
            CI_BACKEND_URL, 
            'activated.' if active else 'deactivated.'
            ))


def activate(args):
    _change_file(True, path=args.path)


def deactivate(args):
    _change_file(False, path=args.path)

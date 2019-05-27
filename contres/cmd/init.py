import os
import shutil
import glob
from ruamel.yaml import YAML
from argparse import Namespace

from contres.config import BASE_PATH, TEMPLATES_FOLDER_NAME, INSTALL_CMD, CI_BACKEND_URL
from contres.cmd._util import welcome, describe
from contres.cmd.git import git_init
from contres import __version__ as VERSION

TEMPLATES_PATH = os.path.join(BASE_PATH, TEMPLATES_FOLDER_NAME)


def init_repository(args):
    # check arguments 
    path = args.path if args.path is not None else os.getcwd()
    if not os.path.exists(path):
        exit("Path %s cannot be found" % path)
    name = args.name
    pre_f = args.pre
    main_f = args.main 
    post_f = args.post

    if all([_ is not None for _ in [name, pre_f, main_f, post_f]]):
        # no need to ask for arguments.
        print('Found config.')
    else:
        # in any other case
        print(welcome())
        print(describe())
    
    # path
    if path == os.getcwd():
        print('Do you want to init in another location?')
        _ = input('PATH [cwd]: ').strip()
        path = path if _ == '' else _
    
    # name
    while name is None:
        _ = input('Project Name: ').strip()
        name = name if _ == '' else _
    
        print('\nYour scripts will be located in %s.' % (os.path.join(path, name)))
        print('Give the relative script names including file extension and arguments if any.')
        print('Example: cleanup.py all')
        print("For a Python script accepting 'all' as argument.\n")
    # pre_f
    if pre_f is None:
        pre_f = input('Preprocessing scirpt call [blank for none]: ').strip()

    # main_f
    while main_f is None or main_f == '':
        main_f = input('Main research script call: ').strip()

    # post_f
    if post_f is None:
        post_f = input('Postprocessing script call [blank for none]: ').strip()
    
    _build_repository(path, name, pre_f, main_f, post_f, args=args)

    # gitlab stuff
    if args.no_gitlab is None or not args.no_gitlab:
        decision = input('Do you want to init git [no/Yes]: ').strip().lower()
        
        if decision is None or decision == 'yes' or decision == 'y':
            _a = Namespace()
            _a.url = args.url
            _a.path = os.path.join(path, name)
            
            git_init(_a)


def _build_repository(path, name, pre=None, main=None, post=None, template='default', args=Namespace()):
    # template folder
    temp_path = os.path.join(TEMPLATES_PATH, template)
    if not os.path.exists(temp_path):
        raise FileNotFoundError('Cannot find a template in %s' % temp_path)
    
    # destination folder
    dest_path = os.path.join(path, name)

    # copy the folder if not exists
    old_wd = os.getcwd()
    os.chdir(temp_path)
    files = glob.glob('**', recursive=True)
    files.extend(['.gitlab-ci.yml', '.cr.yml'])

    # build the folder structure
    if not os.path.exists(dest_path):
        os.makedirs(os.path.join(dest_path))
    if not os.path.exists(os.path.join(dest_path, name)):
        os.makedirs(os.path.join(dest_path, name))
    if not os.path.exists(os.path.join(dest_path, 'run')):
        os.makedirs(os.path.join(dest_path, 'run'))
    for f in files:
        # if file exists, remove it
        if os.path.isfile(f):
            if os.path.exists(os.path.join(dest_path, f)):
                os.remove(os.path.join(dest_path, f))
            shutil.copy2(f, os.path.join(dest_path, f))
        elif os.path.isdir(f) and not os.path.exists(os.path.join(dest_path, f)):
            os.makedirs(os.path.join(dest_path, f))
    os.chdir(old_wd)

    # replace with scripts
    # url in contres
    con_file = os.path.join(dest_path, 'run', 'contres.py')
    with open(con_file, 'r') as f:
        codetxt = f.read()
    # replace url
    codetxt = codetxt.replace('#url = #- URL -#', "url = '%s'" % CI_BACKEND_URL)
    
    # deactivate upload if needed
    if hasattr(args, 'deactivate'):
        codetxt = codetxt.replace('activated = True', 'activated = False')
    
    # replace CLI verison
    codetxt = codetxt.replace("giltlab_meta['cli-version'] = None", "giltlab_meta['cli-version'] = '%s'" % VERSION)
    with open(con_file, 'w') as f:
        f.write(codetxt)

    # main script
    open(os.path.join(dest_path, name, main.split(' ')[0]), 'a').close()
    _replace(os.path.join(dest_path, 'run', 'main.py'), main, projname=name)
    
    # preprocessing script
    if pre is not None and pre != '':
        open(os.path.join(dest_path, name, pre.split(' ')[0]), 'a').close()
        _replace(os.path.join(dest_path, 'run', 'pre.py'), pre, projname=name)

    # postprocessing script
    if post is not None and post != '':
        open(os.path.join(dest_path, name, post.split(' ')[0]), 'a').close()
        _replace(os.path.join(dest_path, 'run', 'post.py'), post, projname=name)

    # finish
    print('Finished.\nCheck repository at: %s\nOnline help: continuous-research.hydrocode.de/help' % dest_path)


def _replace(path, script_call, projname):
    # get the script
    script_call = script_call.split(' ')
    script = './%s/' % projname + script_call[0]
    script_mime = os.path.splitext(script)[1]
    conf_path = os.path.abspath(os.path.join(os.path.dirname(path), '../'))

    # get script type
    if script_mime.lower() == '.py':
        call = ["'python'", "'%s'" % script]
    elif script_mime.lower() == '.r':
        call = ["'Rscript'", "'%s'" % script]
        add_install(conf_path, 'r')
    elif script_mime.lower() == '.m':
        call = ["'octave'", "'%s'" % script]
        add_install(conf_path, 'octave')
    elif script_mime.lower() == '.sh':
        call = ["'%s'" % script]
    elif script_mime.lower() in ('.f90', '.f95', '.f03'):
        call = ["'%s.out'" % os.path.splitext(script)[0]]
        add_install(conf_path, 'fortran', script=script)
    elif script_mime.lower() in ('.f', '.for', 'f77'):
        print('The fixed source form FORTRAN files are not supported.\nYou have to edit .gitlab-ci.yml by hand.')
        call = ["'%s.out'" % os.path.splitext(script)[0]]
        add_install(conf_path, 'fortran', script=script)
    elif script_mime.lower() in ('.c', '.cpp'):
        call = ["'%s.out'" % os.path.splitext(script)[0]]
        add_install(conf_path, 'cpp', script=script)
    else:
        print("'%s' is not a supported file type.\nEdit %s by hand if necessary." % (script_mime, path))
        call = ["'%s'" % script]
    
    # append arguments
    if len(script_call) > 1:
        call.extend(["'{}'".format(_) for _ in script_call[1:]])
    
    # replace the call
    with open(path, 'r') as f:
        code_content = f.read()
    # replace placeholder by script call
    code_content = code_content.replace("'#- nothing to do -#'", ','.join(call))
    # save
    with open(path, 'w') as f:
        f.write(code_content)


def add_install(path, lan, script=None):
    conf = _config(path)
    if lan == 'r':
        if not conf['variables']['R']:
            conf['before_script'].extend(INSTALL_CMD['r']['before_script'])
            conf['variables']['R'] = 1
    elif lan == 'octave':
        if not conf['variables']['OCT']:
            conf['before_script'].extend(INSTALL_CMD['octave']['before_script'])
            conf['variables']['OCT'] = 1
    elif lan == 'fortran':
        if not conf['variables']['FOR']:
            if script is None:
                print('FORTRAN file name not found.')
            else: 
                cmds = INSTALL_CMD['fortran']['before_script']
                cmds[1] = cmds[1].format(**{'source': script, 'output': os.path.splitext(script)[0] + '.out'})
                conf['before_script'].extend(cmds)
            conf['variables']['FOR'] = 1
    elif lan == 'cpp':
        if not conf['variables']['CPP']:
            if script is None:
                print('C/C++ file name not found.')
            else:
                cmds = INSTALL_CMD['cpp']['before_script']
                cmds[1] = cmds[1].format(**{'source': script, 'output': os.path.splitext(script)[0] + '.out'})
                conf['before_script'].extend(cmds)
            conf['variables']['CPP'] = 1
    else:
        print("Language %s not yet supported" % lan)

    # save
    _config(path, config=conf)


def _config(path, config=None):
    if config is None:
        yaml = YAML()
        with open(os.path.join(path, '.gitlab-ci.yml'), 'r') as doc:
            return yaml.load(doc.read())
    else:
        yaml = YAML()
        with open(os.path.join(path, '.gitlab-ci.yml'), 'w') as doc:
            yaml.dump(config, doc)

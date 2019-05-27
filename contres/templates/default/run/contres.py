import os
import requests
import subprocess
import platform
import json
import glob

from .main import args as main_args

args = ['echo']


def _gitlab_meta():
    vs = os.environ
    # project info
    commit = dict(
        sha=vs.get('CI_COMMIT_SHA'),
        id=vs.get('CI_COMMIT_SHORT_SHA'),
        title=vs.get('CI_COMMIT_TITLE'),
        message=vs.get('CI_COMMIT_MESSAGE')
    )
    
    job = dict(
        title=vs.get('CI_JOB_NAME'),
        stage=vs.get('CI_JOB_STAGE'),
        url=vs.get('CI_JOB_URL'),
        pipeline=vs.get('CI_PIPELINE_URL'),
        results=glob.glob('results/**')
    )
    
    project=dict(
        url=vs.get('CI_PROJECT_URL'),
        visibility=vs.get('CI_PROJECT_VISIBILTY'),
        name=vs.get('CI_PROJECT_NAME'),
        namespace=vs.get('CI_PROJECT_NAMESPACE')
    )
    
    author=dict(
        name=vs.get('GITLAB_USER_NAME'),
        login=vs.get('GITLAB_USER_LOGIN'),
        email=vs.get('GITLAB_USER_EMAIL')
    )
    
    meta = dict(
        commit=commit,
        job=job,
        project=project,
        author=author,
        gitlab_version=vs.get('CI_GITLAB_VERSION')
    )
    
    return meta


def _py_meta():
    meta = dict(
        pyversion = platform.python_version(),
        os=platform.system(),
        architecture=platform.architecture()[0],
        os_name=platform.platform(),
        os_version=platform.version(),
        processor=platform.processor()
    )
    
    return meta


def _main_meta():
    d = dict()

    # check if Rscript, python or octave is used
    # todo: add more here as needed
    # todo, get rid of this construct somehow.
    if main_args[0].lower() in ('r', 'python', 'octave'):
        main_mime = os.path.splitext(main_args[1])[1]
        d['main_script_name'] = main_args[1]
    else:
        main_mime = os.path.splitext(main_args[0])[1]
        d['main_script_name'] = main_args[0]
    d['main_script_mime'] = main_mime

    if main_mime == '.py':
        # get dependenties
        res = subprocess.run(['pip', 'freeze'], capture_output=True)
        deps = res.stdout.decode().split('\n')[:-1]
        d['environment'] = deps
    else:
        d['message'] = "Cannot load dependecies for '%s' files." % main_mime
    
    return d

def _load_config():
    meta = dict(
    )
    
    return meta


def __read_logfile(fname):
    try:
        with open(fname, 'r') as log:
            return log.read()
    except FileNotFoundError:
        return '%s not found' % fname


def build_metadata():
    gitlab_meta = _gitlab_meta()
    runner_meta = _py_meta()
    main_meta = _main_meta()
    conf = _load_config()
    
    # update gitlab_meta with config
    gitlab_meta.update(conf)
    gitlab_meta['os'] = runner_meta
    gitlab_meta['script'] = main_meta

    # build a project slug
    name=os.environ.get('CI_PROJECT_NAME', 'contres'),
    namespace=os.environ.get('CI_PROJECT_NAMESPACE', 'foobar')
    gitlab_meta['slug'] = '%s/%s' % (name, namespace)
    giltlab_meta['cli-version'] = None
    
    # load log files
    pre_log = __read_logfile('results/%s_preprocessing.log' % uid)
    main_log = __read_logfile('results/%s_main.log' % uid)
    post_log = __read_logfile('results/%s_postprocessing.log' % uid) 
    
    # add log files
    gitlab_meta['commit']['preprocessingLog'] = pre_log
    gitlab_meta['commit']['mainLog'] = main_log
    gitlab_meta['commit']['postprocessingLog'] = post_log
    
    return gitlab_meta
    

if __name__=='__main__':
    activated = True
    # get uid
    with open('.id', 'r') as f:
        uid = f.read()
        
    print('-' * 40)
    print('Contres making your research awesome..')
    print('UID: #%s' % uid)
    print('-' * 40)
    
    subprocess.run(args)
    print('Finished.')
    
    # build metadata
    print('Colleting Metadata...')
    meta = build_metadata()
    print('sending')
    with open('results/transmitted_metadata.json', 'w') as f:
        json.dump(meta, f, indent=4)

    if activated:
        url = ''
        #url = #- URL -#
        response = requests.put(url, json=meta)
        print('[%d]: %s' % (response.status_code, response.content))
    else:
        print('\n\nThe upload is not activated yet.\nRun contres activate')
        print('\n\n', meta)
    print('Done.')

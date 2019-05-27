import os

CI_BACKEND_URL = 'http://cr-backend-dev.eu-central-1.elasticbeanstalk.com/upload/v1'
TEMPLATES_FOLDER_NAME = 'templates'
BASE_PATH = os.path.dirname(__file__)
VERSION = '0.1'
INSTALL_CMD = dict(
    py=dict(
        before_script=[
            'python --version'
        ]
    ),
    r=dict(
        before_script=[
            'apt-get install -y r-base build-essential',
            'Rscript --version'
            ]
    ),
    octave=dict(
        before_script=[
            'apt-get install -y octave', 
            'apt-get install octave-control octave-image octave-io octave-optim octave-signal octave-statistics',
            'octave --version'
            ]
    ),
    fortran=dict(
        before_script=[
            'apt-get install -y gfortran',
            'gfortran --version',
            'gfortran {source} -o {output}'
            ]
    ),
    c=dict(
        before_script=[
            'agt-get install -y build-essential',
            'gcc --version',
            'gcc {source} -o {output}'
        ]
    ),
    cpp=dict(
        before_script=[
            'apt-get install -y build-essential',
            'g++ --version',
            'g++ {source} -o {output}'
        ]
    )
)
def describe():
    return """-----------------------------------------------------
This CLI will create a preconfigured folder structure 
for your research. After uploading to a Gitlab 
instance, the work will automatically be registered 
at continuous-research.hydrocode.de.
-----------------------------------------------------

"""


def welcome():
    return "\n  Continuous Research integration CLI\n"


def empty(args):
    print(welcome())
    exit('Nothing to do.\nRun with -h flag to get options.')

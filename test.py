import os

sources = []

def get_files(dir):
    for f in os.listdir(dir):
        if os.path.isdir(dir+'/'+f) and '__init__.py' in os.listdir(dir+'/'+f):
            sources.append(dir+'/'+f)
            get_files(dir+'/'+f)

get_files(os.getcwd())
print [x.replace(os.getcwd(),'') for x in sources]
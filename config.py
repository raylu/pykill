import yaml

from os import path
config_path = path.normpath(path.join(path.dirname(path.abspath(__file__)), 'config.yaml'))

__doc = yaml.load(open(config_path, 'r'))
db = __doc['db']
web = __doc['web']

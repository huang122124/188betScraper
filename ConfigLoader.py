import configparser

config = configparser.RawConfigParser()
config.read('./config.ini')

def get(name):
    return config["default"][name]


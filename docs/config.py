import os
import configparser

config = configparser.ConfigParser()
config.read('config-{}.ini'.format(os.environ['env']))

def getConfig():
    return config

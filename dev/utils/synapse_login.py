"""
Name: synapse_login.py
Description: Create synapse login object for interaction with synapse. 
Contributors: Nicholas Lee
"""

import os
import synapseclient


def main():
    # connecting to synapse
    syn = synapseclient.Synapse()

    # Preset environment variable
    synToken = os.getenv("SYNTOKEN")

    # login
    syn.login(authToken=synToken)

    return syn

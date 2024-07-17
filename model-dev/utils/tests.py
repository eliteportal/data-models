""" Tests to use when changing the data model """

import numpy as np

def unique_index(df): 
    if df.index.is_unique:  # first check
        return True
    else: 
        print('FAIL - Index is not unique')
        return False

def all_attrs_present(df): 
    """ All dependsOn values need to be attributes in the data model """
    dependents = df['DependsOn'].aslist()

    check_attrs = []
    for d in dependents: 
        check_attrs += d.split(",")

def invalid_attr_chars(df): 
    """ special characters are not allowed to be in attributes """
    ...

# each attribute should only be in one module
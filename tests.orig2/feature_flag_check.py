import sys
import os
import json
import traceback

# QUESTION: should we introduce a flag that ignores whether or not the flag is set?
# In other words, do we want to ensure a certain set of account flags is set and, if not,
# cause the test to fail?

def read_file():
    feature_flag_file = os.getenv('FEATURE_FLAG_EXPORT')
    f = open(feature_flag_file)
    data = json.load(f)
    f.close()
    return data

def check_boolean_flag():
    data = read_file()
    # This little nugget returns the calling function.  The calling function
    # should map to a lowercase value of the boolean-controlled account flag.
    calling_function = traceback.extract_stack(None, 2)[0][2]
    flag = calling_function.upper()
    return any(f['flag'] == flag and f['value'] == True for f in data)

def enable_cql_v2():
    return check_boolean_flag()

def allow_team_entities_in_catalog_api():
    return check_boolean_flag()

def enable_ui_editing(entity_type):
    data = read_file()
    return any(f['flag'] == "ENABLE_ENTITY_UI_EDITING" and f['value'][entity_type] == True for f in data)
    #return data['ENABLE_UI_EDITING'][entity_type] == true

#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import pickle
from pathlib import Path

Path.mkdir(Path(r'./obj'),exist_ok=True)
def save_obj(obj, name ):
    
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):

    try:
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        with open('obj/'+ name + '.pkl', 'wb') as f:
            return {}
    except EOFError:
        return {}


import streamlit as st
import re
from uuid import UUID
import numpy as np
import requests


def is_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

def dot_score(a, b):
    return np.asarray(a).astype(np.float32).dot(np.asarray(b).astype(np.float32).T)

with st.sidebar:
    score_threshold = st.number_input('Enter a value between 1 and -1 as score threshold', value=0.75)
    hide_similar = st.selectbox('Hide similar items?', ('Yes','No'), index=1)

input_url = st.text_input(label='Media Item URL or ID', value = '')



if input_url != '':
    if input_url.startswith('http') or input_url.startswith('atium'):
        input_url = re.search(r'(?<=https://).+', input_url)[0]
        media_item_id = input_url.split('/')[2].split('?')[0]

    st.caption('Your media item id:')
    st.write(media_item_id)
    res = requests.post(st.secrets['SEARCH_URL'], json={
        'm':media_item_id, 'k':100
    })
    res.raise_for_status()
    res = res.json()
    assert res['status'] == 'ok'
    last_score = 2
    v = None
    for r in res['result']:
        if hide_similar=='Yes' and r['cos_sim'] / last_score > 0.975:
            pass 
        elif r['cos_sim'] > score_threshold:
            if v is not None:
                similarity_to_previous = dot_score(v, r['vector']).flatten()[0]
            else:
                similarity_to_previous = 1
            if similarity_to_previous < score_threshold:
                break
            v = r['vector']
            st.caption('Cosine similarity to source {:0.3f}; Similarity with last entry {:0.3f}'.format(r['cos_sim'], similarity_to_previous))
            with st.expander(r['title']):
                st.write(r['content'])
            st.write('')
            st.write('')
            last_score = r['cos_sim']
    

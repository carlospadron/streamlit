"""
Streamlit page to display a single DataFrame from the database.
"""

import streamlit as st
import lib


st.title("Single DataFrame")
table = lib.load_data("select * from public.test")
st.dataframe(table)

if st.button("Refresh data"):
    lib.load_data.clear()
    st.rerun()

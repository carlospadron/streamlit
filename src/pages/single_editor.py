"""
Streamlit page for editing and saving a single database table interactively.
"""

import pandas as pd
import streamlit as st
from sqlalchemy import text

import lib


st.title("Single Editor")
table = lib.load_data("select * from public.test")
data: pd.DataFrame = st.data_editor(table, num_rows="dynamic")

if st.button("Save changes"):
    try:
        engine = lib.get_database_engine()
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM public.test;"))
            data.to_sql("test", conn, schema="public", if_exists="append", index=False)
        lib.load_data.clear()
        st.success("Changes saved successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error saving changes: {e}")

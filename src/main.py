
"""
HMLR Data Portal Streamlit App

This module provides the main entry point for the HMLR Data Portal web application.
It sets up the Streamlit page configuration and navigation, and defines the welcome page content.
"""

import streamlit as st

def show_welcome() -> None:
	"""
	Display the welcome message and instructions on the main page.
	"""
	st.markdown(
		"""
		# Welcome to the HMLR Data Portal

		This portal provides access to HMLR data and tools for exploration.

		---

		Use the navigation sidebar to access different features:

		- **Single Editor**: Edit data in a table view.
		- **Single DataFrame**: View data in a read-only table.
		- **Map**: Visualize geospatial data on an interactive map.
		"""
	)

def main() -> None:
	"""
	Configure the Streamlit app and set up navigation between pages.
	"""
	st.set_page_config(page_title="HMLR Data Portal", page_icon=":bar_chart:", layout="centered")

	pg = st.navigation([
		st.Page(show_welcome, title="Welcome"), 
		st.Page("pages/single_dataframe.py", title="Single DataFrame"),
		st.Page("pages/single_editor.py", title="Single Editor"),
		st.Page("pages/dataframe_map.py", title="Map")
	])
	pg.run()

if __name__ == "__main__":
	main()

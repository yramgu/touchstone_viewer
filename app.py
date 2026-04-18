import streamlit as st

from pages.touchstone_viewer import TouchStoneViewer

# ----------------------------------------
# Define mini-tools as functions
# ----------------------------------------

def tool_about():
    st.header("ℹ️ About This App")
    st.write("This is a collection of handy daily tools built in a single Streamlit file.")

# ----------------------------------------
# Create the sidebar menu
# ----------------------------------------

st.sidebar.title("🧰 My Toolkit")
st.sidebar.write("Select a tool below:")

# The selectbox returns the string the user clicked
selected_tool = st.sidebar.radio(
    "Navigation", 
    ["Touchstone Viewer", "About"]
)

# ----------------------------------------
# Route to the correct tool
# ----------------------------------------

if selected_tool == "Touchstone Viewer":
    TouchStoneViewer().run()
elif selected_tool == "About":
    tool_about()


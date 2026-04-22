import streamlit as st

from pages.touchstone_viewer import TouchStoneViewer
from pages.smith_match import RfMatcher
from pages.filter_designer import FilterDesigner
from pages.attenuator_designer import AttenuatorDesigner
from pages.fir_designer import FirDesigner
from pages.link_budget import LinkBudgetCalculator


# ----------------------------------------
# Define mini-tools as functions
# ----------------------------------------

def tool_about():
    st.header("ℹ️ About This App")
    st.write("This is a collection of handy RF tools built in a single Streamlit app.")

# ----------------------------------------
# Create the sidebar menu
# ----------------------------------------

st.sidebar.title("🧰 RF Toolkit")
st.sidebar.write("Select a tool below:")

# The selectbox returns the string the user clicked
selected_tool = st.sidebar.radio(
    "Navigation", 
    ["Touchstone Viewer", "Simple RF Match", "Attenuator Designer",
     "Analog filter designer", "FIR filter designer", "Link Budget", "About"]
)

# ----------------------------------------
# Route to the correct tool
# ----------------------------------------

if selected_tool == "Touchstone Viewer":
    TouchStoneViewer().run()
elif selected_tool == "Simple RF Match":
    RfMatcher().run()
elif selected_tool == "Analog filter designer":
    FilterDesigner().run()
elif selected_tool == "Attenuator Designer":
    AttenuatorDesigner().run()
elif selected_tool == "FIR filter designer":
    FirDesigner().run()
elif selected_tool == "Link Budget":
    LinkBudgetCalculator().run()
elif selected_tool == "About":
    tool_about()
else:
    pass

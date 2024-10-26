from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from langchain.prompts import HumanMessagePromptTemplate
from langchain.prompts import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate
import markdown2
import pdfkit

# ------------------------------------------------ Initial Chain to Generate Outline --------------------------------#


SYSTEM_MESSAGE_GENERATE_OUTLINE = SystemMessagePromptTemplate.from_template(
    """\
Your job now is to compare the pre-earthquake and post-earthquake inspection data for each room and generate a cconcise markdown report. 

I will provide you with the pre-earthquake and post-earthquake data for each room. 

Guidelines to follow : 
- Compare the form values based on room number.
- For each room, provide a detailed analysis of whether the values and estimates are correct or not.
- Highlight any mistakes or inconsistencies found in a very concise manner.

 """
)

HUMAN_MESSAGE_GENERATE_OUTLINE = HumanMessagePromptTemplate.from_template(
    """\
Pre-Earthquake Data : {pre_earthquake_data}
Post-Earthquake Data : {post_earthquake_data}
"""
)
GENERATE_OUTLINE_TEMPLATE = ChatPromptTemplate.from_messages(
    [SYSTEM_MESSAGE_GENERATE_OUTLINE, HUMAN_MESSAGE_GENERATE_OUTLINE]
)


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


chain = GENERATE_OUTLINE_TEMPLATE | llm | StrOutputParser()


def generate_report(pre_earthquake_data, post_earthquake_data):
    report = chain.invoke(
        {
            "pre_earthquake_data": pre_earthquake_data,
            "post_earthquake_data": post_earthquake_data,
        }
    )
    return report


st.title("Damage Estimate Analysis Report Generator")

if "pre_earthquake_data" not in st.session_state:
    st.session_state.pre_earthquake_data = []

if "post_earthquake_data" not in st.session_state:
    st.session_state.post_earthquake_data = []


# Get the PDF buffer


def show_pre_earthquake_form():
    st.subheader("Before Earthquake (Pre-Earthquake Inspection):")
    pre_earthquake_data = {
        "Room_Number": st.selectbox(
            "Room Number", ["Room 1", "Room 2", "Room 3"], key="room_number"
        ),
        "Height_of_the_wall_in_feet": st.number_input(
            "Height of the wall (in feet):", format="%.2f"
        ),
        "Width_of_the_wall_in_feet": st.number_input(
            "Width of the wall (in feet):", format="%.2f"
        ),
        "Thickness_of_the_wall_in_inches": st.number_input(
            "Thickness of the wall (in inches):", format="%.2f"
        ),
        "Any_visible_cracks_or_fractures_on_the_wall?": st.selectbox(
            "Any visible cracks or fractures on the wall?", ["Yes", "No"]
        ),
        "Length_of_any_existing_cracks_in_feet_if_present": st.number_input(
            "Length of any existing cracks (in feet, if present):", format="%.2f"
        ),
        "Width_of_any_existing_cracks_in_inches_if_present": st.number_input(
            "Width of any existing cracks (in inches, if present):", format="%.2f"
        ),
    }
    pre_earthquake_submit = st.button("Submit Pre-Earthquake Data")

    if pre_earthquake_submit:
        st.session_state.pre_earthquake_data.append(pre_earthquake_data)
        st.success("Pre-Earthquake Data Submitted")
        st.rerun()


def show_post_earthquake_form():
    st.subheader("After Earthquake (Post-Earthquake Inspection):")
    post_earthquake_data = {
        "Room_Number": st.selectbox(
            "Room Number", ["Room 1", "Room 2", "Room 3"], key="room_number_2"
        ),
        "Current_height_of_the_wall_in_feet": st.number_input(
            "Current height of the wall (in feet):", format="%.2f", key="height"
        ),
        "Current_width_of_the_wall_in_feet": st.number_input(
            "Current width of the wall (in feet):", format="%.2f"
        ),
        "Current_thickness_of_the_wall_in_inches": st.number_input(
            "Current thickness of the wall (in inches):", format="%.2f"
        ),
        "Total_number_of_new_cracks_in_the_wall": st.number_input(
            "Total number of new cracks in the wall:", format="%d"
        ),
        "Total_length_of_all_cracks_combined_in_feet": st.number_input(
            "Total length of all cracks combined (in feet):", format="%.2f"
        ),
        "Maximum_width_of_any_crack_observed_in_inches": st.number_input(
            "Maximum width of any crack observed (in inches):", format="%.2f"
        ),
    }
    post_earthquake_submit = st.button("Submit Post-Earthquake Data")

    if post_earthquake_submit:
        st.session_state.post_earthquake_data.append(post_earthquake_data)
        st.success("Post-Earthquake Data Submitted")
        st.rerun()


with st.expander("Enter Pre-Earthquake Data"):
    show_pre_earthquake_form()
for index, space in enumerate(st.session_state.pre_earthquake_data):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(space["Room_Number"])
    with col2:
        if st.button(f"Remove Entry {index + 1}", key=f"remove_pre_{index}"):
            st.session_state.pre_earthquake_data.pop(index)
            st.rerun()
with st.expander("Enter Post-Earthquake Data"):
    show_post_earthquake_form()
for index, space in enumerate(st.session_state.post_earthquake_data):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(space["Room_Number"])
    with col2:
        if st.button(f"Remove Entry {index + 1}", key=f"remove_post_{index}"):
            st.session_state.post_earthquake_data.pop(index)
            st.rerun()

if st.button("Compare Data"):
    with st.spinner("Generating Report..."):
        if (
            st.session_state.pre_earthquake_data
            and st.session_state.post_earthquake_data
        ):
            report = generate_report(
                st.session_state.pre_earthquake_data,
                st.session_state.post_earthquake_data,
            )
            st.subheader("Generated Report")
            st.markdown(report)
        else:
            st.warning(
                "Please submit both Pre-Earthquake and Post-Earthquake data before comparing."
            )

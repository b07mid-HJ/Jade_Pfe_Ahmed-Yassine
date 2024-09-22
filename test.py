import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import db
import jwt
import extra_streamlit_components as stx
from langfuse.callback import CallbackHandler
import os
import pickle
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_vector import MultiVectorRetriever
import streamlit as st
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langfuse import Langfuse
import chat
from streamlit_option_menu import option_menu
import tdr
import DocGen
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Jade Software", page_icon=":bar_chart:", layout="wide")

cookie_manager = stx.CookieManager()
# --- DEMO PURPOSE ONLY --- #
placeholder = st.empty()
# ------------------------- #

# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

# Initialize an empty dictionary for usernames
usernames_dict = {}
# Populate the dictionary with usernames and their hashed passwords
for user in users:
    # Assuming user[1] is the username and user[2] is the hashed password
    username = user[1]
    hashed_password = user[2]
    name=user[3]
    
    # Populate the usernames dictionary
    usernames_dict[username] = {'name':name, 'password': hashed_password}

# Now, structure the credentials dictionary as expected by streamlit_authenticator
credentials = {
    'usernames': 
        usernames_dict
    
}
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)
authenticator = stauth.Authenticate(credentials, "Jade6co", "benchmark-key-2244",cookie_manager)

name, authentication_status, username = authenticator.login()

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    logo = "./assets/jade_advisory_logo-removebg-preview.png"
    st.sidebar.image(logo, width=150)
    if "page" not in st.session_state:
        st.session_state.page="home"

    if st.sidebar.button("Home page"):
        st.session_state.page="home"
    if st.sidebar.button("Chat Assistant"):
        st.session_state.page="chat"
    if st.sidebar.button("Document Generation"):
        st.session_state.page="doc"

    if st.session_state.page=="chat":
        chat.chat(cookie_manager)
    if st.session_state.page=="home":
        tdr.tdr()
    if st.session_state.page=="doc":
        DocGen.full_generation_docx()
    st.sidebar.markdown("""---""")
    authenticator.logout("Logout", "sidebar")
    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
    }
    </style>""", unsafe_allow_html=True)
    
    css = """
    <style>
    div.stButton > button:hover {
        color: rgb(31, 150, 146) !important;
        border-color: rgb(31, 150, 146) !important;
    }
    div.stButton > button:active {
    color: rgb(31, 150, 146) !important;
    border-color: rgb(31, 150, 146) !important;
    background-color: rgb(31, 150, 146) !important;
}
    div.stButton > button:focus {
    color: rgb(31, 150, 146) !important;
    border-color: rgb(31, 150, 146) !important;
}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
    
import streamlit as st

def tdr():
    st.markdown("""
<p align="center" style="color: rgb(31, 150, 146); font-size: 70px;"><strong>Jade Advisory AI Tool</strong></p>
""", unsafe_allow_html=True)
    st.markdown("""---""")
    st.markdown("""

Welcome to the Jade Advisory AI Tool, designed specifically for enhancing productivity and efficiency in handling PPP projects. This tool consists of two main components: the Chat Assistant and the Document Generation Tool.

## 1. Chat Assistant

The Chat Assistant allows you to interact directly with PPP project reports, helping you to extract relevant information quickly and efficiently. You can ask questions in natural language, and the assistant will retrieve the necessary data from the reports.

### Example Questions You Can Ask:
- "what is this project about?"
- "what are the different scenarios?"
- "which scenario is recommended?"
- "why Scenario X is recommended?"
- "what is the equity IRR for scenario X?"
- "give me a summery on the projects sensitivity analysis"

## 2. Document Generation Tool

The Document Generation Tool is designed to process and analyze Excel files to generate detailed PPP project reports. For optimal performance, please ensure that your Excel files adhere to the following rules:

### Excel File Requirements:
- **Format**: Files must be in `.xlsx` or `.xls` format.
- **Structure**: Tables should be clearly defined with headers in the first row; each table should start from a new sheet.
- **Content**: Include only one type of data per table (e.g., financial data, project timelines, stakeholder information).
- **Naming**: Sheets should be named according to the content they contain for easy identification and access by the tool.

### Generating Reports:
Once your Excel file is prepared according to the above guidelines, upload it to the tool. The tool will analyze the tables and generate a comprehensive PPP report, incorporating elements such as financial models, risk assessments, and project timelines.

---

This AI tool aims to streamline your interactions with complex PPP project data, ensuring that you spend less time on data processing and more on strategic decision-making.
""")
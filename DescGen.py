

import os
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

from langchain.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
#from langchain_community.chat_models import ChatOllama

"""
This is the class in wich we will deal with the conversationflow
Objectives :
*************model that understand quantitative data tables*************
*************model that understand the context of the conversation*************
*************model that aware of the history of the conversation*************
*************model that generate a concise description of the table*************
*************model that generate a response that respect the language of the table*************
*************model that minimize the repetition of information from the table itself and hallucination*************
*************Fine tune is the future*************
"""

class descriptionGenerator:
    template = """
    You are an assistant tasked with table analysis.In the context of a Public Private partenership project.\
    the name of the project is : 
    {project}\
    the context is the following:
    {context}\
    Please write a concise description of the table, highlighting the most important aspects of the data.Keep in mind the history of the conversation\
    ** Focus on the key trends, comparisons, or insights revealed by the table.\
    ** Use clear and concise language, avoiding repetition of information from the table itself.\
    *THE RESPONSE SHOULD BE IN ENGLISH.* \
    This is the History of the conversation : 
    {history}\
    
    Conversation:
    Human: The title of this section is : {title}
        Give me a description (paragraph-like) of the table. Table : {table}.\
        keep in mind to {text_input}.\
            
    AI: """
    prompt = PromptTemplate(
        input_variables=["project","context","history", "title" "table" , "text_input"], template=template)
    
    
   

    def __init__(self,context , project):
        os.environ["GOOGLE_API_KEY"]="AIzaSyBqzRiIEfTV-m5qZ1VezYQzKSI07CQz5eU"

        self.model = ChatGoogleGenerativeAI(
                                        model="gemini-pro", 
                                        temperature=0.5, 
                                        convert_system_message_to_human=True
                                    )
       

        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.context = context
        self.project = project
        
      
       

    def predict(self, title,table , text_input , hist):
        summarize_chain = {"title": RunnablePassthrough(),
                           "table":RunnablePassthrough() ,
                            "text_input" : RunnablePassthrough() , 
                            "history" : RunnablePassthrough() ,
                            "context" : RunnablePassthrough(),
                            "project" : RunnablePassthrough()} | self.prompt | self.model | StrOutputParser()
        
        op = summarize_chain.invoke({"title": title,
                                    "table": table ,
                                    "text_input": text_input,
                                    "history": hist,
                                    "context": self.context,
                                    "project": self.project
                                    })

        return op

        



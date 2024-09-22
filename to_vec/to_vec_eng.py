import os
import pickle
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document as dc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
import trans_text
import db
DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/Jade-Chatbot"

model_name = "BAAI/bge-m3"
model_kwargs = {"device": "cpu"}
hf = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs,
)
#model preperation
os.environ["GOOGLE_API_KEY"]="AIzaSyCrmOAFj2bJ12lBeFYBd7UPR00Zt1pvK1I"

model = ChatGoogleGenerativeAI(
                                model="gemini-pro", 
                                temperature=0.5, 
                                convert_system_message_to_human=True
                            )
    
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
from xml.etree.ElementTree import Element, SubElement, tostring
from docx import Document

def table_to_xml(table):
    root = Element('table')
    for row in table.rows:
        row_element = SubElement(root, 'row')
        for cell in row.cells:
            cell_element = SubElement(row_element, 'cell')
            cell_element.text = cell.text.strip()  # Use cell.text directly
    return root

def get_paragraphs_before_tables(doc_path):
    doc = Document(doc_path)
    paragraphs_and_tables = []
    last_paragraph = None 
    for element in doc.element.body:
        if element.tag.endswith('p'):
            last_paragraph = element
        elif element.tag.endswith('tbl'):
            # Find the table object corresponding to this element
            for table in doc.tables:
                if table._element == element:
                    if last_paragraph is not None:
                        xml_root = table_to_xml(table)
                        xml_str = tostring(xml_root, encoding='unicode')
                        langchain_document = "Title: "+ last_paragraph.text + "Content: " + xml_str
                        paragraphs_and_tables.append(langchain_document)
                    break

    return paragraphs_and_tables


directory_path = "./docs/eng"

for docx_file in os.listdir(directory_path):
    if docx_file.endswith(".docx"):
        docx_path = os.path.join(directory_path, docx_file)
        collection_name_prefix = docx_file.split('.')[0]
        print("file started")
        # Example usage:
        table_elements = get_paragraphs_before_tables(docx_path)

        output_dir = f'./chunks/{collection_name_prefix}/'
        os.makedirs(output_dir, exist_ok=True)
        # Prompt
        prompt_text = """You are an assistant tasked with summarizing tables.\ 
        Summerize it and keep the most important information.
        Also you must put the title at the beginning of the summary. \
        If you encounter any table name that has Sc. that means it's a senario \
        The summery should always be translated to english \
        *YOU MUST TRANSLATE THE SUMMERY TO ENGLISH* \
        Give a summary of the table. Table chunk: {element} """
        prompt = ChatPromptTemplate.from_template(prompt_text)

        # Summary chain
        summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

        tables = table_elements
        table_summaries = summarize_chain.batch(tables, {"max_concurrency": 5})
        print("summeries done")

        # The vectorstore to use to index the child chunks
        vectorstore1 = PGVector(
            collection_name=f"{collection_name_prefix}: table_summaries",
            connection_string=DATABASE_URL,
            embedding_function=hf,
            pre_delete_collection = True
        )

        # The storage layer for the parent documents
        store1 = InMemoryStore()
        id_key1 = "doc_id"

        # The retriever (empty to start)
        retriever1 = MultiVectorRetriever(
            vectorstore=vectorstore1,
            docstore=store1,
            id_key=id_key1,
        )


        # Add tables
        table_ids = [str(uuid.uuid4()) for _ in tables]
        summary_tables = [
            dc(page_content=s, metadata={id_key1: table_ids[i]})
            for i, s in enumerate(table_summaries)
        ]
        retriever1.vectorstore.add_documents(summary_tables)
        retriever1.docstore.mset(list(zip(table_ids, tables)))
        with open(f'./chunks/{collection_name_prefix}/store1.pkl', 'wb') as f:
            pickle.dump(store1, f)
        print("table vec done")
        # Text Retrieval
        state_of_the_union = trans_text.extract_text_from_docx(docx_path)

        #text spliter
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=3500,
            chunk_overlap=0 ,
            separators=["\n\n","\n", " ",""],
        )

        texts = text_splitter.create_documents([state_of_the_union])
        vectorstore2 = PGVector(
            collection_name=f"{collection_name_prefix}: child_chunks",
            connection_string=DATABASE_URL,
            embedding_function=hf,
            pre_delete_collection = True
        )
        print("extraction done")
        # The storage layer for the parent documents
        store2 = InMemoryStore()
        id_key2 = "doc_id"
        # The retriever (empty to start)
        retriever2 = MultiVectorRetriever(
            vectorstore=vectorstore2,
            byte_store=store2,
            id_key=id_key2,
        )

        doc_ids = [str(uuid.uuid4()) for _ in texts]

        child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

        sub_docs = []
        for i, doc in enumerate(texts):
            _id = doc_ids[i]
            _sub_docs = child_text_splitter.split_documents([doc])
            for _doc in _sub_docs:
                _doc.metadata[id_key2] = _id
            sub_docs.extend(_sub_docs)

        retriever2.vectorstore.add_documents(sub_docs)
        retriever2.docstore.mset(list(zip(doc_ids, texts)))

        with open(f'./chunks/{collection_name_prefix}/store2.pkl', 'wb') as f:
            pickle.dump(store2, f)
        print("text vec done")
        db.insert_doc(collection_name_prefix)
import logging
from haystack.nodes import TextConverter, PDFToTextConverter, DocxToTextConverter, PreProcessor
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.utils import convert_files_to_docs
import pickle
import os
from src import data_normalization, config

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)


def get_documents_from_dir (doc_dir = "None", company = "None"):
    """
    Retrieves a list of documents from a directory and performs necessary preprocessing.
    Args:
    - doc_dir (str): Path of the directory containing the documents.
    - company (str): Name of the company associated with the documents.
    Returns:
    - all_docs (list): List of processed documents.

    """
    all_docs = []
    documents = convert_files_to_docs(dir_path=doc_dir, split_paragraphs=True, clean_func = data_normalization.clean_func)
    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=False,
        split_by="word",
        split_length=200,
        split_respect_sentence_boundary=True,
    )
    docs_prep = preprocessor.process(documents)
    for doc in docs_prep:
        file_name = os.path.basename(doc.meta["name"])
        file_parts = file_name.split("_")
        year = file_parts[2].split(".")[0]

        doc.meta["company"] = company
        doc.meta["year"] = year
        doc.meta["filename"] = file_name

    all_docs = all_docs + docs_prep
    return all_docs


def get_documents (doc_dir = "Data"):
    """
    Transform the pdf's that are in the doc_dir folder into json documents with normalized and clean text.
    Args:
        - doc_dir: str : directory where the pdf files are located, organized by company
    Returns:
        -list(Document): list of standard and clean documents
    """
    all_docs = []
    for company in os.listdir(doc_dir):
        path_aux = os.path.join(doc_dir, company)
        documents = convert_files_to_docs(dir_path=path_aux, split_paragraphs=True, clean_func = data_normalization.clean_func)

        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by="word",
            split_length=200,
            split_respect_sentence_boundary=True,
        )
        docs_prep = preprocessor.process(documents)


        for doc in docs_prep:
            doc.company = company

        all_docs = all_docs + docs_prep
    return all_docs



def write_documents (documents):
    """
    Writes a list of documents to an Elasticsearch document store.
    Args:
    - documents (list): List of documents to be written.
    Returns:
    - True (bool): Indicates that the documents were successfully written.
    """
    document_store = ElasticsearchDocumentStore(
        host=config.ELASTICSEARCH_HOST,
        username="",
        password="",
        index="document"
    )
    document_store.write_documents(documents)
    return True

def delete_documents ():
    """
    Deletes all documents from an Elasticsearch document store.
    Returns:
    - True (bool): Indicates that the documents were successfully deleted.
    """
    document_store = ElasticsearchDocumentStore(
        host=config.ELASTICSEARCH_HOST,
        username="",
        password="",
        index="document"
    )
    document_store.delete_documents()
    return True

def read_load_documents (initialPath = None, 
                        pathPick = None,
                        saveToPick = False,
                        pathTxt = None,
                        saveToTxt = False,
                        saveToElasticSearch = False,
                        limit = 10,
                        skip = 0,
                        usingTop = False,
                        companiesTop = None
                         ):
    """
    Reads and loads documents from a specified directory, performs processing, and optionally saves them to different formats or Elasticsearch.

    Args:
    - initialPath (str): Path to the initial directory containing company folders.
    - pathPick (str): Path to the directory where pickled files will be saved.
    - saveToPick (bool): Whether to save documents as pickled files.
    - pathTxt (str): Path to the directory where text files will be saved.
    - saveToTxt (bool): Whether to save documents as text files.
    - saveToElasticSearch (bool): Whether to save documents to Elasticsearch.
    - limit (int): Maximum number of companies to process.
    - skip (int): Number of companies to skip.
    - usingTop (bool): Whether to use a list of specific companies to process instead of paginating through all companies.
    - companiesTop (list): List of specific companies to process if usingTop is True.

    Returns:
    - folderProcessed (list): List of processed company folders.

    """
    folderProcessed = []
    companies = os.listdir(initialPath)

    if not usingTop:
        paginated_items = companies[skip : skip + limit]
    else:
        paginated_items = companiesTop

    for company in paginated_items:
        try:
            path_aux = os.path.join(initialPath, company)
            print("Generating documents:",path_aux)
            
            documents = get_documents_from_dir(doc_dir=path_aux, company = company)

            if saveToElasticSearch:
                print("Saving to Elastic Search")
                write_documents (documents)

            if saveToPick:
                print("Saving to pkl file")
                filename = company+".pkl"
                with open(os.path.join(pathPick, filename), "wb") as file:
                    pickle.dump(documents, file)
            if saveToTxt:
                print("Saving to txt file")
                filename = company+".txt"
                with open(os.path.join(pathTxt, filename), "w") as file:
                    file.write(str(documents))

            folderProcessed.append(company)
            documents.clear()
            
        except Exception as e:
            print(str(e))
        finally:
            pass
            #documents.clear()

    return folderProcessed

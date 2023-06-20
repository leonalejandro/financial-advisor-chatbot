import multiprocessing
import logging
import glob
import os
from typing import Dict
#from src.transform import convert_file, preprocess_doc

def index_doc(pdf_doc: Dict[str, str]) -> bool:
    """Process and index a pdf document into elasticsearch
    Args:
        pdf_doc (Dict[str, str]): Document to index
    """
    doc = convert_file(pdf_doc["path"])
    if doc:
        doc.meta["company"] = pdf_doc["company"]
        doc.meta["year"] = pdf_doc["year"]
        doc.meta["filename"] = pdf_doc["filename"]
        doc = preprocess_doc(doc)
        logging.info(f"Indexing {len(doc)} documents")
        #document_store.write_documents(doc)
        return True
    else:
        return False

class Indexer(multiprocessing.Process):
    def __init__(self, connection):
        self.is_alive = True
        self.connection = connection
        multiprocessing.Process.__init__(self)

    def run(self):
        logging.info("Waiting for files to be downloaded")

        while self.is_alive:
            pdf_doc = self.connection.recv()

            #path = "./dataset/**/*.pdf"
            path = "./dataset/**/*.pdf"
            self.is_alive = bool(pdf_doc) ^ (len(glob.glob("./dataset/**/*.pdf")) == 0)
            if pdf_doc:
                doc_indexed = index_doc(pdf_doc)
                if doc_indexed:
                    logging.info(
                        f'Indexed processed document with path: {pdf_doc["path"]}'
                    )
        else:
            self.connection.close()
            logging.info("Conectionn closed")
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from src.BM25RetrieverRanker import BM25RetrieverRanker
from haystack.nodes import PromptNode, PromptTemplate
from haystack.pipelines import Pipeline

from src import config

document_store = ElasticsearchDocumentStore(
    host=config.ELASTICSEARCH_HOST,
    username="",
    password="",
    index="document"
)

def get_predictions (model, query = "None", top_retriever = 5, top_reader = 5):
    """
    Retrieves predictions from a model given a query, using both a retriever and a reader.

    Args:
    - model: The model used for prediction.
    - query (str): The query or question for which predictions are generated.
    - top_retriever (int): The number of retriever results to consider.
    - top_reader (int): The number of reader results to consider.

    Returns:
    - prediction: The prediction generated by the model.

    """
    prediction = model.run(
        query=query, params={"Retriever": {"top_k": top_retriever}, "Reader": {"top_k": top_reader}}
    )
    return prediction

def load_model_retrieve_reader():
    """
    Loads and configures a retriever and reader model for question answering.

    Returns:
    - model_reader: A configured model pipeline for question answering.

    """
    retrieverEmb = EmbeddingRetriever(
        document_store=document_store, 
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    retrieverEmb = EmbeddingRetriever(
        document_store=document_store, 
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
    model_reader = Pipeline()
    model_reader = ExtractiveQAPipeline(reader, retrieverEmb)
    return model_reader


def load_model_gpt():
    """
    Loads and configures a GPT-based model for question answering.

    Returns:
    - model: A configured model pipeline for question answering.

    """
    retrieverGPT = EmbeddingRetriever(
        document_store=document_store,
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
        api_key=config.OPENAI_API_KEY,
    )

    qa_prompt = PromptTemplate(
        name="question-answering",
        prompt_text="""Given the context please answer the question. 
                Your answer should be in your own words and be no longer than 50 words. 
                Context: {join(documents)}; 
                Question:  {query}; 
                Answer:""",
    )

    # Create an instance of PromptNode using ChatGPT API as generator,
    generator = PromptNode(
        "gpt-3.5-turbo",
        api_key=config.OPENAI_API_KEY,
        default_prompt_template=qa_prompt,
        model_kwargs={"stream": True},
    )

    model = Pipeline()
    model.add_node(component=retrieverGPT, name="retriever", inputs=["Query"])
    model.add_node(component=generator, name="generator", inputs=["retriever"])
    return model


def get_output_gpt(model , query = "None", top_retriever = 5):
    """
    Retrieves the output from a GPT-based model given a query.

    Args:
    - model: The GPT-based model used for generating the output.
    - query (str): The query or question for which output is generated.
    - top_retriever (int): The number of retriever results to consider.

    Returns:
    - output: The generated output from the model.

    """
    output = model.run(query=query, params={"retriever": {"top_k": top_retriever}})
    return output['results'][0]


def make_retriever():
    """
    Creates and returns a BM25RetrieverRanker for document retrieval.

    Returns:
    - retriever: A BM25RetrieverRanker object for document retrieval.
    """
    document_store = ElasticsearchDocumentStore(
        host=config.ELASTICSEARCH_HOST,
        username="",
        password="",
        index="document",
    )
    return BM25RetrieverRanker(document_store)



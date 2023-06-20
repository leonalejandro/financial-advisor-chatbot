import boto3
import random
import os
import shutil
from src import config
from random import sample
from collections import Counter

s3 = boto3.resource(
    "s3",
    aws_access_key_id = config.AWS_ACCESS_KEY,
    aws_secret_access_key = config.AWS_SECRET_KEY,
)

def get_filenames_size ():
    """
    Download the contents of a folder directory

    Args:

    Returns:
    -data_dict: dictionary containing the name of the files found in the bucket and their respective weight in bytes
    -total_size: weight in bytes of all files found in bucket
    """
    bucket_name = config.BUCKET_NAME
    prefix = config.PREFIX

    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=prefix)
    
    data_dict = {}
    total_size = 0

    for obj in objects:
        obj_name = obj.key
        obj_size = obj.size
        total_size += obj_size
        data_dict[obj_name] = obj_size
    
    return data_dict, total_size


def get_companies (size = None):

    """
    Obtains companies without repeating the bucket.

    Args:
        - size: int : random number of companies to be returned
    Returns:
        -str[]: list of companies with no repetition
    """

    bucket_name = config.BUCKET_NAME
    prefix = config.PREFIX

    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=prefix)
    
    companies = []
    for obj in objects:
        obj_name = obj.key
        tokens = obj_name.split('/')
        if len(tokens) > 2:
            companies.append(tokens[1])
    
    if size is None:
        return set(companies)
    else:
        return random.sample(list(companies), size)


def get_documents_sample(local_dir=None, sample_size=1):

    """
    Obtains a data sample

    Args:
        - local_dir: str : local directory where files downloaded from s3 will be stored.
        - sample_size: int : number of samples to be downloaded
    Returns:
        
    """

    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)

    bucket_name = config.BUCKET_NAME
    prefix = config.PREFIX
    
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=prefix)
    obj_sample = sample(list(objects), sample_size)
    cont = 0
    for obj in obj_sample:
        cont = cont+1
        target = (
            obj.key
            if local_dir is None
            else os.path.join(local_dir, os.path.relpath(obj.key, prefix))
        )
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue
        bucket.download_file(obj.key, target)
        print("File",target,"Downloaded:",cont)


def  get_top_n_companies(top = 10):

    """Returns the top companies by file count

    Args:
        objects (List[S3Object]): S3 object list
        top (int, optional): number of companies to retrieve. Defaults to 100.

    Returns:
        List[str]: Top company names
    """

    bucket_name = config.BUCKET_NAME
    bucket = s3.Bucket(bucket_name)
    prefix = config.PREFIX
    objects = bucket.objects.filter(Prefix=prefix)

    companies = [
        obj.key.split("/")[1] for obj in objects if len(obj.key.split("/")) > 2
    ]

    company_file_counter = Counter(companies)
    top_companies = company_file_counter.most_common(top)
    return [company[0] for company in top_companies]



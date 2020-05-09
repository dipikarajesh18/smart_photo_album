import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
from elasticsearch import Elasticsearch
from botocore.vendored import requests


es = Elasticsearch("https://vpc-photos-wzuwkc4uurph6brpbrpcgk7bf4.us-west-2.es.amazonaws.com")
# es = Elasticsearch("https://vpc-photos-ri2a5rpbqh7xynn3dwebkbppwq.us-west-2.es.amazonaws.com")

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    return response

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    return search_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def process_in_lex(input):
    client = boto3.client('lex-runtime')
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    response_lex = client.post_text(botName='searchBot', botAlias='$LATEST', userId='user', inputText= input)
    if 'slots' in response_lex:
        keys = [response_lex['slots']['word'],response_lex['slots']['wordtest']]#,response_lex['slots']['keythree']
        return keys
    else:
        return [];
            

def es_search_item(indexname, labels):
    images = []
    for label in labels:
        if label is not None:
            resp = es.search(index=indexname, body={
                "query":{
                    "match": {
                        "labels": label
                    }
                }
            })
            if resp["hits"]["total"]["value"]:
                for item in resp["hits"]["hits"]:
                    images.append(item["_source"]["name"])
    
    return images
    
def lambda_handler(event, context):
    # TODO implement
    print("This is the event from UI",event["queryStringParameters"]["q"])
    input = event["queryStringParameters"]["q"]
    indexname = 'photos'
    labels = process_in_lex(input)
    print("These are the labels : ",labels)
    # labels = ["Person"]
    results = es_search_item(indexname, labels)
    print("These are the results from es : ",results)
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Credentials":True,"Content-Type":"application/json"},
        "body": json.dumps(results)
    }
    

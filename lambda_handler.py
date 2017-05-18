'''

Slack command text to SNS

'''

import os
import logging
import json
import urlparse
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

SNS = boto3.client('sns')

class DecoderError(Exception):
    ''' Exception class for decoder '''
    pass

def flatten_dictionary_array(inp_x):
    ''' flatten a dict of arrays of 1 value to just key, value dict '''
    out_y = {}
    for key in inp_x:
        if len(inp_x[key]) == 1:
            out_y[key] = inp_x[key][0]
    return out_y

def decode_urlencoded(body):
    ''' decode x-www-form-urlencoded '''

    try:
        data = flatten_dictionary_array(urlparse.parse_qs(body, keep_blank_values=True))
    except ValueError:
        raise DecoderError('ERROR:  Can not parse body')
    except TypeError:
        raise DecoderError('ERROR:  Can not parse body')

    return data

def lambda_handler(event, context):
    ''' Entry point for API Gateway '''

    LOGGER.debug('Function ARN: %s', context.invoked_function_arn)

    slackmsg = {}
    try:
        payload = decode_urlencoded(event['body'])

        if 'text' not in payload or payload['text'] is None or payload['text'] == '':
            slackmsg = ':cry: No comments were included! You gotta give me something to work with here!'
        else:
            SNS.publish(
                TopicArn=os.environ.get('SNS-FEEDBACK-ARN'),
                Message=json.dumps(payload),
                Subject='feedback'
            )
            slackmsg = ':ok_hand: Thanks for sharing your message. We\'ll hit you back soon!'

    except DecoderError:
        # Do not ever let them see you sweat
        slackmsg = ':cry: No comments were included! You gotta give me something to work with here!'

    return {
        'statusCode': 200,
        'headers': {'Content-type': 'application/json'},
        'body': json.dumps({'text': slackmsg})
    }

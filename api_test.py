# extract out all csv files in folder, read csv files, use csv inputs to send request to api, take response and compare with input, add new columns in csv


import json
import os
import pandas
import requests
import pytest
import pandas as pd
import numpy as np

import glob

from pandas import DataFrame

payloads = []
response_received = []

for filepath in glob.iglob(r'.\csv\*.csv'):
    #print(filepath)
    print("files analysed: ", filepath)
    status_code_received = []
    response_received = []
    compare_result = []
    payload_values = pd.read_csv(filepath, usecols=['token', 'table', 'text']).replace(np.nan, "")
    # expected_values = pd.read_csv(filepath, usecols=['expected output', 'expected status code'])
    payload_values['table'] = payload_values['table'].apply(lambda x: x.split(","))

    data = pd.DataFrame()
    # Convert CSV data to Json and write to Dataframe created
    data["payload"] = payload_values.apply(lambda x: x.to_json(), axis=1)

    payloads = data.to_numpy()
    df = pd.read_csv(filepath)

    for i in payloads:
        resp = requests.post("http://172.20.192.29/api/v1/sanitise", json=json.loads(i[0]))

        if "text" in resp.json():
            response_output = resp.json()["text"]
        else:
            response_output = resp.json()["error_description"]
        # print(response_output)
        # response_received.append(response_output)
        # status_code_received.append(resp.status_code)
        # #df.assign(**{'response received' : response_received, 'status code received' : status_code_received})
        # print(response_received)
        # print(status_code_received)
        # df_status_code = pd.DataFrame([resp.status_code], columns = ['status code received'])
        # print(df_status_code)
        # # with open(filepath, mode='a') as f:
        # #     df_status_code.to_csv(f, header=f.tell() == 0, index=False)
        # # df_status_code.to_csv(r'filepath', sep=',', index=False)
        # df_status_code.to_csv(r'filepath', mode='a')
        # df = pd.read_csv(filepath)
        # df["received status code"] = resp.status_code
        # df.to_csv(r"filepath", index=False)
        # df_status_code = pd.DataFrame([resp.status_code])
        # print(df_status_code)
        status_code_received.append(resp.status_code)
        response_received.append(response_output)

    df_status_code = DataFrame(status_code_received, columns=['status code received'])
    df_response = DataFrame(response_received, columns=['response received'], )

    if 'expected status code' and 'expected output' in df.columns:
        comparison_column = np.where( (df_response['response received'] == df['expected output']) & (df_status_code['status code received'] == df['expected status code']),['Pass'],['Fail'])
        #print(comparison_column)
        df_compare = DataFrame(comparison_column, columns=['Pass or Fail'])



        df_auto = pandas.concat([df, df_compare], axis=1)
        #print(df_compare)
        if 'Pass or Fail' in df.columns:
            continue
        else:
            df_new_file = pandas.concat([df, df_response, df_status_code, df_compare], axis=1)

            df_new_file.to_csv(filepath, mode='w+', index=False)



    else:
        if 'status code received' and 'response received' in df.columns:
            continue
        else:
            df_new_file = pandas.concat([df, df_response, df_status_code], axis=1)
            df_new_file.to_csv(filepath, mode='w+', index=False)




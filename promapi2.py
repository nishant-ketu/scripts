import requests
import pandas as pd
import re

def sanitize_sheet_name(sheet_name):
    # Replace invalid characters in sheet name
    return re.sub(r'[\/:*?"<>|]', '_', sheet_name)

def query_prometheus_api(query, endpoint):
    response = requests.get(endpoint, params={'query': query})
    response.raise_for_status()
    results = response.json()
    if results and 'data' in results and 'result' in results['data']:
        headers = ["Metric"] + list(results['data']['result'][0]['metric'].keys()) + ["Value"]
        rows = [(entry['metric'].get('__name__', ''), *entry['metric'].values(), entry['value'][1]) for entry in results['data']['result']]
        return pd.DataFrame(rows, columns=headers)

endpoints = ['https://prometheus-dev.aexp.com/prometheus/api/v1/query',
            'https://prometheus.aexp.com/prometheus/api/v1/query']

queries = ['round (  sum  by (function)(increase(platform_level_function_response_code_count{project="one-data"}[24h]))) > 0',]

# Create an Excel writer object
with pd.ExcelWriter('prometheus_results.xlsx') as writer:
    for endpoint in endpoints:
        for query in queries:
            result = query_prometheus_api(query, endpoint)
            if result is not None:
                # Write the results to the Excel sheet
                sanitized_sheet_name = sanitize_sheet_name(f"{endpoint}_{query[:10]}")
                result.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)

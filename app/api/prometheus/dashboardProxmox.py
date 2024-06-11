# app/api/prometheus/dashboardProxmox.py
import requests
from flask import jsonify, current_app

def query_prometheus(query):
    url = f"{current_app.config['PROMETHEUS_URL']}/api/v1/query"
    response = requests.get(url, params={'query': query})
    response.raise_for_status()
    return response.json()

def get_cpu_usage():
    query = 'rate(node_cpu_seconds_total[1m])'
    result = query_prometheus(query)
    return jsonify(result)

def get_memory_usage():
    queries = {
        'total': 'node_memory_MemTotal_bytes',
        'free': 'node_memory_MemFree_bytes',
        'available': 'node_memory_MemAvailable_bytes',
        'buffers': 'node_memory_Buffers_bytes',
        'cached': 'node_memory_Cached_bytes'
    }
    results = {key: query_prometheus(query) for key, query in queries.items()}
    return jsonify(results)

def get_disk_usage():
    queries = {
        'size': 'node_filesystem_size_bytes',
        'free': 'node_filesystem_free_bytes',
        'available': 'node_filesystem_avail_bytes',
        'used': 'node_filesystem_size_bytes - node_filesystem_free_bytes'
    }
    results = {key: query_prometheus(query) for key, query in queries.items()}
    return jsonify(results)

def get_network_usage():
    queries = {
        'receive_bytes': 'rate(node_network_receive_bytes_total[1m])',
        'transmit_bytes': 'rate(node_network_transmit_bytes_total[1m])',
        'receive_errors': 'rate(node_network_receive_errs_total[1m])',
        'transmit_errors': 'rate(node_network_transmit_errs_total[1m])'
    }
    results = {key: query_prometheus(query) for key, query in queries.items()}
    return jsonify(results)

def get_system_load():
    query = 'node_load1'
    result = query_prometheus(query)
    return jsonify(result)

def get_uptime():
    query = 'node_time_seconds - node_boot_time_seconds'
    result = query_prometheus(query)
    return jsonify(result)

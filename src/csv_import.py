#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017  <@ruby.local>
#
# Distributed under terms of the MIT license.

"""

"""
from __future__ import print_function
from HydraLib.PluginLib import JsonConnection
import re
import sys
import os
import datetime

def verify_arguments(argv=None):
    
    if (argv == None) or (len(argv) != 2):
        sys.exit("requires one argument ... the path the csv file")

    return argv[1]

def get_filehandle(filename=None):

    if not filename or not os.path.exists(filename):
        sys.exit("error filename not valid or does not exist")

    fh = open(filename, 'r')
    return fh

def read_csv_header(fh):
    return fh.readline()


def read_csv_body(fh):

    lines = []
    for line in fh:
        lines.append(line)

    fh.close()
    return lines

def create_connection():

    url = "http://localhost:8080"
    return JsonConnection(url)

def get_session_id(conn):

    return conn.login()

def create_project(conn):
    
    proj = dict(
            name = 'CSV Import %s' %(datetime.datetime.now()),
            description = 'Project created via CSV-USGS Import Plugin',
            status = 'A'
            )
    return conn.call('add_project', {'project':proj})

def build_network(project, projection, node_list, link_list):

    description = 'NWIS Sites exported from NWIS Mapper'
    url = 'http://waterdata.usgs.gov/mt/nwis/current?type=flow&group_key=county_cd&format=station_list&station_list_format=xml&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=agency_use_cd'

    network = {}
    network['project_id'] = project['id'] 
    network['projection'] = projection 
    network['nodes'] = build_nodes(node_list)
    network['links'] = build_links(link_list)
    network['scenarios'] = build_scenarios()
    network['name'] = 'NWIS sites'
    network['description'] = str({ 'url': url, 'description': description })

    return network

def build_nodes(raw_nodes=None):

    refined_nodes = []
    if not raw_nodes:
        return refined_nodes

    for raw_node in raw_nodes:
        refined_node = build_node(raw_node)
        if refined_node:
            refined_nodes.append(refined_node)

    return refined_nodes 

def build_node(raw_node):

    raw_node = raw_node.strip('\n')
    
    # the following code is a result of commas being in the midst of
    # the csv strings themselves so a simple split on comma did not work
    elements = []
    pos = 0
    exp = re.compile(r"""(['"]?)(.*?)\1(,|$)""")

    while True:
        match = exp.search(raw_node, pos)
        result = match.group(2)
        separator = match.group(3)
        elements.append(result)
        if not separator:
            break
        pos = match.end(0) 
        
    if len(elements) != 7:
        print(node_elements)

    # todo clean up sloppy code & throw exception if node_elements != 7
    description = {
            'SiteNumber': elements[0],
            'SiteCategory': elements[2],
            'SiteAgency': elements[3],
            'SiteNWISURL': elements[6]
            }
    refined_node = {
            'name': elements[1],
            'x': float(elements[4]),
            'y': float(elements[5]),
            'description': [], # todo replace str(description),
            'attributes' : [],
            }

    return refined_node
    
def build_links(raw_links=None):
    
    return []

def build_scenarios(scenario=None):

    if not scenario or type(scenario) is not dict:
        scenario = {}
        
    scenario['name'] = 'scenario created by import app'
    scenario['description'] = 'standard scenario created by import app'
    scenario['id'] = -1
    scenario['resourcescenarios'] = []

    return scenario


def create_network(conn, network):

    return conn.call('add_network', {'net':network})


if __name__ == '__main__':

    # todo make cmdline arg
    projection = 'EPSG:4326'

    fn = verify_arguments(sys.argv)
    fh = get_filehandle(fn)
    header = read_csv_header(fh)
    node_list = read_csv_body(fh)
    conn = create_connection()
    session_id = get_session_id(conn)

    project_info = create_project(conn)
    network = build_network(project_info, projection, node_list, None)
    network_info = create_network(conn, network)
    print(network_info)


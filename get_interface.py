#! /usr/bin/env python
from pysnmp.entity.rfc3413.oneliner import cmdgen
import re
import json
import pprint

def wsgi_app(environ, start_response):
    if environ['QUERY_STRING'] != '':
        output1 = pprint.pformat(environ['QUERY_STRING'])
        output1 = output1.strip("'")
        output2 = output1.split("&")
        device_ip = "0.0.0.0"
        snmp_community = "public"
        for i in range(0, len(output2)):
            if re.search("IP", output2[i]):
                device_ip = output2[i].split("=")[-1]
            elif re.search("snmp_comm", output2[i]):
                snmp_community = output2[i].split("=")[-1]
            else:
                pass

        errorIndication, errorStatus, errorIndex, \
                 varBindTable = cmdgen.CommandGenerator().nextCmd(\
                 cmdgen.CommunityData('test-agent', snmp_community),\
                 cmdgen.UdpTransportTarget((device_ip, 161)),\
                 '1.3.6.1.2.1.31.1.1.1.1')
        interface_dict = {}
        interface_dict['interface'] = []
        if errorIndication:
            pass
        else:
            if errorStatus:
                print '%s at %s\n' % (\
                    errorStatus.prettyPrint(),\
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?')
                interface_dict = errorStatus.prettyPrint()
            else:
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        temp_val = name._value
                        interfaceindex = temp_val[-1]
                        c_val = ""
                        for key in range(0, len(temp_val)-1):
                            c_val += str(temp_val[key]).strip()+"."
                        temp_val = c_val + str(temp_val[-1]).strip()
                        if re.search("1.3.6.1.2.1.31.1.1.1.1", str(temp_val)):
                            if not re.search("BR", val._value):
                                interface_dict['interface'].append(("IF "+str(interfaceindex)+": "+str(val._value)))

        output = json.dumps(interface_dict)

    # send first header and status
        status = '200 OK'
        headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(output)))]
        start_response(status, headers)
        yield output
    else:
        interface_dict = {}
        interface_dict['interface'] = []
        output = json.dumps(interface_dict)
        status = '200 OK'
        headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(output)))]
        start_response(status, headers)
        yield output

def return_string(d_val):
    val_key = ""
    for key in range(0, len(d_val)-1):
        val_key += str(ord(d_val[key])) + "."
    val_key += str(ord(d_val[-1]))
    return val_key

application = wsgi_app

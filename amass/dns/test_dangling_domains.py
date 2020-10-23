import itertools
import ipaddress
import pytest
import json
import urllib.request


def get_httpbin_ips():
    # IPs we always want to test
    ips = [
        '127.0.0.1',
        '13.58.0.0',
    ]

    req = urllib.request.Request('http://httpbin.org/ip')

    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        ips.append(json.loads(body).get('origin', None))

    return ips


def get_aws_ips():
    req = urllib.request.Request('https://ip-ranges.amazonaws.com/ip-ranges.json')

    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        return json.loads(body)['prefixes']

#
# find domains that have entries that point at non-mozilla ip space
# data sources: amass and/or infoblox? dns server ideally.
#
# will intially have a ton of hits, build whitelist?
#

# @pytest.mark.dangling_domains
# @pytest.mark.parametrize(
#     ['ip', 'aws_ip_ranges'],
#     zip(get_httpbin_ips(), itertools.repeat(get_aws_ips())))
# def test_httpbin_ip_in_aws(ip, aws_ip_ranges):
#     for aws_ip_range in aws_ip_ranges:
#         assert ipaddress.IPv4Address(ip) not in ipaddress.ip_network(aws_ip_range['ip_prefix']), \
#           "{0} is in AWS range {1[ip_prefix]} region {1[region]} service {1[service]}".format(ip, aws_ip_range)

@pytest.mark.amass_dns
def test_dangling_domains():
    assert True == True
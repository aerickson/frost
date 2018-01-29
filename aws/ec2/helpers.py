

def ip_permission_opens_all_ports(ipp):
    """
    Returns True if an EC2 security group IP permission opens all
    ports and False otherwise.

    >>> ip_permission_opens_all_ports({'FromPort': 1, 'ToPort': 65535})
    True
    >>> ip_permission_opens_all_ports({'FromPort': 1, 'ToPort': 965535})
    True
    >>> ip_permission_opens_all_ports({'FromPort': -1, 'ToPort': 20})
    True
    >>> ip_permission_opens_all_ports({'FromPort': 20, 'ToPort': -1})
    True

    >>> ip_permission_opens_all_ports({'ToPort': -1})
    False
    """
    if 'FromPort' not in ipp or 'ToPort' not in ipp:
        return False

    from_port, to_port = ipp['FromPort'], ipp['ToPort']

    # -1 indicates all ICMP/ICMPv6 codes
    if from_port == -1 or to_port == -1:
        return True

    if ipp['FromPort'] <= 1 and ipp['ToPort'] >= 65535:
        return True

    return False


def ip_permission_cidr_allows_all_ips(ipp):
    """
    Returns True if any IPv4 or IPv6 range for an EC2 security group
    IP permission opens allows access to or from all IPs and False
    otherwise.

    >>> ip_permission_cidr_allows_all_ips({'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
    True
    >>> ip_permission_cidr_allows_all_ips({'Ipv6Ranges': [{'CidrIpv6': '::/0'}]})
    True

    >>> ip_permission_cidr_allows_all_ips({'IpRanges': [{'CidrIp': '192.0.1.1/8'}]})
    False
    >>> ip_permission_cidr_allows_all_ips({'Ipv6Ranges': [{'CidrIpv6': '192.0.1.1/8'}]})
    False
    >>> ip_permission_cidr_allows_all_ips({})
    False
    """
    for ip_range in ipp.get('IpRanges', []):
        if ip_range.get('CidrIp', '') == '0.0.0.0/0':
            return True

    for ip_range in ipp.get('Ipv6Ranges', []):
        if ip_range.get('CidrIpv6', '') == '::/0':
            return True

    return False

def ip_permission_grants_access_to_group_with_id(ipp, security_group_id):
    """
    Returns True if an EC2 security group IP permission opens access to
    a security with the given ID and False otherwise.

    >>> ip_permission_grants_access_to_group_with_id(
    ... {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]}, 'test-sgid')
    True
    >>> ip_permission_grants_access_to_group_with_id(
    ... {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]}, 'not-test-sgid')
    False
    >>> ip_permission_grants_access_to_group_with_id({}, 'test-sgid')
    False
    """
    for user_id_group_pair in ipp.get('UserIdGroupPairs', []):
        if user_id_group_pair.get('GroupId', None) == security_group_id:
            return True

    return False


def ec2_security_group_opens_all_ports(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing inbound access on all ports and False otherwise.

    >>> ec2_security_group_opens_all_ports(
    ... {'IpPermissions': [{}, {'FromPort': -1,'ToPort': 65536}]})
    True

    >>> ec2_security_group_opens_all_ports({})
    False
    """
    if 'IpPermissions' not in ec2_security_group:
        return False

    for ipp in ec2_security_group['IpPermissions']:
        if ip_permission_opens_all_ports(ipp):
            return True

    return False


def ec2_security_group_opens_all_ports_to_self(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing all IPs inbound access on all ports and False otherwise.

    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'FromPort': 1, 'ToPort': 65535, 'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]},
    ... ]})
    True

    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_self({'GroupId': 'test-sgid'})
    False
    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'UserIdGroupPairs': []},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_self({})
    False
    >>> ec2_security_group_opens_all_ports_to_self([])
    False
    """
    if 'GroupId' not in ec2_security_group:
        return False

    self_group_id = ec2_security_group['GroupId']

    if 'IpPermissions' not in ec2_security_group:
        return False

    for ipp in ec2_security_group['IpPermissions']:
        if ip_permission_opens_all_ports(ipp) and \
            ip_permission_grants_access_to_group_with_id(ipp, self_group_id):
            return True

    return False


def ec2_security_group_opens_all_ports_to_all(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing all IPs inbound access on all ports and False otherwise.

    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': [
    ... {'FromPort': -1,'ToPort': 65535,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    True
    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': [
    ... {'FromPort': 1,'ToPort': 65535,'Ipv6Ranges': [{'CidrIpv6': '::/0'}]}
    ... ]})
    True

    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': []})
    False
    >>> ec2_security_group_opens_all_ports_to_all({})
    False
    >>> ec2_security_group_opens_all_ports_to_all([])
    False
    """
    if 'IpPermissions' not in ec2_security_group:
        return False

    for ipp in ec2_security_group['IpPermissions']:
        if ip_permission_opens_all_ports(ipp) and ip_permission_cidr_allows_all_ips(ipp):
            return True

    return False


def ec2_security_group_test_id(ec2_security_group):
    """A getter fn for test ids for EC2 security groups"""
    return '{0[GroupId]} {0[GroupName]}'.format(ec2_security_group)

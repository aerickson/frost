def pytest_configure(config):
    # register custom marks for amass services
    for svc_name in [
        "amass_dns",
    ]:
        config.addinivalue_line(
            "markers", "{}: mark tests against {}".format(svc_name, svc_name)
        )

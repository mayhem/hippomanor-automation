import urequests
from net_config import INFLUX_SERVER, INFLUX_PORT, INFLUX_DB


def post_data(data):
    url = "http://" + INFLUX_SERVER + ":" + str(INFLUX_PORT) + "/write?db=" + INFLUX_DB
    print(url)
    print(data)
    response = urequests.post(url, data = data)
    return response.status_code


def post_points(location, points):

    data = b"%s,location=%s" % (location, location)

    for k in points:
        data += (b" %s=%s" % (k, points[k]))

    return post_data(data)

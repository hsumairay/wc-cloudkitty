import decimal


# Price for each flavor. These are equivalent to hashmap field mappings.
flavors = {
    'm1.tiny': decimal.Decimal(0.65),
    'm1.small': decimal.Decimal(0.35),
    'm1.medium': decimal.Decimal(2.67)
}

# Price per MB / GB for images and volumes. These are equivalent to
# hashmap service mappings.
image_mb_price = decimal.Decimal(0.002)
volume_gb_price = decimal.Decimal(0.35)

#price on network services
network_in_price = decimal.Decimal(0.005)
network_out_price = decimal.Decimal(0.006)
network_floating_price = decimal.Decimal(0.007)

# discount percentage as 15%
discount_percentage = 0.85

# discount thresholds quantities

compute_discount_threshold = 2
image_discount_threshold = 512
volume_discount_threshold = 2
floating_discount_threshold = 2

# These functions return the price of a service usage on a collect period.
# The price is always equivalent to the price per unit multiplied by
# the quantity.
def get_compute_price(item):
    if not item['desc']['flavor'] in flavors:
        return 0
    else:
        cost = decimal.Decimal(item['vol']['qty']) * flavors[item['desc']['flavor']]
        if item['vol']['qty'] < compute_discount_threshold:
            return cost
        else:
            return cost * discount_percentage

def get_image_price(item):
    if not item['vol']['qty']:
        return 0
    else:
        cost = decimal.Decimal(item['vol']['qty']) * image_mb_price
        if item['vol']['qty'] < image_discount_threshold:
            return cost
        else:
            return  cost * discount_percentage

def get_volume_price(item):
    if not item['vol']['qty']:
        return 0
    else:
        cost = decimal.Decimal(item['vol']['qty']) * volume_gb_price
        if item['vol']['qty'] < volume_discount_threshold:
            return cost
        else:
            return cost * discount_percentage

def get_network_in_price(item):
    if not item['vol']['qty']:
        return 0
    else:
        return decimal.Decimal(item['vol']['qty']) * network_in_price

def get_network_out_price(item):
    if not item['vol']['qty']:
        return 0
    else:
        return decimal.Decimal(item['vol']['qty']) * network_out_price

def get_network_floating_price(item):
    if not item['vol']['qty']:
        return 0
    else:
        cost = decimal.Decimal(item['vol']['qty']) * network_floating_price
        if item['vol']['qty'] < floating_discount_threshold:
            return cost
        else:
            return cost * discount_percentage


# Mapping each service to its price calculation function
#http://docs.openstack.org/developer/cloudkitty/rating/hashmap.html
services = {
    'compute': get_compute_price,
    'volume': get_volume_price,
    'image': get_image_price,
    'network.bw.in': get_network_in_price,
    'network.bw.out': get_network_out_price,
    'network.floating': get_network_floating_price
}

def process(data):
    # The 'data' parameter is a list of dictionaries containing a
    # "usage" and a "period" field
    for d in data:
        usage = d['usage']
        for service_name, service_data in usage.items():
            # Do not calculate the price if the service has no
            # price calculation function
            if service_name in services.keys():
                # A service can have several items. For example,
                # each running instance is an item of the compute service
                for item in service_data:
                    item['rating'] = {'price': services[service_name](item)}
    return data


# 'data' is passed as a global variable. The script is supposed to set the
# 'rating' element of each item in each service
data = process(data)



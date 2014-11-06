import numpy
import math

"""Helper classes."""

def read_ibrl_data(data_file):
    """Reads IBRL data from file and returns dict mapping
    temp./humidity sensor data to the node that collected them

    :param data_file: string representing path to ibrl dataset
    :return: dictionary mapping sensor node to list of tuples containing sensor data
    """
    with open(data_file, 'r') as fp:
        row_count = 0
        bad_count = 0
        measurements = {}
        for line in fp:

            row_count = row_count + 1
            line = line.strip() # remove edge whitespace
            tokens = line.split(',') # segregate each section

            try:
                if len(tokens) != 5: # dump incomplete sensor readings
                    bad_count = bad_count + 1
                elif tokens[3] in measurements: # if sensor id is in the sensor dict
                    # append new temp/humidity tuple
                    measurements[tokens[3]].append((float(tokens[0]), float(tokens[1])))
                else:
                    # else create a new entry in sensor_dict and add it's respective sensor data
                    measurements[tokens[3]] = [(float(tokens[0]), float(tokens[1]))]
            except Exception as e:
                raise e
        print "Total rows: %s" % row_count
        print "Total incomplete rows: %s" % bad_count
    return measurements

def randomize_readings(dictionary):
    """For each list mapped to a sensor, randomize the tuples within and returns the resulting dictionary

    :param dictionary: Dictionary of sensors whose lists will be shuffled
    :return: Dictionary mapping sensors to randomized list of temp. and humidity readings
    """
    import random
    for sensor in dictionary:
        random.shuffle(dictionary[sensor])

    return dictionary

def generate_differences(dictionary):
    """Generates a dictionary that maps each sensor to a list of length n and containing tuples of temp. and humidity
    data to a new list of tuples size n-1 where each tuple is the difference between the original list at index n+1 and
    the original list at index n

    :param dictionary: dictionary mapping sensors to original tuples of temp. and humidity data.
    :return: tuple containing dictionary mapping sensors to new list of tuple differences and a lookup table containing
    back references to the raw measurements used to calculate the new measurements in the differences dict
    """
    differences = {}
    lookup_table = {}

    for sensor in dictionary:
        for index in range(len(dictionary[sensor]) - 1):
            difference_tuple =  (
                dictionary[sensor][index + 1][0] - dictionary[sensor][index][0],
                dictionary[sensor][index + 1][1] - dictionary[sensor][index][1]
            )
            if sensor in differences:
                differences[sensor].append(difference_tuple)
            else:
                differences[sensor] = [difference_tuple]

    return (differences, lookup_table)

def calculate_mean(list):
    """Calculate the mean of a list of numbers"""
    return sum(list) * 1.0 / len(list)

def calculate_std_dev(sensor_readings):
    """
    :param list: list of tuples representing sensor readings (temp., humidity)
    :return: tuple of population std. dev. (sd of temp, sd of humidity)
    """
    temperature_readings = [reading[0] for reading in sensor_readings]
    humidity_readings = [reading[1] for reading in sensor_readings]

    return (numpy.std(temperature_readings), numpy.std(humidity_readings))

# FIXME: Are we picking the correct values here? Why are the sigmas
# FIXME: 'swapped' in the calculations?
# FIXME: Flip the h's and t's
def calculate_dist(point_one, point_two, sigma_one, sigma_two):
    """ Calculates the distance between two points
    d(pi, pj) = (h1-h2)^2*sigma_one+(t1-t2)^2*sigma_two + 2*(h1-h2)(t1-t2)*sigma_one*sigma_two
    :param point_one: first tuple (temp., humidity)
    :param point_two: second tuple (temp., humidity)
    :param sigma_one: std. dev. of temperature readings
    :param sigma_two: std. dev. of humidity readings
    :return: distance
    """
    t1, h1 = point_one
    t2, h2 = point_two

    return math.fabs(math.pow(h1-h2, 2)*sigma_one + math.pow(t1-t2, 2)*sigma_two + 2*(h1-h2)*(t1-t2)*sigma_one*sigma_two)

def calculate_ellipsoid_orientation(sensor_readings):
    """
    :param sensor_readings: list of tuples (temp., humidity) representing readings
    :return: float, theta of ellipsoid orientation
    """

    n = len(sensor_readings)
    temperature_readings = [reading[0] for reading in sensor_readings]
    humidity_readings = [reading[1] for reading in sensor_readings]

    #FIXME(hrybacki): Come up with a better way of breaking this components down
    #FIXME(hrybacki): Shouldwe be getting negative values anywhere in here?

    # part_one
    part_one_multiplicands = [temperature_readings[i]*humidity_readings[i] for i in range(n)]
    part_one_value = n * sum(part_one_multiplicands)

    # part two
    part_two_value = sum(temperature_readings) * sum(humidity_readings)

    # part three
    part_three_value = n * sum([math.pow(temp, 2) for temp in temperature_readings])

    # part four
    part_four_value = math.pow(sum(temperature_readings), 2)

    # arctan(theta)
    tan_theta = (part_one_value - part_two_value) / (part_three_value - part_four_value)
    """
    print "Temp. readings: %s" % temperature_readings
    print "Humidity readings: %s" % humidity_readings

    print "Part one: %s" % part_one_value
    print "Part two: %s" % part_two_value
    print "Part three: %s" % part_three_value
    print "Part four: %s" % part_four_value
    print "tan(theta) = %s" % tan_theta
    """
    return math.atan(tan_theta)


def calculate_humidity_mean(sensor_readings):
    """Calculates the mean humidity of a given sensors list of readings

    :param list: list of tuples representing sensor readings (temp., humidity)
    :return: mean
    """

    total_count = 0

    for index, reading in enumerate(sensor_readings):
        total_count = total_count + reading[0] # humidity portion of tuple

    return total_count / len(sensor_readings)

def calculate_temp_mean(sensor_readings):
    """Calculates the mean temp. of a given sensors list of readings

    :param list: list of tuples representing sensor readings (humidity, temp.)
    :return: mean
    """

    total_count = 0

    for index, reading in enumerate(sensor_readings):
        total_count = total_count + reading[1] # temp. portion of tuple

    return total_count / len(sensor_readings)

def get_min_max_temp(sensor_readings):
    """
    :param sensor_readings: list of tuples representing temp and humidity readings
    :return: tuple of the minimum and maximum temps from a list of readings
    """
    min_temp = 999
    max_temp = -999
    for reading in sensor_readings:
        if reading[0] < min_temp:
            min_temp = reading[0]
        elif reading[0] > max_temp:
            max_temp = reading[0]

    return (int(min_temp), int(max_temp))

def model_ellipsoid(sensor_data):
    """Generates and returns a three tuple of ellipsoid parameter for a single sensor

    :param sensor_data: Dictionary mapping a sensor to it's normalized readings
    :return: 3-tuple with ellipsoid parameters
    """
    pass

def model_region_ellipsoid(sensor_ellipsoids):
    """Generates and returns a three tuple of ellipsoid parameter aggregate

    :param sensor_data: Dictionary mapping sensors to their respective ellipsoids
    :return: 3-tuple with ellipsoid aggregate parameters
    """
    pass

def inverse_transformation(lookup_table, aggregate_ellipsoid):
    """ Generates a tuple of two dicts mapping sensors to anomalies and true measurements

    :param lookup_table: dictionary mapping difference readings to their raw measurements
    :param aggregate_ellipsoid: 3-tuple containing aggregate ellipsoid parameters
    :return: tuple containing two dicts, one of true measurements and another of anomalies
    each mapped to their original sensors
    """
    true_measurements = {}
    anomalies = {}

    for sensor in lookup_table:
        for reading in sensor:
            if is_anomaly(reading):
                anomalies[sensor] = reading
            else:
                true_measurements[sensor] = reading

    return (true_measurements, anomalies)

def is_anomaly(reading, aggregate_ellipsoid):
    """ Determines if reading is anomaly with respect to an ellipsoid

    :param reading: temperature and humidity readings
    :param aggregate_ellipsoid: parameters for aggregate ellipsoid
    :return: True if an anomaly, else False
    """
    pass
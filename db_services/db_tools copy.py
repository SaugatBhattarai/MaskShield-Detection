import sys
from pandas import DataFrame
try:
    from db import dbconnect, dbconnect_cur
except:
    try:
        from .db import dbconnect, dbconnect_cur
    except:
        try:
            from db_services.db import dbconnect, dbconnect_cur
        except:
            from .db_services.db import dbconnect, dbconnect_cur


def insert_detection_details(full_image, vehicle_image, vehicle_type, plate_image, plate_type, detected_characters, actual_characters, gate):
    """
    all the input parameters must be strings (str)
    """
    try:
        assert all(isinstance(x, str) for x in (full_image, vehicle_image, vehicle_type,
                                                plate_image, plate_type, detected_characters, actual_characters, gate))
    except AssertionError as e:
        print(e)
        print("all input parameters must be strings")
        print("returning empty dataframe...")
        return DataFrame()

    query = """INSERT INTO detection_details (full_image,vehicle_image,vehicle_type,plate_image,plate_type,detected_characters,actual_characters,gate) \
        values ('{}','{}','{}','{}','{}','{}','{}','{}') returning *""".format(full_image, vehicle_image, vehicle_type, plate_image, plate_type, detected_characters, actual_characters, gate)

    con = dbconnect()
    return con.receive_db_data(query)


def update_detection_detail(detection_id, actual_characters):
    """
    only 'actual_detection' parameter can be updated
    actual_detection: string
    """
    try:
        assert isinstance(actual_characters, str)
    except AssertionError as e:
        print(e)
        print("'actual_prediction' must be a string. returning empty datframe")
        return DataFrame()

    query = """UPDATE detection_details set actual_characters='{}' where id={} returning *""".format(
        actual_characters, detection_id)
    con = dbconnect()
    return con.receive_db_data(query)


def insert_entry_details(detection_id):
    """
    detection_id : integer
    exit_status is always 0 for initial entry
    """
    try:
        assert isinstance(detection_id, int)
    except AssertionError as e:
        print(e)
        print("'detection_id' must be an integer. returning empty dataframe...")
        return DataFrame()

    query = """INSERT INTO entry_details (detection_id, exit_status) values ({},{}) \
        returning *""".format(detection_id, 0)
    con = dbconnect()
    return con.receive_db_data(query)


def insert_exit_details(detection_id, entry_detection_id):
    """
    detection_id: integer
    entry_detection_id: integer
    """
    try:
        assert isinstance(detection_id, int)
        assert isinstance(entry_detection_id, int)
    except AssertionError as e:
        print(e)
        print("'detection_id' and 'entry_detection_id' must be integers. returning empty dataframe...")
        return DataFrame()
    if entry_detection_id == 0:
        query = """INSERT INTO exit_details (detection_id, entry_detection_id) values ({},{}) \
            returning *""".format(detection_id, 0)
    else:
        query = """INSERT INTO exit_details (detection_id, entry_detection_id) values ({},{}) \
            returning *""".format(detection_id, entry_detection_id)
    con = dbconnect()
    return con.receive_db_data(query)


def update_vehicle_exit_status(entry_id, exit_status=1):
    """
    entry_id: integer
    exit_status: o or 1
    """
    try:
        assert isinstance(entry_id, int)
        assert isinstance(exit_status, int)
    except AssertionError as e:
        print(e)
        print("'extry_id' and 'exit_status' must be integers. returning empty dataframe")
        return DataFrame()

    query = """UPDATE entry_details set exit_status={} where id={} returning *""".format(
        exit_status, entry_id)
    con = dbconnect()
    return con.receive_db_data(query)


def get_vehicle_entry_details(license_plate_number):
    """
    check to see if the vehicle with certain license plate number exists in database
    license_plate_number: string (string of individual characters separated by space)
    """
    try:
        assert isinstance(license_plate_number, str)
    except AssertionError as e:
        print(e)
        print("'license_plate_number' must be a string. returning empty dataframe")
        return DataFrame()

    query = """SELECT 
            detection_details.id as detection_id,
            detection_details.full_image as full_frame,
            detection_details.vehicle_image as vehicle_image,
            detection_details.vehicle_type as vehicle_type,
            detection_details.plate_image as plate_image,
            detection_details.plate_type as plate_type,
            detection_details.actual_characters as license_plate_number,
            detection_details.created_on as entry_time,
            entry_details.id as entry_id,
            entry_details.detection_id as entry_detection_id 
            FROM 
            detection_details 
            INNER JOIN entry_details ON entry_details.detection_id = detection_details.id 
            where entry_details.exit_status=0 and detection_details.actual_characters='{}' 
            ORDER BY detection_details.created_on LIMIT 1
            """.format(license_plate_number)
    # print (query)
    con = dbconnect()
    return con.receive_db_data(query)


def get_detection_details_from_actual_characters(actual_characters):

    query = """select * from detection_details where actual_characters='{}' AND gate='{}' ORDER BY created_on DESC LIMIT 1""".format(
        actual_characters, 'entry')
    conn = dbconnect()

    data = conn.receive_db_data(query)

    return data

# details = insert_detection_details('test','test','test','test','test','test','test','test')
# print (details)

# details = insert_entry_details(2)
# print (details)


def get_all_vehicles_details(start_date, end_date):
    query = """SELECT 
        detection_details.id as detection_id,
        detection_details.vehicle_image as vehicle_image,
        detection_details.vehicle_type as vehicle_type,
        detection_details.plate_image as plate_image,
        detection_details.gate as gate,
        detection_details.created_on as detected_time,
        detection_details.detected_characters as predicted_plate,
        detection_details.actual_characters as actual_plate
        FROM
        detection_details
        where detection_details.created_on>'{}' and detection_details.created_on<'{}'
        """.format(start_date, end_date)
    conn = dbconnect()
    # print(query)
    data = conn.receive_db_data(query)

    return data


def get_detection_details_from_booth_type(booth_type):

    query = """select * from detection_details where gate='{}'""".format(
        booth_type)
    conn = dbconnect()

    data = conn.receive_db_data(query)

    return data


def select_query(select="*", table="", where=[], group_by="", sort={}, limit=None, offset=None):

    assert select == "*" or type(select) == tuple
    assert type(table) == str
    assert type(where) == list
    assert type(group_by) == str
    assert type(sort) == dict
    assert limit == None or type(limit) == int
    assert limit == None or type(limit) == int

    def build(select=select, table=table, where=where, group_by=group_by, sort=sort, limit=limit, offset=offset):
        if type(select) == tuple:
            select = build_select()
        query = "SELECT {} FROM {} ".format(select, table)

        if where:
            where = build_where()
            query += "WHERE {}".format(where)

        if group_by:
            query += " GROUP BY {}".format(group_by)

        if sort:
            sort = build_sort()
            query += " ORDER BY {}".format(sort)

        if limit:
            query += " LIMIT {}".format(str(limit))

        if offset:
            query += " OFFSET {}".format(str(offset))

        # print(query)
        return query

    def build_select():
        return " ".join(select)

    def build_where():
        # should be list of objects in format {"key": "key1", "value": "value1", "comparator": "comparator1"}
        # where comparator should be one of [=, >, <]
        new_where = ""
        for condition in where:
            value = condition['value']
            value = value if type(value) == int else "'{}'".format(value)
            new_where += "{}{}{} and ".format(
                condition['key'], condition["comparator"], value)
        return new_where[:-4]

    def build_sort():
        new_sort = ""
        for k in sort.keys():
            new_sort += "{} {},".format(k, sort[k])
        return new_sort[:-1]

    query = build()

    conn = dbconnect()
    return conn.receive_db_data(query)

# print (select_query(select="*", table="images", where={}, group_by="image_id", sort={"image_id": "desc"}, limit=10, offset=5))


def insert_into_flag_number(vehicle_number, detection_status, flag_status, vehicle_type, vehicle_description, remarks):

    query = "insert into flag_number (vehicle_number, detection_status, flag_status, vehicle_type, vehicle_description, remarks) values \
            ('{}', '{}', '{}', '{}', '{}', '{}')".format(vehicle_number, detection_status, flag_status, vehicle_type, vehicle_description, remarks)

    conn = dbconnect()
    try:
        conn.execute_query(query)
        print("executed successfully")
        return True
    except Exception as e:
        print("Exception: ", e)
        return False

# insert_into_flag_number('बा ५ ख ३ ८',1, 1, 'kha', 'car description 2', 'car remarks 2')


def update_flag_detection_status(flag_id):

    query = """update flag_number set detection_status = {}, updated_on=now() where flag_id= {}""".format(1, flag_id)

    conn = dbconnect()

    try:
        conn.execute_query(query)
        print("updated successfully")
        return True
    except Exception as e:
        print(e)
        return False
# update_flag_detection_status(5)


def update_into_flag_number(flag_id, vehicle_number, vehicle_type, vehicle_description, remarks):

    query = """update flag_number set vehicle_number = '{}', vehicle_type= '{}', vehicle_description= '{}', remarks= '{}', updated_on= now() where flag_id='{}'""".format(vehicle_number,
                                                                                                                                                                          vehicle_type, vehicle_description, remarks, flag_id)

    conn = dbconnect()

    try:
        conn.execute_query(query)
        print("updated successfully")
        return True
    except Exception as e:
        print(e)
        return False

#update_into_flag_number(1,'बा ५ ख ३ ५ ८ ८','bus', 'hello world','change in remarks')


def delete_flag(flag_id):
    assert type(flag_id) == int
    query = """update flag_number set active=0, updated_on=now() where flag_id={}""".format(flag_id)

    conn = dbconnect()
    try:
        return conn.execute_query(query)
    except Exception as e:
        print(e)
        return False


def get_flag_details():
    print('inside get flag details')
    # {"key": "key1", "value": "value1", "comparator": "comparator1"}
    flag_list = select_query(select="*", table="flag_number",
                             where=[{"key": "active", "value": 1, "comparator": "="}])
    # print(flag_list)

    def _get_temp():
        return {"flag_id": None, "vehicle_number": None, "flag_status": None, "detection_status": None, "vehicle_type": None, "vehicle_description": None, "remarks": None, "active": None}

    details = []
    for i in range(0, len(flag_list)):
        temp = _get_temp()
        temp["flag_id"] = str(flag_list.iloc[i]["flag_id"])
        temp["vehicle_number"] = flag_list.iloc[i]["vehicle_number"]
        temp["flag_status"] = str(flag_list.iloc[i]["flag_status"])
        temp["detection_status"] = str(flag_list.iloc[i]["detection_status"])
        temp["vehicle_type"] = flag_list.iloc[i]["vehicle_type"]
        temp["vehicle_description"] = flag_list.iloc[i]["vehicle_description"]
        temp["remarks"] = flag_list.iloc[i]["remarks"]
        temp["active"] = str(flag_list.iloc[i]["active"])
        # details[str(flag_list.iloc[i]["flag_id"])] = temp
        details.append(temp)
    return details


def insert_into_movie_detection(poster_image_path, detection_status, detection_number, delete_status, detection_1_path,
                                detection_2_path, detection_3_path, detected_movie_name, actual_movie_name):

    query = "insert into flag_number (vehicle_number, detection_status, flag_status, vehicle_type, vehicle_description, remarks) values \
            ('{}', '{}', '{}', '{}', '{}', '{}')".format(vehicle_number, detection_status, flag_status, vehicle_type, vehicle_description, remarks)

    conn = dbconnect()
    try:
        conn.execute_query(query)
        print("executed successfully")
        return True
    except Exception as e:
        print("Exception: ", e)
        return False

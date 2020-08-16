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


def insert_into_maskshield_detection(covid_image_path, detection_status, detection_number, detection_maskshield_number, delete_status, detect_mask_path,
                                     detect_no_mask_path, detect_faceshield_path, detect_no_faceshield_path, detect_person_path):

    query = """INSERT INTO maskshield_detection (covid_image_path, detection_status, detection_number, detection_maskshield_number, delete_status, detect_mask_path, detect_no_mask_path,  detect_faceshield_path, detect_no_faceshield_path, detect_person_path) \
        values ('{}','{}','{}','{}','{}','{}','{}','{}', '{}', '{}') returning *""".format(covid_image_path, detection_status, detection_number, detection_maskshield_number, delete_status, detect_mask_path, detect_no_mask_path, detect_faceshield_path, detect_no_faceshield_path, detect_person_path)

    conn = dbconnect()
    try:
        # conn.execute_query(query)
        # print("executed successfully")
        return conn.receive_db_data(query)
    except Exception as e:
        print("Exception: ", e)
        return False


def get_maskshield_details():

    query = """select detection_id,covid_image_path,detection_status,detection_number, detection_maskshield_number, delete_status, detect_mask_path, detect_no_mask_path,
        detect_faceshield_path, detect_no_faceshield_path, detect_person_path from maskshield_detection where delete_status=0 order by detection_id DESC limit 4"""

    conn = dbconnect()

    return conn.receive_db_data(query)


def insert_into_maskshield_detection_info(detection_id, image_path,  total_detection, detect_mask, detect_faceshield,
                                          detect_no_mask, detect_no_faceshield, detect_person):
    #    print('...in db_tools_covid...')
    query = """INSERT INTO maskshield_detection_info(detection_id, image_path, total_detection, detect_mask, detect_faceshield, detect_no_mask, detect_no_faceshield, detect_person) \
        values('{}', '{}','{}', '{}', '{}', '{}', '{}', '{}') returning * """.format(detection_id, image_path, total_detection, detect_mask, detect_faceshield, detect_no_mask, detect_no_faceshield, detect_person)

    conn = dbconnect()
    try:
        conn.execute_query(query)
#        print("executed successfully info")
        return True
        # return conn.receive_db_data(query)
    except Exception as e:
        print("Exception: ", e)
        return False


def get_maskshield_detection_info():

    query = """select detection_id, image_path, total_detection, detect_mask,
    detect_faceshield, detect_no_mask, detect_no_faceshield, detect_person
    from maskshield_detection_info order by detection_info_id DESC limit 4"""

    conn = dbconnect()

    return conn.receive_db_data(query)


# TESTING TABLE

# detection_id = insert_into_maskshield_detection(
#     '45.jpg', 1, 2, 1, 0, '', '', '', '', '')
# print(a)

# b = get_maskshield_details()
# print(b)

# detection_id = detection_id.iloc[0]['detection_id'].tolist()
# print(detection_id)
# detection_info = insert_into_maskshield_detection_info(
#     detection_id, '', 3, 1, 1, 0, 0, 1)
# print(detection_info)

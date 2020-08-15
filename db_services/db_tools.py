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


def insert_into_movie_detection(poster_image_path, detection_status, detection_number, delete_status, detection_1_path,
                                detection_2_path, detection_3_path, detected_movie_name, actual_movie_name):

    query = """INSERT INTO movie_detection (poster_image_path, detection_status, detection_number, delete_status, detection_1_path, detection_2_path, detection_3_path, detected_movie_name, actual_movie_name) \
        values ('{}','{}','{}','{}','{}','{}','{}','{}', '{}') returning *""".format(poster_image_path, detection_status, detection_number, delete_status, detection_1_path, detection_2_path, detection_3_path, detected_movie_name, actual_movie_name)

    conn = dbconnect()
    try:
        conn.execute_query(query)
        # print("executed successfully")
        return True
    except Exception as e:
        print("Exception: ", e)
        return False


def get_movie_detection_details():

    query = """select poster_id,poster_image_path,detection_status,detection_number, delete_status, detection_1_path, 
         detection_2_path from movie_detection where delete_status=0 order by poster_id DESC limit 4"""

    conn = dbconnect()

    return conn.receive_db_data(query)

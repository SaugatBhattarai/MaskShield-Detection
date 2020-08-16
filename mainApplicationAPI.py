
import math
import cv2
from datetime import date, datetime
from time import time, sleep
import tornado.web
import tornado.ioloop
import tornado.options
import socket
import sys
import json
import os

from darknet import performDetect as scan
from db_services.db_tools import insert_into_maskshield_detection, get_maskshield_details, insert_into_maskshield_detection_info, get_maskshield_detection_info

ROOT_PATH = os.path.abspath(os.getcwd()) + '/'


def _get_maskshield_detection_details():

    maskshield_details = get_maskshield_details()

    def get_temp():
        temp_dict = {
            "covid_image_path": '',
            "detection_number": 0,
            "detection_maskshield_number": 0,
            "detect_mask_path": '',
            "detect_faceshield_path": '',
            "detect_no_mask_path": '',
            "detect_no_faceshield_path": '',
            "detect_person_path": ''
        }

        return temp_dict

    details = {}
    for i in range(0, len(maskshield_details)):
        temp = get_temp()
        temp["covid_image_path"] = maskshield_details.iloc[i]["covid_image_path"]
        temp["detection_number"] = maskshield_details.iloc[i]["detection_number"]
        temp["detect_mask_path"] = maskshield_details.iloc[i]["detect_mask_path"]
        temp["detect_faceshield_path"] = maskshield_details.iloc[i]["detect_faceshield_path"]
        temp["detect_no_mask_path"] = maskshield_details.iloc[i]["detect_no_mask_path"]
        temp["detect_no_faceshield_path"] = maskshield_details.iloc[i]["detect_no_faceshield_path"]
        temp["detect_person_path"] = maskshield_details.iloc[i]["detect_person_path"]
        details[maskshield_details.iloc[i]['detection_id']] = temp
    return details


def _get_maskshield_detection_info():

    covid_details_info = get_maskshield_detection_info()

    def get_temp():
        temp_dict = {
            "detection_id": 0,
            "image_path": '',
            "total_detection": 0,
            "detect_mask": 0,
            "detect_faceshield": 0,
            "detect_no_mask": 0,
            "detect_no_faceshield": 0,
            "detect_person": 0
        }

        return temp_dict

    details = {}
    for i in range(0, len(covid_details_info)):
        temp = get_temp()
        temp["detection_id"] = covid_details_info.iloc[i]["detection_id"]
        temp["image_path"] = covid_details_info.iloc[i]["image_path"]
        temp["total_detection"] = covid_details_info.iloc[i]["total_detection"]
        temp["detect_mask"] = covid_details_info.iloc[i]["detect_mask"]
        temp["detect_faceshield"] = covid_details_info.iloc[i]["detect_faceshield"]
        temp["detect_no_mask"] = covid_details_info.iloc[i]["detect_no_mask"]
        temp["detect_no_faceshield"] = covid_details_info.iloc[i]["detect_no_faceshield"]
        temp["detect_person"] = covid_details_info.iloc[i]["detect_person"]
        details[covid_details_info.iloc[i]['detection_id']] = temp
    return details


def detect(img_path):
    ''' this script if you want only want get the coord '''
    picpath = img_path

    # change this if you want use different config
    cfg = ROOT_PATH + 'cfg/yolo-obj.cfg'
    coco = ROOT_PATH + 'obj.data'  # you can change this too
    # and this, can be change by you

    data = ROOT_PATH + 'backup/yolo-obj_last.weights'
    test = scan(imagePath=picpath, thresh=0.35, configPath=cfg, weightPath=data, metaPath=coco, showImage=False, makeImageOnly=False,
                initOnly=False)  # default format, i prefer only call the result not to produce image to get more performance

    # until here you will get some data in default mode from alexeyAB, as explain in module.
    # try to: help(scan), explain about the result format of process is: [(item_name, convidence_rate (x_center_image, y_center_image, width_size_box, height_size_of_box))],
    # to change it with generally used form, like PIL/opencv, do like this below (still in detect function that we create):

    newdata = []

    # For multiple Detection
    if len(test) > 0:
        for x in test:
            item, confidence_rate, imagedata = x
            x1, y1, w_size, h_size = imagedata
            x_start = round(x1 - (w_size/2))
            y_start = round(y1 - (h_size/2))
            x_end = round(x_start + w_size)
            y_end = round(y_start + h_size)
            data = (item, confidence_rate,
                    (x_start, y_start, x_end, y_end), (w_size, h_size))
            newdata.append(data)

    else:
        newdata = []
    print('from detect ...')
    return newdata


def main(image):
    detections = detect(image)

    img = cv2.imread(image)
    today = datetime.today().isoformat().replace('-', "").replace(':', "")[:15]

    try:
        # Multiple detection
        if len(detections) > 0:
            count = 0
            multiple_crop_img_path = {
                'masks': "",
                'faceshield': "",
                'no_masks': "",
                'no_faceshield': "",
                'person': ""
            }
            for detection in detections:
                x1, y1, x2, y2 = detection[2]
                x1 = abs(x1)
                y1 = abs(y1)
                x2 = abs(x2)
                y2 = abs(y2)

                IMAGE_NAME = 'static/covid_detected/' + detection[0] + "/" + \
                    today + str(count) + '.jpg'
                CROPPED_PATH = ROOT_PATH + IMAGE_NAME
                cropped_image = img[y1:y2, x1:x2]
                print('IMage name', IMAGE_NAME)
                print('cropped path ... multiple detection', CROPPED_PATH)
                cv2.imwrite(CROPPED_PATH, cropped_image)
                multiple_crop_img_path.update({detection[0]: IMAGE_NAME})
                count += 1

            masks_len = 0
            faceshield_len = 0
            if len(multiple_crop_img_path['masks']) > 1:
                masks_len = 1
            if len(multiple_crop_img_path['faceshield']) > 1:
                faceshield_len = 1

            maskshield_number = masks_len + faceshield_len  # todo calculate masks and shield
            data = {
                'root': ROOT_PATH,
                'cropped_image': multiple_crop_img_path,
                'detection_number': len(detections),
                'maskshield_number': maskshield_number
            }
        # Single detection
        else:
            data = {
                'root': ROOT_PATH,
                'cropped_image': None,
                'detection_number': 0,
                'maskshield_number': 0
            }
            return data
    except:
        data = {
            'root': ROOT_PATH,
            'cropped_image': None,
            'detection_number': 0,
            'maskshield_number': 0
        }
        return data
    return data


class HomePage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render(
            'index.html', title="Saugat Bhattarai - Artificial Intelligence | Machine Learning | Natural Language Processing")


class ProjectMaskShieldPage(tornado.web.RequestHandler):

    def initialize(self):
        self.maskshield_details_dict = _get_maskshield_detection_details()
        self.maskshield_details_info = _get_maskshield_detection_info()

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('maskshield.html', title="Mask-Shield Detection Page",
                    detection_history=self.maskshield_details_info)

    def post(self):
        today = datetime.today().isoformat().replace(
            '-', "").replace(':', "")[:15]
        detected_dict_img_path = {}
        detected_dict = {
            'Masks': [0, 'Not Detected'],
            'Face Shield': [0, 'Not Detected']
        }

        detected_items_number = {
            'masks': 0,
            'faceshield': 0,
            'no_masks': 0,
            'no_faceshield': 0,
            'person': 0
        }

        last_detection_id = None

        try:

            file1 = self.request.files['file1'][0]
            original_fname = file1['filename']
            image_abs_path = "static/covid_images/" + today + original_fname
            output_file = open(image_abs_path, 'wb')
            output_file.write(file1['body'])

            result = main(image_abs_path)
            print('cropped image', result["cropped_image"])
            print('result ...', result)
            if result["cropped_image"] is not None:
                print('inside result not NOne')
                if result['cropped_image']['masks']:
                    detection_1_path = result['cropped_image']['masks']
                    detected_dict_img_path['masks'] = result['cropped_image']['masks']
                    detected_dict.update({"Masks": [1, "Detected"]})
                    detected_items_number.update({'masks': 1})
                    print('detection_1_path', detection_1_path)
                else:
                    detection_1_path = result['cropped_image']['masks']
                    print('detection_1_path', detection_1_path)

                if result['cropped_image']['faceshield']:
                    detection_2_path = result['cropped_image']['faceshield']
                    detected_dict_img_path['faceshield'] = result['cropped_image']['faceshield']
                    detected_dict.update({"Face Shield": [1, "Detected"]})
                    detected_items_number.update({'faceshield': 1})
                    print('detection_2_path', detection_2_path)
                else:
                    detection_2_path = result['cropped_image']['faceshield']
                    print('detection_2_path', detection_2_path)

                if result['cropped_image']['no_masks']:
                    detection_3_path = result['cropped_image']['no_masks']
                    detected_dict_img_path['no_masks'] = result['cropped_image']['no_masks']
                    detected_items_number.update({'no_masks': 1})
                    print('detection_3_path', detection_3_path)
                else:
                    detection_3_path = result['cropped_image']['no_masks']
                    print('detection_3_path', detection_3_path)

                if result['cropped_image']['no_faceshield']:
                    detection_4_path = result['cropped_image']['no_faceshield']
                    detected_dict_img_path['no_faceshield'] = result['cropped_image']['no_faceshield']
                    detected_items_number.update({'no_faceshield': 1})
                    print('detection_4_path', detection_4_path)
                else:
                    detection_4_path = result['cropped_image']['no_faceshield']
                    print('detection_4_path', detection_4_path)

                if result['cropped_image']['person']:
                    detection_5_path = result['cropped_image']['person']
                    detected_dict_img_path['person'] = result['cropped_image']['person']
                    detected_items_number.update({'no_person': 1})
                    print('detection_5_path', detection_5_path)
                else:
                    detection_5_path = result['cropped_image']['person']
                    print('detection_5_path', detection_5_path)

                print('mask shield ........number ...',
                      result['maskshield_number'])
                detection_id = insert_into_maskshield_detection(image_abs_path, 1, result['detection_number'], result['maskshield_number'],
                                                                0, detection_1_path, detection_2_path, detection_3_path, detection_4_path, detection_5_path)

                print('detection id ...', detection_id)
                last_detection_id = detection_id.iloc[0]['detection_id'].tolist(
                )

                insert_into_maskshield_detection_info(
                    last_detection_id, image_abs_path, result['detection_number'], detected_items_number['masks'], detected_items_number['faceshield'], detected_items_number['no_masks'], detected_items_number['no_faceshield'], detected_items_number['person'])
                safety_percentage = result['maskshield_number']

                self.render('covid_results_list.html',
                            source_image=image_abs_path, detected_category=detected_dict, destination_image=detected_dict_img_path, detection_history=self.maskshield_details_info, safety_percentage=safety_percentage)

            else:
                # print('no thing detected', result["cropped_image"])
                detection_id = insert_into_maskshield_detection(
                    image_abs_path, 1, 0, 0, 0, '', '', '', '', '')

                last_detection_id = detection_id.iloc[0]['detection_id'].tolist(
                )
                insert_into_covid_detection_info(
                    last_detection_id, image_abs_path, result['detection_number'], 0, 0, 0, 0, 0)

                self.render('covid_result_no_value.html',
                            title="Covid-19 Safety Kit Analyzer", detection_history=self.maskshield_details_info)

        except:
            print('at except')
            self.render('covid_result_no_image_selected.html',
                        title="Covid-19 Safety Kit Analyzer", detection_history=self.maskshield_details_info)


class AboutPage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('about.html', title="About Me - Saugat Bhattarai")


settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=False,
    autoreload=True
)


def make_app():
    return tornado.web.Application([
        (r"/masks-shield", ProjectMaskShieldPage),
        (r"/", HomePage)
    ], **settings)


if __name__ == "__main__":
    port = 8888
    app = make_app()
    print("Server is Runing " + str(port))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


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
from db_services.db_tools import insert_into_movie_detection, get_movie_detection_details

ROOT_PATH = os.path.abspath(os.getcwd()) + '/'


def _get_movie_detection_details():

    poster_details = get_movie_detection_details()

    def get_temp():
        temp_dict = {
            "poster_image_path": '',
            # "detection_status": 1,
            "detection_number": 1,
            "detection_1_path": '',
            "detection_2_path": ''
        }

        return temp_dict

    details = {}
    for i in range(0, len(poster_details)):
        temp = get_temp()
        temp["poster_image_path"] = poster_details.iloc[i]["poster_image_path"]
        # temp["detection_status"] = poster_details.iloc[i]["detection_status"]
        temp["detection_number"] = poster_details.iloc[i]["detection_number"]
        temp["detection_1_path"] = poster_details.iloc[i]["detection_1_path"]
        temp["detection_2_path"] = poster_details.iloc[i]["detection_2_path"]
        details[poster_details.iloc[i]['poster_id']] = temp
    return details


def detect(img_path):
    ''' this script if you want only want get the coord '''
    picpath = img_path

    # change this if you want use different config
    cfg = ROOT_PATH + 'cfg/yolo-obj.cfg'
    coco = ROOT_PATH + 'obj.data'  # you can change this too
    # and this, can be change by you

    data = ROOT_PATH + 'backup/yolo-obj_last.weights'
    test = scan(imagePath=picpath, thresh=0.25, configPath=cfg, weightPath=data, metaPath=coco, showImage=False, makeImageOnly=False,
                initOnly=False)  # default format, i prefer only call the result not to produce image to get more performance

    # until here you will get some data in default mode from alexeyAB, as explain in module.
    # try to: help(scan), explain about the result format of process is: [(item_name, convidence_rate (x_center_image, y_center_image, width_size_box, height_size_of_box))],
    # to change it with generally used form, like PIL/opencv, do like this below (still in detect function that we create):

    newdata = []

    # For multiple Detection
    if len(test) >= 2:
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

    # For Single Detection
    elif len(test) == 1:
        item, confidence_rate, imagedata = test[0]
        x1, y1, w_size, h_size = imagedata
        x_start = round(x1 - (w_size/2))
        y_start = round(y1 - (h_size/2))
        x_end = round(x_start + w_size)
        y_end = round(y_start + h_size)
        data = (item, confidence_rate,
                (x_start, y_start, x_end, y_end), (w_size, h_size))
        newdata.append(data)

    else:
        newdata = False

    return newdata


def main(image):
    detections = detect(image)

    img = cv2.imread(image)
    today = datetime.today().isoformat().replace('-', "").replace(':', "")[:15]

    try:
        # Multiple detection
        if len(detections) > 1:
            count = 0
            multiple_crop_img_path = []
            for detection in detections:
                x1, y1, x2, y2 = detection[2]
                x1 = abs(x1)
                y1 = abs(y1)
                x2 = abs(x2)
                y2 = abs(y2)

                IMAGE_NAME = 'static/movie_names/'+today + str(count) + '.jpg'
                CROPPED_PATH = ROOT_PATH + IMAGE_NAME
                cropped_image = img[y1:y2, x1:x2]

                cv2.imwrite(CROPPED_PATH, cropped_image)
                multiple_crop_img_path.append(IMAGE_NAME)
                count += 1

            data = {
                'root': ROOT_PATH,
                'cropped_image': multiple_crop_img_path
            }
        # Single detection
        else:
            if len(detections) == 1:
                x1, y1, x2, y2 = detections[0][2]

                x1 = abs(x1)
                y1 = abs(y1)
                x2 = abs(x2)
                y2 = abs(y2)

                IMAGE_NAME = 'static/movie_names/'+today + '.jpg'
                CROPPED_PATH = ROOT_PATH + IMAGE_NAME
                cropped_image = img[y1:y2, x1:x2]
                cv2.imwrite(CROPPED_PATH, cropped_image)

                data = {
                    'root': ROOT_PATH,
                    'cropped_image': IMAGE_NAME
                }
    except:
        data = {
            'root': ROOT_PATH,
            'cropped_image': None
        }
        return data
    return data


class ProjectsPosterPage(tornado.web.RequestHandler):

    def initialize(self):
        self.movie_details_dict = _get_movie_detection_details()

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('posterindex.html', title="Movie Extraction System",
                    movie_details_dict=self.movie_details_dict)

    def post(self):

        today = datetime.today().isoformat().replace(
            '-', "").replace(':', "")[:15]
        try:
            file1 = self.request.files['file1'][0]
            original_fname = file1['filename']
            image_abs_path = "static/poster_images/" + today + original_fname
            output_file = open(image_abs_path, 'wb')
            output_file.write(file1['body'])

            result = main(image_abs_path)

            if result["cropped_image"] is not None:
                if isinstance(result["cropped_image"], list):
                    detection_1_path = result['cropped_image'][0]
                    detection_2_path = result['cropped_image'][1]
                    detection_3_path = ''

                    insert_into_movie_detection(image_abs_path, 1, len(
                        result['cropped_image']), 0, detection_1_path, detection_2_path, detection_3_path, '', '')

                    self.render('result_list.html',
                                source_image=image_abs_path, movie_details_dict=self.movie_details_dict, destination_image=result["cropped_image"])
                else:
                    insert_into_movie_detection(
                        image_abs_path, 1, 1, 0, result["cropped_image"], '', '', '', '')

                    self.render('results.html',
                                source_image=image_abs_path, movie_details_dict=self.movie_details_dict, destination_image=result["cropped_image"])

            else:
                insert_into_movie_detection(
                    image_abs_path, 1, 0, 0, '', '', '', '', '')

                self.render('result_no_value.html',
                            movie_details_dict=self.movie_details_dict)
        except:
            print('There is not file uploaded')
            self.render('result_no_image_selected.html',
                        movie_details_dict=self.movie_details_dict)

        # self.set_status(200)


class AboutPage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('about.html', title="About Me - Saugat Bhattarai")


class ContactPage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('contact.html', title="About Me - Saugat Bhattarai")


class ProjectsPage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('projects.html', title="Project Page")


class HomePage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render(
            'index.html', title="Saugat Bhattarai - Artificial Intelligence | Machine Learning | Natural Language Processing")


class ResumePage(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        'authorization, content-type')

    def get(self):
        self.render('resume.html',
                    title="Curriculam Vitae Page- Saugat Bhattarai")


settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=False,
    autoreload=True
)


def make_app():
    return tornado.web.Application([
        (r"/projects", ProjectsPage),
        (r"/poster", ProjectsPosterPage),
        (r"/about", AboutPage),
        (r"/contact", ContactPage),
        (r"/resume", ResumePage),
        (r"/", HomePage)
    ], **settings)


if __name__ == "__main__":
    port = 8888
    app = make_app()
    print("Server is Runing " + str(port))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

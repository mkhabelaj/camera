import cv2
from datetime import datetime
import imutils
from glob import glob
import sys
import socket
from struct import pack


class Camera:
    def __init__(self, camera_number, initialize_stream=False, stream_port=0, *args, **kwargs):
        """
        :param camera_number: Video camera ID
        :param args:
        :param kwargs: configuration
        """
        self.show_video = kwargs.get('show_video')
        self.delta_thresh = kwargs.get('delta_thresh')
        self.record_motion = kwargs.get('record_motion')
        self.min_area = kwargs.get('min_area')
        self.email_images = kwargs.get('email_images')
        self.min_email_seconds = kwargs.get('min_email_seconds')
        self.motion_detection = kwargs.get('motion_detection')
        self.display_text_if_occupied = kwargs.get('display_text_if_occupied')
        self.display_text_if_unoccupied = kwargs.get('display_text_if_unoccupied')
        # Setting up video self.capture
        self.camera_number = camera_number
        print('Setting up camera {camera_number}'.format(camera_number=camera_number))
        self.capture = cv2.VideoCapture(camera_number)
        self.initialize_stream = initialize_stream
        self.stream_port = stream_port
        self.resolution_width = kwargs.get('resolution_width')
        self.resolution_height = kwargs.get('resolution_height')
        self.set_camera_resolution(self.resolution_width, self.resolution_height)
        # todo create zoom functionality
        # todo create record video option
        # todo create email functionality

        if self.initialize_stream:
            print('creating stream ...')
            if self.stream_port == 0:
                print("Port stream port is not set, canceling socket set up....")
                self.initialize_stream = False
                return False
            self.server_address = ("0.0.0.0", self.stream_port)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client_socket.connect(self.server_address)
                print('Connection established, streaming to port {port}'.format(port=self.stream_port))
            except Exception as ex:
                self.initialize_stream = False
                print('Failed to create socket connection: {stream_port}'.format(stream_port=self.stream_port), ex)

    def initialise_camera(self):
        avg = None
        while True:
            # print(len(thread_counter))
            text = self.display_text_if_unoccupied
            timestamp = datetime.now()
            # self.capture frame-by-frame
            ret, frame = self.capture.read()

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if avg is None:
                print("[INFO] starting background model...")
                avg = gray.copy().astype("float")
                continue
            if self.motion_detection:
                result = self.motion_detector(gray, avg, frame, text)
                text = result[2]

            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            if self.initialize_stream:
                self.stream_image(frame)
            else:
                cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the self.capture
        self.capture.release()
        cv2.destroyAllWindows()

    def motion_detector(self, gray_frame, avg, frame, text):
        motion_detected = False
        cv2.accumulateWeighted(gray_frame, avg, 0.5)
        frame_delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frame_delta, self.delta_thresh, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        if cnts:
            motion_detected = True
            text = self.display_text_if_occupied

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.min_area:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return motion_detected, frame, text

    def stream_image(self, frame):
        if frame.any():
            img = cv2.imencode(".jpg", frame)[1].tostring()
            file_size = len(img)
            length = pack('>Q', file_size)
            try:
                self.client_socket.send(length)
                self.client_socket.sendall(img)
            except Exception as ex:
                print(ex)
                self.initialize_stream = False

    def set_camera_resolution(self, width, height):
        print('setting up camera resolution')
        try:
            self.capture.set(3, width)
            self.capture.set(4, height)
        except Exception as ex:
            print('camera does not support resolution ', ex)



    @staticmethod
    def count_system_cameras(path='/dev/video*'):
        print("counting number of camera's available under the following path {path}".format(path=path))
        camera_positions = []
        cameras = glob(path)
        if cameras:
            print('{camera} found'.format(camera=len(cameras)))
            for camera in cameras:
                camera_positions.append(int(camera[-1:]))
        else:
            print("No cameras available exiting ....")
            sys.exit([1])
        return camera_positions




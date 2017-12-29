import cv2
from datetime import date, datetime
import imutils
from threading import Thread


class Camera:
    def __init__(self, camera_number, display_on_web=False, *args, **kwargs):
        """
        :param camera_number: Video camera ID
        :param args:
        :param kwargs: configuration
        """
        if kwargs.get('show_video'):
            self.show_video = kwargs.get('show_video')
        if kwargs.get('min_motion_frames'):
            self.min_motion_frames = kwargs.get('min_motion_frames')
        if kwargs.get('delta_thresh'):
            self.delta_thresh = kwargs.get('delta_thresh')
        if kwargs.get('fps'):
            self.fps = kwargs.get('fps')
        if kwargs.get('resolution'):
            self.resolution = kwargs.get('resolution')
        if kwargs.get('record_motion'):
            self.record_motion = kwargs.get('record_motion')
        if kwargs.get('min_area'):
            self.min_area = kwargs.get('min_area')
        if kwargs.get('email_images'):
            self.email_images = kwargs.get('email_images')
        # Setting up video self.capture
        self.camera_number = camera_number
        self.display_on_web = display_on_web
        print('Setting up camera {camera_number}'.format(camera_number=camera_number))
        self.capture = cv2.VideoCapture(camera_number)
        ret, frame = self.capture.read()

    def initialise_camera(self):
        avg = None
        while True:
            text = "unoccupied"
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

            cv2.accumulateWeighted(gray, avg, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, self.delta_thresh, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.min_area:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"
                # if not myThread.is_alive():
                    # myThread = MyThread()
                    # myThread.start()

            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            # if self.display_on_web:
            #     print(self.display_on_web)
            #     ret, jpeg = cv2.imencode('.jpg', frame)
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + bytearray(jpeg.tobytes()) + b'\r\n')
            # else:
            #     # Display the resulting frame
            cv2.imshow('frame', frame)
            print(self.display_on_web)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the self.capture
        self.capture.release()
        cv2.destroyAllWindows()

    def start(self):
        print("start thread")
        # start the thread to read frames from the video stream
        t = Thread(target=self.initialise_camera, args=())
        # t.daemon = True
        t.start()
        # return self

import cv2 as open_cv
import numpy as np
import logging
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE
from collections import Counter
import time
import datetime
from tkinter import *
import tkinter.font
from PIL import Image, ImageTk
from booking import window
import random
from single import Single
from pay import Number

class MotionDetector:
    LAPLACIAN = 1.5
    DETECT_DELAY = 1
    def __init__(self, video, coordinates, start_frame):
        self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []
        self.time_log = [self.exit_time() for i in range(len(coordinates))]
        self.centers = [0 for i in range(len(coordinates))]
        self.lmain = None
        self.app  = None


    def detect_motion(self):
        capture = open_cv.VideoCapture(self.video)
        capture.set(open_cv.CAP_PROP_POS_FRAMES, self.start_frame)

        coordinates_data = self.coordinates_data
        logging.debug("coordinates data: %s", coordinates_data)


        self.app = Tk()
        self.app.geometry('1200x800')
        self.app.title('Tez Parking(Null Pointer Exception)')

        font1 = tkinter.font.Font(family='Times', size=30, weight='bold')
        text_frame1 = Frame(self.app, bg="grey", borderwidth=2, relief=GROOVE)
        text_frame1.place(x=1000, y=0, width=120, height=300)
        l11 = Label(text_frame1, text="Vacant Slot")
        l11.pack(side=TOP)
        l1 = Listbox(text_frame1)
        l1.pack()


        text_frame2 = Frame(self.app, bg="grey", borderwidth=2, relief=GROOVE)
        text_frame2.place(x=1120, y=0, width=120, height=300)
        l21 = Label(text_frame2, text="Occupied Slot")
        l21.pack(side=TOP)
        l2 = Listbox(text_frame2)
        l2.pack()
        l2.insert(END, "Data list")

        text_frame3 = Frame(self.app, bg="grey",  borderwidth=2, relief=GROOVE)
        text_frame3.place(x=1240, y=0, width=120, height=300)
        l11 = Label(text_frame3, text="listbox")
        l11.pack(side=TOP)
        l3 = Listbox(text_frame3)
        l3.pack()

        b_frame = Frame(self.app, borderwidth=2, relief=GROOVE)
        l3 = Label(b_frame, text='0',font=font1, width=10)

        l4 = Label(b_frame, text="Total Vacant Slot",font=font1)
        l4.pack(side=LEFT)

        b1 = Button(b_frame, bg='grey',text='Book/Pay', font=font1,command = window)
        b1.pack(side=RIGHT)
        b_frame.pack(side=BOTTOM)
        obj = Number()
        obj.final()
        text_frame4 = Frame(self.app, bg="grey", borderwidth=2, relief=GROOVE)
        text_frame4.place(x=1000, y=300, width=360, height=300)


        imagelist = ['1.jpg','2.jpg','3.jpg','4.jpg','5.jpg','6.jpg','7.jpg','8.jpg','9.jpg']

        rand_item = imagelist[random.randrange(len(imagelist))]
        load = Image.open("number_plate_data/"+rand_item)
        load = load.resize((350, 290), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(text_frame4, image=render)
        img.image = render
        img.place(x=0, y=0)






        imageFrame = Frame(self.app, bg="grey")
        imageFrame.place(x=0, y=0, width=1000, height=600)
        vaccant_label = Label(imageFrame,text = 'Best Availabe Slot',font=font1)
        vaccant_label.place(x=0,y=510,width=990,height=80)
        lmain = Label(imageFrame)
        lmain.grid(row=0, column=0)




        for p in coordinates_data:
            coordinates = self._coordinates(p)
            logging.debug("coordinates: %s", coordinates)

            rect = open_cv.boundingRect(coordinates)
            logging.debug("rect: %s", rect)

            new_coordinates = coordinates.copy()
            new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
            new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
            logging.debug("new_coordinates: %s", new_coordinates)

            self.contours.append(coordinates)
            self.bounds.append(rect)

            mask = open_cv.drawContours(
                np.zeros((rect[3], rect[2]), dtype=np.uint8),
                [new_coordinates],
                contourIdx=-1,
                color=255,
                thickness=-1,
                lineType=open_cv.LINE_8)


            mask = mask == 255
            self.mask.append(mask)
            logging.debug("mask: %s", self.mask)

        statuses = [False] * len(coordinates_data)
        times = [None] * len(coordinates_data)
        # time_log = [0 for i in range(len(statuses))]

        while capture.isOpened():
            result, frame = capture.read()
            if frame is None:
                break

            if not result:
                raise CaptureReadError("Error reading video capture on frame %s" % str(frame))

            blurred = open_cv.GaussianBlur(frame.copy(), (5, 5), 3)
            grayed = open_cv.cvtColor(blurred, open_cv.COLOR_BGR2GRAY)
            new_frame = frame.copy()
            logging.debug("new_frame: %s", new_frame)

            position_in_seconds = capture.get(open_cv.CAP_PROP_POS_MSEC) / 1000.0



            for index, c in enumerate(coordinates_data):
                status = self.__apply(grayed, index, c)

                if times[index] is not None and self.same_status(statuses, index, status):
                    times[index] = None
                    continue

                if times[index] is not None and self.status_changed(statuses, index, status):
                    if position_in_seconds - times[index] >= MotionDetector.DETECT_DELAY:
                        statuses[index] = status
                        times[index] = None
                    continue

                if times[index] is None and self.status_changed(statuses, index, status):
                    times[index] = position_in_seconds

            for index, p in enumerate(coordinates_data):
                coordinates = self._coordinates(p)

                color = COLOR_GREEN if statuses[index] else COLOR_BLUE
                self.centers[p['id']] = draw_contours(new_frame, coordinates, str(p["id"] + 1), COLOR_WHITE, color)



            stats = Counter(statuses)
            vacant = stats[True]

            l3.configure(text=vacant)
            l3.update()
            l3.pack(side=LEFT)



            occupied = stats[False]
            font = open_cv.FONT_HERSHEY_SIMPLEX
            open_cv.putText(new_frame, 'Occupied: ' + str(occupied), (200, 35), font, 1, (0, 0, 255), 2,
                            open_cv.LINE_AA)
            open_cv.putText(new_frame, 'Vacant: ' + str(vacant), (10, 35), font, 1, (0, 255, 0), 2, open_cv.LINE_AA)
            indices = [str(i) for i, x in enumerate(statuses) if x == True]
            occupied1 = [str(i) for i, x in enumerate(statuses) if x == False]
            open_cv.putText(new_frame, 'vacant locations: ' + " ".join(indices), (21, 418), font, 1, (255, 0, 0), 2, open_cv.LINE_AA)
            for i in range(len(self.centers)):
                open_cv.putText(new_frame, self.waiting_time(self.time_log[i]), self.centers[i], font, 1, (255, 0, 0), 1,
                                open_cv.LINE_AA)
            l1.delete(0, 'end')
            for i in indices:
                i=int(i)+1
                l1.insert(END,'Slot No ' + str(i))
            l2.delete(0, 'end')
            for i in occupied1:
                i = int(i) + 1
                l2.insert(END, 'Slot No ' + str(i))

            cv2image = open_cv.cvtColor(new_frame, open_cv.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image).resize((990, 500))
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
        self.app.mainloop()
        capture.release()
        open_cv.destroyAllWindows()


    def __apply(self, grayed, index, p):
        coordinates = self._coordinates(p)
        logging.debug("points: %s", coordinates)

        rect = self.bounds[index]
        logging.debug("rect: %s", rect)

        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
        logging.debug("laplacian: %s", laplacian)

        coordinates[:, 0] = coordinates[:, 0] - rect[0]
        coordinates[:, 1] = coordinates[:, 1] - rect[1]
        mean = np.mean(np.abs(laplacian * self.mask[index]))
        print(mean, MotionDetector.LAPLACIAN)
        status = mean < MotionDetector.LAPLACIAN

        logging.debug("status: %s", status)

        return status

    @staticmethod
    def _coordinates(p):
        return np.array(p["coordinates"])

    @staticmethod
    def same_status(coordinates_status, index, status):
        # gets called when something gets changed
        return status == coordinates_status[index]

    @staticmethod
    def status_changed(coordinates_status, index, status):
        return status != coordinates_status[index]

    @staticmethod
    def exit_time(hr=0, mins=0.5):
        ts = time.time()
        wts = ts + hr * 60 * 60 + mins * 60
        return wts


    @staticmethod
    def waiting_time(t):
        return str(datetime.timedelta(seconds=int(t - time.time())))


class CaptureReadError(Exception):
    pass

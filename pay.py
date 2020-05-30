from number_plate import plate_number
import random
from receipts.receipt import gen_receipt
from single import Single
from tkinter import *
class Number:

    def final(self):
        imagelist = ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.jpg']
        rand_item = imagelist[random.randrange(len(imagelist))]
        number = plate_number('number_plate_data/'+rand_item)
        print(number)
        gen_receipt(number, Single.value)
        print("receipt generated")


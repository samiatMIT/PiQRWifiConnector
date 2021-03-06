import subprocess
from imutils.video import VideoStream
from pyzbar import pyzbar
import imutils
import time
import cv2

def connectingLoop():
    print("[INFO] starting video stream...")
    # vs = VideoStream(src=0).start() # for mac camera
    vs = VideoStream(usePiCamera=True).start() # for Pi camera
    time.sleep(2.0)

    while True:
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)
        # loop over the detected barcodes
        result = None
        barcodeFound = False
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            barcodeFound = True
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            connectWifi(barcodeData)
            result = checkWifi()
        if barcodeFound:
            if result is None or result[0] == 0:
                try:
                    print(result[1])
                except:
                    print(result)
                time.sleep(5)
                continue
            elif result[0] == 1:
                print(result[1])
                break
        
    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")
    cv2.destroyAllWindows()
    vs.stop()

def connectWifi(json): # when you make the QR Code, make a json of whats supposed to be INSIDE the 'network'.
    string  = '\nnetwork={\n\tssid="'+ str(json['ssid'])+'"\n\tpsk="'+str(json['psk']) +'"\n\tscan_ssid='+ str(json['scan_ssid']) +'\n\tkey_mgmt=' + str(json['key_mgmt']) + '\n}'
    with open('/etc/wpa_supplicant/wpa_supplicant.conf','a') as f:
        f.write(string)
    # with open('wpa_supplicant.txt','a') as f: # for debuggin purposes, file must be created before hand
    #     f.write(jsonString)


def checkWifi():
    ps = subprocess.Popen(['iwconfig'], stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep','ESSID'), stdin=ps.stdout)
        return 1,"Wifi Connected to: " + str(output) # this only print if connected
    except subprocess.CalledProcessError:
        return 0,'No Wireless Connection' # should run QR script here

if __name__ == "__main__":
    connectingLoop()
    # json = {'ssid':'Participant WIFI NAME', 'psk': 'Participant WIFI PASSWORD', 'scan_ssid':1, 'key_mgmt':'WPA-PSK'} 
    # string  = '\nnetwork={\n\tssid="'+ str(json['ssid'])+'"\n\tpsk="'+str(json['psk']) +'"\n\tscan_ssid='+ str(json['scan_ssid']) +'\n\tkey_mgmt=' + str(json['key_mgmt']) + '\n}'
    # print(string)
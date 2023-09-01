import cv2
import screeninfo
import time
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
RECEIVE_EXPORT_GATE_OUT_URL = os.getenv('RECEIVE_EXPORT_GATE_OUT_URL')
GATE_ID = os.getenv('GATE_ID')
LANE_ID = os.getenv('LANE_ID')
SCREEN_ID = int(os.getenv('SCREEN_ID'))
CAMERA_ID = int(os.getenv('CAMERA_ID'))

camera_id = CAMERA_ID
delay = 1
window_name = 'Auto Gate-Out'

# get the size of the screen
screen_id = SCREEN_ID
screen = screeninfo.get_monitors()[screen_id]
width, height = screen.width, screen.height

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)

                # font
font = cv2.FONT_HERSHEY_SIMPLEX
  
# org
org = (150, 50)
  
# fontScale
fontScale = 1
   
# Blue color in BGR
color = (255, 0, 0)
  
# Line thickness of 2 px
thickness = 2

color_topic =(255, 79, 51)

import requests
import json
async def send_data(license):
    print("Start sending...")
    try :
        starting_time = time.time()
        url = f'{RECEIVE_EXPORT_GATE_OUT_URL}?PARM_TRUCKNO={license}&PARM_GATE_ID={GATE_ID}&PARM_LANE_ID={LANE_ID}'
        # ------------------------------------------------
        r = requests.post(url, timeout=60)
        if r.status_code == 200 :
            r_json = r.json()
            print(r_json)
        else:
            print (f'Error on sending License :{license}')
        ending_time = time.time()-starting_time
        time.sleep(1)
        return f"{r_json['status']} : {r_json['msg']}"
    except Exception as e:
        ending_time = time.time()-starting_time
        return "Error.."
    
    
    print(f"Sending completed...{ending_time:.2f} seconds")

def print_env(text1,text2,frame):
    # setup text
    font = cv2.FONT_HERSHEY_PLAIN
    # get boundary of this text
    # textsize = cv2.getTextSize(text, font, 1, 2)[0]
    footer_start=430
    textX= 5
    textY = footer_start+20
    frame = cv2.putText(frame, text1, (textX, textY ), font, 1, (255, 255, 255), 1)
    textY = footer_start+40
    frame = cv2.putText(frame, text2, (textX, textY ), font, 1, (255, 255, 255), 1)
    # add text centered on image
    return frame

def print_text_topic(text,background_color,frame):
    # color = (0, 0, 255)
    frame = cv2.rectangle(frame, (0,0), (width-1,50), background_color, -1)
    # setup text
    font = cv2.FONT_HERSHEY_SIMPLEX
    # get boundary of this text
    textsize = cv2.getTextSize(text, font, 1, 2)[0]

    # get coords based on boundary
    # textX = (width - textsize[0]) / 2
    # textY = (50 + textsize[1]) / 2
    textX= 100
    textY = 40

    # add text centered on image
    return cv2.putText(frame, text, (textX, textY ), font, 1, (255, 255, 255), 2)

def print_text_footer(text,background_color,frame):
    # color = (0, 0, 255)
    footer_start=430
    frame = cv2.rectangle(frame, (0,footer_start), (width-1,footer_start+50), background_color, -1)
    # setup text
    font = cv2.FONT_HERSHEY_SIMPLEX
    # get boundary of this text
    
    textsize = cv2.getTextSize(text, font, 1, 2)[0]

    # get coords based on boundary
    # textX = (width - textsize[0]) / 2
    # textY = (50 + textsize[1]) / 2
    textX= 5
    textY = footer_start+40

    # add text centered on image
    return cv2.putText(frame, text, (textX, textY ), font, 1, (255, 255, 255), 2)

def detect_qr(sending_data):
    found_qr = False
    license = ''
    ret, frame = cap.read()

    # Add on Aug 29,2023 -- TO flip image to be more sense.
    # Fliping the image
    frame = cv2.flip(frame,1)

    # if sending_data :
    #     return print_text('Sending data...',(255,20,147),frame)

    # color= color = (0, 0, 255)
    # frame = cv2.rectangle(frame, (0,0), (width-1,50), color, -1)
    if ret:
        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                if s:
                    # Found QR code.
                    license = s
                    color = (0, 255, 0)
                    frame = cv2.putText(frame, f'License : {license}', p[0].astype(int), font, 
                                fontScale, color, thickness, cv2.LINE_AA)

                    # frame = cv2.putText(frame, f'License : {s}', org, font, 
                    #             fontScale, color_topic, thickness, cv2.LINE_AA)
                    
                    frame = print_text_topic(f'Sending data : {license}',color,frame)
                    # frame = print_text(msg,(0, 0, 255),frame)
                    found_qr = True
                   
                else:
                    color = (0, 0, 255)

                frame = cv2.polylines(frame, [p.astype(int)], True, color, thickness)
                
        else :
            if sending_data :
                msg = 'Sending data...'
            else:
                msg = 'Please scan QR code..'
            # frame = cv2.putText(frame, msg, org, font, 
            #                     fontScale, color_topic, thickness, cv2.LINE_AA)
            frame = print_text_topic(msg,(0, 0, 255),frame)
            # break
    return frame,found_qr,license

async def main():
    NUMBER_CAPTURE = 0
    SENDING_DATA = False
    send_data_result=''
    while True:
        # Capture image

        frame,found_qr,license = detect_qr(SENDING_DATA)
        # Show image

        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                            cv2.WINDOW_FULLSCREEN)
        if send_data_result :
            frame=print_text_footer(send_data_result,(84,84,84),frame)
        else:
            frame=print_env(RECEIVE_EXPORT_GATE_OUT_URL, f'{GATE_ID}:{LANE_ID}',frame)

        
        cv2.imshow(window_name, frame)
        # Found Image
        if found_qr:
            NUMBER_CAPTURE+=1
            if NUMBER_CAPTURE == 5:
                SENDING_DATA = True
                send_data_result = await send_data(license)
                SENDING_DATA = False
        else:
            # send_data_result=''
            NUMBER_CAPTURE=0
            SENDING_DATA = False
        

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break
    cv2.destroyWindow(window_name)

if __name__ == "__main__":
    asyncio.run(main())


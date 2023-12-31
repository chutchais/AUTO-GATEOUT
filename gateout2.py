import cv2
import screeninfo
import time
import asyncio
import os
from dotenv import load_dotenv
# Added on Oct 17,2023 -- CHange another QR reader library
from qreader import QReader


load_dotenv()
RECEIVE_EXPORT_GATE_OUT_URL = os.getenv('RECEIVE_EXPORT_GATE_OUT_URL')
GATE_ID = os.getenv('GATE_ID')
LANE_ID = os.getenv('LANE_ID')
SCREEN_ID = int(os.getenv('SCREEN_ID'))
CAMERA_ID = int(os.getenv('CAMERA_ID'))

# Added on Sep 1,2023 -- To show monitor screen
SHOW_MONITOR = os.getenv('SHOW_MONITOR')

camera_id = CAMERA_ID
delay = 1
window_name = 'Auto Gate-Out'
monitor_name = 'Monitor'

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


# Added on Oct 17,2023
qreader = QReader()

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
			# Added on Sep 5,2023 -- To play receive EIR sound
			if r_json['status'] == 'OK' :
				play_call_sound()
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


# First Version
# def detect_qr(sending_data):
# 	found_qr = False
# 	license = ''
# 	ret, frame = cap.read()
# 	# Add on Aug 29,2023 -- TO flip image to be more sense.
# 	# Fliping the image
# 	frame = cv2.flip(frame,1)
# 	data = qreader.detect_and_decode(image=frame,return_detections = True)
# 	# print(data)
# 	if not data[0] == ():
		
# 		if data[0][0] :
# 			# print(data[0])
# 			license = data[0][0]
# 			p = data[1][0]['bbox_xyxy']
# 			polygon_xy = data[1][0]['quad_xy']

# 			color = (0, 255, 0)
# 			frame = cv2.putText(frame, f'License : {license}', [p[0].astype(int),p[1].astype(int)], font, 
# 				fontScale, color, thickness, cv2.LINE_AA)
# 			frame = print_text_topic(f'Sending data : {license}',color,frame)
			
# 			found_qr = True
# 		else:
# 			color = (0, 0, 255)
# 			polygon_xy = data[1][0]['quad_xy']
		
# 		frame = cv2.polylines(frame,
# 						 [polygon_xy.astype(int)],
# 						 True, color, thickness)
# 			# frame = cv2.polylines(frame, [p[0].astype(int),p[1].astype(int),p[2].astype(int),p[3].astype(int)], True, color, thickness)
# 	else :
# 		if sending_data :
# 			msg = 'Sending data...'
# 		else:
# 			msg = 'Please scan QR code..'
# 		frame = print_text_topic(msg,(0, 0, 255),frame)

# 	return frame,found_qr,license

def detect_qr(sending_data):
	found_qr = False
	license = ''
	ret, frame = cap.read()
	# Add on Aug 29,2023 -- TO flip image to be more sense.
	# Fliping the image
	frame = cv2.flip(frame,1)
	data = qreader.detect(image=frame)
	# print(data)
	if not data == []:
		data = qreader.detect_and_decode(image=frame,return_detections = True)
		if not data[0] == () and data[0][0] :
			# print(data[0])
			license = data[0][0]
			p = data[1][0]['bbox_xyxy']
			polygon_xy = data[1][0]['quad_xy']

			color = (0, 255, 0)
			frame = cv2.putText(frame, f'License : {license}', [p[0].astype(int),p[1].astype(int)], font, 
				fontScale, color, thickness, cv2.LINE_AA)
			frame = print_text_topic(f'Sending data : {license}',color,frame)
			
			found_qr = True
		else:
			color = (0, 0, 255)
			polygon_xy = data[1][0]['quad_xy']
		
		frame = cv2.polylines(frame,
						 [polygon_xy.astype(int)],
						 True, color, thickness)
			# frame = cv2.polylines(frame, [p[0].astype(int),p[1].astype(int),p[2].astype(int),p[3].astype(int)], True, color, thickness)
	else :
		if sending_data :
			msg = 'Sending data...'
		else:
			msg = 'Please scan QR code..'
		frame = print_text_topic(msg,(0, 0, 255),frame)

	return frame,found_qr,license

import os
def play_call_sound():
	cwd = os.getcwd()
	sound_root_path = '%s\\sounds\\' % cwd
	try:
		from pathlib import Path
		file_wav = sound_root_path + 'success.wav'
		file_wav2 = sound_root_path + 'receive_eir.wav'
		sound_file = Path(file_wav)
		sound_file2 = Path(file_wav2)
		from playsound import playsound
		if sound_file.exists():
			playsound(file_wav) #Welcome sound
		if sound_file2.exists():
			playsound(file_wav2) #Welcome sound
	except:
		print ('Error on play_call_sound')

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

		# Added on Sep 1,2023 -- To show monitor screen
		if SHOW_MONITOR == 'yes' :
			cv2.imshow(monitor_name, frame)

		# Found Image
		if found_qr:
			NUMBER_CAPTURE+=1
			if NUMBER_CAPTURE == 2:
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


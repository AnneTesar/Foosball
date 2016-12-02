# USAGE
# python save_key_events.py --output output

# import the necessary packages
from pyimagesearch.keyclipwriter import KeyClipWriter
from imutils.video import VideoStream
from collections import deque
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2
import ffmpy
import json

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output directory")
ap.add_argument("-f", "--fps", type=int, default=30,
	help="FPS of output video")
ap.add_argument("-c", "--codec", type=str, default=('I', 'Y', 'U', 'V'),
	help="codec of output video") 
ap.add_argument("-b", "--buffer-size", type=int, default=32, #change this for longer clips i think
	help="buffer size of video clip writer")
ap.add_argument("-d", "--draw", type=int, default=0,
        help="1 to draw the line")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to
# warmup
print("[INFO] warming up camera...")
vs = VideoStream(2).start(); #0 for laptop webcam. 2 for USB webcam
time.sleep(2.0)

# define the lower and upper boundaries of the "green" ball in
# the HSV color space
# use range-detect to recalibrate for these
greenLower = (0, 0, 100)
greenUpper = (12, 255, 255)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer_size"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

# TODO add "duration" to highlights. Currently only passes start time
# and assumes a constant time for highlight duration.  
#class HighlightClass:
 #  def __init__(self, time, duration):
  #    self.time = time
   #   self.duration = duration
highlight_duration = 4;


# initialize key clip writer and the consecutive number of
# frames that have *not* contained any action
kcw = KeyClipWriter(bufSize=args["buffer_size"])
consecFrames = 0

# keep looping
while True:
        is_highlight = False;
	# grab the current frame, resize it, and initialize a
	# boolean used to indicate if the consecutive frames
	# counter should be updated
	frame = vs.read()
	frame = imutils.resize(frame, width=600)
	updateConsecFrames = True

	# blur the frame and convert it to the HSV color space
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use it
		# to compute the minimum enclosing circle
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		updateConsecFrames = radius <= 10
		M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the redius meets a minimum size
		if radius > 5:
			# reset the number of consecutive frames with
			# *no* action to zero and draw the circle
			# surrounding the object
			consecFrames = 0
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 0, 255), 2)
                        pts.appendleft(center)
                        
			# if we are not already recording, start recording
			if not kcw.recording:
				timestamp = datetime.datetime.now()
				video_name = timestamp.strftime("%Y%m%d-%H%M%S");
				p = "{}/{}.avi".format(args["output"],
					video_name)
				kcw.start(p, cv2.cv.CV_FOURCC(*args["codec"]),
					args["fps"])
				print("I'm recording now!")
				#START TIMER HERE
				time_start = time.time();
				#highlights = [HighlightClass(0, 1)]
				highlights = [0]

	# otherwise, no action has taken place in this frame, so
	# increment the number of consecutive frames that contain
	# no action
	if updateConsecFrames:
		consecFrames += 1

        # loop over the set of tracked points
	for i in np.arange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# check to see if enough points have been accumulated in
		# the buffer
		if counter >= 10 and i == 10 and pts[i-10] is not None:
			# compute the difference between the x and y
			# coordinates and re-initialize the direction
			# text variables
			dX = pts[i-10][0] - pts[i][0]
			dY = pts[i-10][1] - pts[i][1]
			(dirX, dirY) = ("", "")

			dX_prev = pts[i-20][0] - pts[i][0]

                        #if np.abs(dX) > 100 or np.abs(dY) > 100:
                                #print("fast movement");
                                #is_highlight = True;

                        #if shot on goal
                                #where it's heading, is that the goal?

                        #goal scored
                                #was headed toward the goal
                                #and now I don't see it anymore

                        if (dX < -400) :
                                print("shot across table, left");

                        if (dX > 400) :
                                print("shot across table, right");

                        if ((dX_prev ^ dX) < 0):
                                print("sign changed on dX");
                        


	# show the movement deltas and the direction of movement on
	# the frame
	if args["draw"]:
                thickness = int(np.sqrt(args["buffer_size"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
                cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

        if (is_highlight):
                # THIS TIME IS A HIGHLIGHT
                # only add to highlights if the last highlight was a while ago
                # TODO get rid of 0, or handle empty array, or something.
                this_highlight = time.time() - time_start
                #print (highlights[-1].time)
                #if it's only one away from time+duration of -1, add 1 to duration
                #if it's a separate highlight or just more of the same one?
                #if (this_highlight > highlights[-1].time + highlights[-1].duration) :
                 #       new_highlight = HighlightClass(this_highlight, 1)
                  #      highlights.append(new_highlight)
                if (this_highlight > highlights[-1] + highlight_duration):
                        highlights.append(time.time() - time_start)

	# update the key frame clip buffer
	kcw.update(frame)

	# if we are recording and reached a threshold on consecutive
	# number of frames with no action, stop recording the clip
	if kcw.recording and consecFrames == args["buffer_size"]:
                print("Stopped seeing ojbect")
                print("dx: " + dX + ", dy: " + dY); #TODO check this - can i use it to determine who scored?
		kcw.finish()
		
		# Get the output .avi, convert it to an .mp4 and put it where
		# the UI knows to look for it. 
		ff = ffmpy.FFmpeg(
                        inputs={args["output"]+ '/' + video_name + '.avi': None},
                        outputs={'C:/UwAmp/www/output_video/' + video_name + '.mp4': None})
                ff.run()
                
		#STOP THE TIMER, RESET IT, WHATEVER
		time_stop = time.time()
		video_length = time_stop - time_start;
		print(video_length) #TODO adjust FPS so this length actually matches the video length
		
		#Write the highlights to a text file
		with open('C:/UwAmp/www/output_highlights/' + video_name + '.json', 'w') as outfile:
                    json.dump(highlights, outfile)

	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	counter += 1

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break


# if we are in the middle of recording a clip, wrap it up
if kcw.recording:
	kcw.finish()

print ("all done")

# do a bit of cleanup
vs.stop()
cv2.destroyAllWindows()

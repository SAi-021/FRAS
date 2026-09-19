from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import usernameForm,DateForm,UsernameAndDateForm, DateForm_2
from django.contrib.auth.models import User
import cv2
import dlib
import imutils
from imutils import face_utils
from imutils.video import VideoStream
from imutils.face_utils import rect_to_bb
from imutils.face_utils import FaceAligner
import time
import os
import face_recognition 
import face_recognition_models 
from face_recognition.face_recognition_cli import image_files_in_folder
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import numpy as np
from django.contrib.auth.decorators import login_required
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import datetime
import seaborn as sns
import pandas as pd
from django.db.models import Count
#import mpld3
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from matplotlib import rcParams
import math
from users.models import Employee, Attendance,TimeTable
import calendar
from attendance.forms import edit_my_employee_profile as empEdit

mpl.use('Agg')

#Get the model
User = get_user_model()

#Utility Function
def total_number_employees():
	#qs=Employee.objects.all().filter(isAdmin=True)
	#print("total number of employ: ", len(qs) -1)
	qs=Employee.objects.all()
	print("total number of employ: ", len(qs)-1)
	return (len(qs) -1)
	# -1 to account for admin 

def employee_present_in_month(attendence):
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    lastDate = calendar.monthrange(current_year, current_month)[1]
    firstDay = datetime.datetime(current_year, current_month, 1)
    lastDay = datetime.datetime(current_year, current_month, lastDate)
    num_days_worked_month=attendence.filter(date__gte=firstDay).filter(date__lte=lastDay).order_by('-date')
    print( "Total number of days worked in a month: " ,len(num_days_worked_month))
    return len(num_days_worked_month)



def employees_present_today():
	today=datetime.date.today()
	qs=Attendance.objects.filter(date=today).filter(isPresent=True)
	print("total number PRESENT of employ: ", len(qs))
	return len(qs)

def username_present(username):
	if Employee.objects.filter(username=username).exists():
		return True
	
	return False

def update_attendance_in_db_in(present):
	today=datetime.date.today()
	time=datetime.datetime.now()
	print(present)
	for person in present:
		print(person,'line78')
		user=Employee.objects.get(username=person)
		print(user,'line80')
		try:
		   qs=Attendance.objects.filter(employee=user,date=today).first()

		   print(qs,'line82')
		   
		except :
			qs= None
			
		if qs is None:
			print(present[person])
			if present[person]==True:
						
						a=Attendance(employee=user,date=today,isPresent=True)
						a.save()
			else:
				
				a=Attendance(employee=user,date=today,isPresent=False)
				a.save()
		else:
			print(present[person],'cut')
			if present[person]==True:
				print(qs,'paste')
				qs.isPresent=True
				qs.save(update_fields=['isPresent'])
				print(qs,'copy')
		if present[person]==True:
			a=TimeTable(employee=user,date=today,logtime=time, isLogin=False)
			a.save()

def update_attendance_in_db_out(present):
	today=datetime.date.today()
	time=datetime.datetime.now()
	for person in present:
		user=Employee.objects.get(username=person)
		if present[person]==True:
			a=TimeTable(employee=user,date=today,logtime=time, isLogin=True)
			a.save()

def convert_hours_to_hours_mins(hours):
	
	h=int(hours)
	hours-=h
	m=hours*60
	m=math.ceil(m)
	return str(str(h)+ " hrs " + str(m) + "  mins")

def check_validity_times(times_all):
	print(times_all,'line 128')

	if(len(times_all)>0):
		print('line 131')
		sign=times_all.first().isLogin
		print(sign,'line 133')
	else:
		sign=True
		print(sign,'line 136')
	times_in=times_all.filter(isLogin=False)
	print(times_in,'line 138')
	times_out=times_all.filter(isLogin=True)
	print(times_out,'line 140')
	if(len(times_in)!=len(times_out)):
		print('line 142')
		sign=True
	break_hourss=0
	if(sign==True):
			print('line 146')
			check=False
			break_hourss=0
			return (check,break_hourss)
	prev=True
	prev_time=times_all.first().logtime

	for obj in times_all:
		curr=obj.isLogin
		
		if(curr==prev):
			print(curr,'line 157')
			check=False
			break_hourss=0
			return (check,break_hourss)
		if(curr==False):
			curr_time=obj.logtime
			to=curr_time
			ti=prev_time
			break_time=((to-ti).total_seconds())/3600
			break_hourss+=break_time
			print(break_hourss,'line 167')


		else:
			prev_time=obj.logtime

		prev=curr

	return (True,break_hourss)

def hours_vs_employee_given_date(present_qs,time_qs):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	df_username=[]
	qs=present_qs

	for obj in qs:
		user=obj.employee
		print(user,'line186')
		times_in=time_qs.filter(employee=user).filter(isLogin=False)
		times_out=time_qs.filter(employee=user).filter(isLogin=True)
		times_all=time_qs.filter(employee=user)
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.hours=0
		if (len(times_in)>0):			
			obj.time_in=times_in.first().logtime
			print(obj.time_in,'line196')
		if (len(times_out)>0):
			obj.time_out=times_out.last().logtime
			print(obj.time_out,'line199')
		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
			print(obj.hours,'line205')
		else:
			obj.hours=0
		(check,break_hourss)= check_validity_times(times_all)
		if check:
			obj.break_hours=break_hourss


		else:
			obj.break_hours=0
			print(obj.break_hours,'line 215')
		
		df_hours.append(obj.hours)
		df_username.append(user.username)
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)

	



	#df = read_frame(qs)	
	#df['hours']=df_hours
	#df['username']=df_username
	#df["break_hours"]=df_break_hours


	#sns.barplot(data=df,x='username',y='hours')
	sns.barplot(data=None,x=None,y=None)
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	plt.savefig('./attendance/static/recognition/img/attendance_graphs/hours_vs_employee/1.png')
	plt.close()
	start1 = datetime.date(2022, 3, 15)
	end1 = datetime.date(2022, 4, 16)
	days = np.busday_count(start1, end1)
	print('Number of business days is:', days)
    
	return qs

def hours_vs_date_given_employee(present_qs,time_qs,admin=True):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	qs=present_qs

	for obj in qs:
		date=obj.date
		times_in=time_qs.filter(date=date).filter(isLogin=False).order_by('logtime')
		times_out=time_qs.filter(date=date).filter(isLogin=True).order_by('logtime')
		times_all=time_qs.filter(date=date).order_by('logtime')
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.break_hours=0
		if (len(times_in)>0):			
			obj.time_in=times_in.first().logtime
			
		if (len(times_out)>0):
			obj.time_out=times_out.last().logtime

		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
		

		else:
			obj.hours=0

		(check,break_hourss)= check_validity_times(times_all)
		if check:
			obj.break_hours=break_hourss


		else:
			obj.break_hours=0


		
		df_hours.append(obj.hours)
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)
			
	
	
	
	#df = read_frame(qs)	
	#df["hours"]=df_hours
	#df["break_hours"]=df_break_hours
	#sns.barplot(data=df,x=df_hours ,y=df_break_hours)
		
	sns.barplot(data=None,x=None ,y=None)
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	if(admin):
		plt.savefig('./attendance/static/recognition/img/attendance_graphs/hours_vs_date/1.png')
		plt.close()
	else:
		plt.savefig('./attendance/static/recognition/img/attendance_graphs/employee_login/1.png')
		plt.close()
	return qs

def predict(face_aligned,svc,threshold=0.7):
	face_encodings=np.zeros((1,128))
	try:
		x_face_locations=face_recognition.face_locations(face_aligned)
		faces_encodings=face_recognition.face_encodings(face_aligned,known_face_locations=x_face_locations)
		if(len(faces_encodings)==0):
			return ([-1],[0])

	except:

		return ([-1],[0])

	prob=svc.predict_proba(faces_encodings)
	result=np.where(prob[0]==np.amax(prob[0]))
	if(prob[0][result[0]]<=threshold):
		return ([-1],prob[0][result[0]])

	return (result[0],prob[0][result[0]])

def create_dataset(username):
	id = username
	if(os.path.exists('face_recognition_data/training_dataset/{}/'.format(id))==False):
		os.makedirs('face_recognition_data/training_dataset/{}/'.format(id))
	directory='face_recognition_data/training_dataset/{}/'.format(id)

	# Detect face
	#Loading the HOG face detector and the shape predictpr for allignment

	print("[INFO] Loading the facial detector")
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor('face_recognition_data/shape_predictor_68_face_landmarks.dat')   #Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
	fa = FaceAligner(predictor , desiredFaceWidth = 96)
	#capture images from the webcam and process and detect the face
	# Initialize the video stream
	print("[INFO] Initializing Video stream")
	vs = VideoStream(src=0).start()
	#time.sleep(2.0) ####CHECK######

	# Our identifier
	# We will put the id here and we will store the id with a face, so that later we can identify whose face it is
	
	# Our dataset naming counter
	sampleNum = 0
	# Capturing the faces one by one and detect the faces and showing it on the window
	while(True):
		# Capturing the image
		#vs.read each frame
		frame = vs.read()
		#Resize each image
		frame = imutils.resize(frame ,width = 800)
		#the returned img is a colored image but for the classifier to work we need a greyscale image
		#to convert
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		#To store the faces
		#This will detect all the images in the current frame, and it will return the coordinates of the faces
		#Takes in image and some other parameter for accurate result
		faces = detector(gray_frame,0)
		#In above 'faces' variable there can be multiple faces so we have to get each and every face and draw a rectangle around it.
		
		
			


		for face in faces:
			print("inside for loop")
			(x,y,w,h) = face_utils.rect_to_bb(face)

			face_aligned = fa.align(frame,gray_frame,face)
			# Whenever the program captures the face, we will write that is a folder
			# Before capturing the face, we need to tell the script whose face it is
			# For that we will need an identifier, here we call it id
			# So now we captured a face, we need to write it in a file
			sampleNum = sampleNum+1
			# Saving the image dataset, but only the face part, cropping the rest
			
			if face is None:
				print("face is none")
				continue


			

			cv2.imwrite(directory+'/'+str(sampleNum)+'.jpg'	, face_aligned)
			face_aligned = imutils.resize(face_aligned ,width = 400)
			#cv2.imshow("Image Captured",face_aligned)
			# @params the initial point of the rectangle will be x,y and
			# @params end point will be x+width and y+height
			# @params along with color of the rectangle
			# @params thickness of the rectangle
			cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),1)
			# Before continuing to the next loop, I want to give it a little pause
			# waitKey of 100 millisecond
			cv2.waitKey(50)

		#Showing the image in another window
		#Creates a window with window name "Face" and with the image img
		cv2.imshow("Add Images",frame)
		#Before closing it we need to give a wait command, otherwise the open cv wont work
		# @params with the millisecond of delay 1
		cv2.waitKey(1)
		#To get out of the loop
		if(sampleNum>50):
			break
	
	#Stoping the videostream
	vs.stop()
	# destroying all the windows
	cv2.destroyAllWindows()
	print("add pic complete")
	

def vizualize_Data(embedded, targets,):
	
	X_embedded = TSNE(n_components=2).fit_transform(embedded)

	for i, t in enumerate(set(targets)):
		idx = targets == t
		plt.scatter(X_embedded[idx, 0], X_embedded[idx, 1], label=t)

	plt.legend(bbox_to_anchor=(1, 1));
	# plt.legend(bbox_to_anchor=(1, 1))
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()	
	plt.savefig('./attendance/static/recognition/img/training_visualisation.png')
	plt.close()


# Create your views here.

#HOME 
def home(request):
    all =User.objects.all()
    print("yes")
    print(all[0])
    all1 =Employee.objects.all().values()
    print("yes")
    print(all1[0]['isAdmin'])
    template = loader.get_template('recognition/home.html')  
    return HttpResponse(template.render())

#ATTENDANCE LOG IN
def mark_your_attendance_out(request):
	detector = dlib.get_frontal_face_detector()
	
	predictor = dlib.shape_predictor('face_recognition_data/shape_predictor_68_face_landmarks.dat')   #Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
	svc_save_path="face_recognition_data/svc.sav"	
		
	with open(svc_save_path, 'rb') as f:
			svc = pickle.load(f)
	fa = FaceAligner(predictor , desiredFaceWidth = 96)
	encoder=LabelEncoder()
	encoder.classes_ = np.load('face_recognition_data/classes.npy')

	faces_encodings = np.zeros((1,128))
	no_of_faces = len(svc.predict_proba(faces_encodings)[0])
	count = dict()
	present = dict()
	log_time = dict()
	start = dict()
	for i in range(no_of_faces):
		count[encoder.inverse_transform([i])[0]] = 0
		present[encoder.inverse_transform([i])[0]] = False

	vs = VideoStream(src=0).start()
	
	sampleNum = 0
	
	while(True):
		
		frame = vs.read()
		
		frame = imutils.resize(frame ,width = 800)
		
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		faces = detector(gray_frame,0)
		
		for face in faces:
			print("INFO : inside for loop")
			(x,y,w,h) = face_utils.rect_to_bb(face)

			face_aligned = fa.align(frame,gray_frame,face)
			cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),1)
					
			
			(pred,prob)=predict(face_aligned,svc)
			if(pred!=[-1]):
				
				person_name=encoder.inverse_transform(np.ravel([pred]))[0]
				pred=person_name
				if count[pred] == 0:
					start[pred] = time.time()
					count[pred] = count.get(pred,0) + 1

				if count[pred] == 4 and (time.time()-start[pred]) > 1.5:
					 count[pred] = 0
				else:
				#if count[pred] == 4 and (time.time()-start) <= 1.5:
					present[pred] = True
					log_time[pred] = datetime.datetime.now()
					count[pred] = count.get(pred,0) + 1
					print(pred, present[pred], count[pred])
				cv2.putText(frame, str(person_name)+ str(prob), (x+6,y+h-6), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

			else:
				person_name="unknown"
				cv2.putText(frame, str(person_name), (x+6,y+h-6), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

			
			
			#cv2.putText()
			# Before continuing to the next loop, I want to give it a little pause
			# waitKey of 100 millisecond
			#cv2.waitKey(50)

		#Showing the image in another window
		#Creates a window with window name "Face" and with the image img
		cv2.imshow("Mark Attendance- Out - Press q to exit",frame)
		#Before closing it we need to give a wait command, otherwise the open cv wont work
		# @params with the millisecond of delay 1
		#cv2.waitKey(1)
		#To get out of the loop
		key=cv2.waitKey(50) & 0xFF
		if(key==ord("q")):
			break
	
	#Stoping the videostream
	vs.stop()

	# destroying all the windows
	cv2.destroyAllWindows()
	update_attendance_in_db_out(present)
	return redirect('home')


#ATTENDANCE LOG OUT
def mark_your_attendance(request):
		
	detector = dlib.get_frontal_face_detector()
	
	predictor = dlib.shape_predictor('face_recognition_data/shape_predictor_68_face_landmarks.dat')   #Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
	svc_save_path="face_recognition_data/svc.sav"	


		
			
	with open(svc_save_path, 'rb') as f:
			svc = pickle.load(f)
	fa = FaceAligner(predictor , desiredFaceWidth = 96)
	encoder=LabelEncoder()
	encoder.classes_ = np.load('face_recognition_data/classes.npy')


	faces_encodings = np.zeros((1,128))
	no_of_faces = len(svc.predict_proba(faces_encodings)[0])
	count = dict()
	present = dict()
	log_time = dict()
	start = dict()
	for i in range(no_of_faces):
		count[encoder.inverse_transform([i])[0]] = 0
		present[encoder.inverse_transform([i])[0]] = False

	

	vs = VideoStream(src=0).start()
	
	sampleNum = 0
	
	while(True):
		
		frame = vs.read()
		
		frame = imutils.resize(frame ,width = 800)
		
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		faces = detector(gray_frame,0)
		
		
		for face in faces:
			print("INFO : inside for loop")
			(x,y,w,h) = face_utils.rect_to_bb(face)

			face_aligned = fa.align(frame,gray_frame,face)
			cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),1)
					
			
			(pred,prob)=predict(face_aligned,svc)
			

			
			if(pred!=[-1]):
				
				person_name=encoder.inverse_transform(np.ravel([pred]))[0]
				pred=person_name
				if count[pred] == 0:
					start[pred] = time.time()
					count[pred] = count.get(pred,0) + 1

				if count[pred] == 4 and (time.time()-start[pred]) > 1.2:
					 count[pred] = 0
				else:
				#if count[pred] == 4 and (time.time()-start) <= 1.5:
					present[pred] = True
					log_time[pred] = datetime.datetime.now()
					count[pred] = count.get(pred,0) + 1
					print(pred, present[pred], count[pred])
				cv2.putText(frame, str(person_name)+ str(prob), (x+6,y+h-6), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

			else:
				person_name="unknown"
				cv2.putText(frame, str(person_name), (x+6,y+h-6), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

			
			
			#cv2.putText()
			# Before continuing to the next loop, I want to give it a little pause
			# waitKey of 100 millisecond
			#cv2.waitKey(50)

		#Showing the image in another window
		#Creates a window with window name "Face" and with the image img
		cv2.imshow("Mark Attendance - In - Press q to exit",frame)
		#Before closing it we need to give a wait command, otherwise the open cv wont work
		# @params with the millisecond of delay 1
		#cv2.waitKey(1)
		#To get out of the loop
		key=cv2.waitKey(50) & 0xFF
		if(key==ord("q")):
			break
	
	#Stoping the videostream
	vs.stop()

	# destroying all the windows
	cv2.destroyAllWindows()
	update_attendance_in_db_in(present)
	return redirect('home')

#DASHBOARD
@login_required
def dashboard2(request):
	print(request.user.username)
	if(request.user.username=='admin'):
		print("admin")
		return render(request, 'recognition/ad_dashboard.html')
	else:
		print("not admin")

		return render(request,'recognition/StudentsLayout.html')
	
#ADD PHOTOS
@login_required
def add_photos(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	if request.method=='POST':
		form=usernameForm(request.POST)
		data = request.POST.copy()
		username=data.get('username')
		if username_present(username):
			create_dataset(username)
			messages.success(request, f'Dataset Created')
			return redirect('add-photos')
		else:
			messages.warning(request, f'No such username found. Please register employee first.')
			return redirect('dashboard')


	else:
		

			form=usernameForm()
			return render(request,'recognition/add_photos.html', {'form' : form})
	
#TRAIN
@login_required
def train(request):
	if request.user.username!='admin':
		return redirect('not-authorised')

	training_dir='face_recognition_data/training_dataset'
	
	
	
	count=0
	for person_name in os.listdir(training_dir):
		curr_directory=os.path.join(training_dir,person_name)
		
		print(curr_directory)
		print()
		
		if not os.path.isdir(curr_directory):
			continue
		for imagefile in image_files_in_folder(curr_directory):
			count+=1

	X=[]
	y=[]
	i=0


	for person_name in os.listdir(training_dir):
		print(str(person_name))
		curr_directory=os.path.join(training_dir,person_name)
		if not os.path.isdir(curr_directory):
			continue
		for imagefile in image_files_in_folder(curr_directory):
			print(str(imagefile))
			image=cv2.imread(imagefile)
			try:
				X.append((face_recognition.face_encodings(image)[0]).tolist())
				y.append(person_name)
				i+=1
			except:
				print("removed")
				os.remove(imagefile)

			


	targets=np.array(y)
	encoder = LabelEncoder()
	encoder.fit(y)
	y=encoder.transform(y)
	X1=np.array(X)
	print("shape: "+ str(X1.shape))
	np.save('face_recognition_data/classes.npy', encoder.classes_)
	svc = SVC(kernel='linear',probability=True)
	svc.fit(X1,y)
	svc_save_path="face_recognition_data/svc.sav"
	with open(svc_save_path, 'wb') as f:
		pickle.dump(svc,f)

	
	vizualize_Data(X1,targets)
	
	messages.success(request, f'Training Complete.')

	return render(request,"recognition/train.html")
	
#ADMIN View attendance home 
@login_required
def view_attendance_home(request):
	total_num_of_emp=total_number_employees()
	emp_present_today=employees_present_today()
	
	return render(request,"recognition/view_attendance_home.html", {'total_num_of_emp' : total_num_of_emp, 'emp_present_today': emp_present_today})

#ADMIN VIEW ATTENDANCE BY EMPLOYEE NAMES
@login_required
def view_attendance_employee(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	time_qs=None
	present_qs=None
	qs=None

	if request.method=='POST':
		form=UsernameAndDateForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data.get('username')
			if username_present(username):
				
				u=Employee.objects.get(username=username)
				
				time_qs=TimeTable.objects.filter(employee=u)
				present_qs=Attendance.objects.filter(employee=u)
				date_from=form.cleaned_data.get('date_from')
				date_to=form.cleaned_data.get('date_to')
				
				if date_to < date_from:
					messages.warning(request, f'Invalid date selection.')
					return redirect('view-attendance-employee')
				else:
					

					time_qs=time_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
					present_qs=present_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
					
					if (len(time_qs)>0 or len(present_qs)>0):
						qs=hours_vs_date_given_employee(present_qs,time_qs,admin=True)
						return render(request,'recognition/view_attendance_employee.html', {'form' : form, 'qs' :qs})
					else:
						#print("inside qs is None")
						messages.warning(request, f'No records for selected duration.')
						return redirect('view-attendance-employee')
            
			else:
				print("invalid username")
				messages.warning(request, f'No such username found.')
				return redirect('view-attendance-employee')


	else:
		

			form=UsernameAndDateForm()
			return render(request,'recognition/view_attendance_employee.html', {'form' : form, 'qs' :qs})
	
#ADMIN VIEW ATTENDANCE BY DATE
@login_required
def view_attendance_date(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	qs=None
	time_qs=None
	present_qs=None


	if request.method=='POST':
		form=DateForm(request.POST)
		if form.is_valid():
			date=form.cleaned_data.get('date')
			print("date:"+ str(date))
			time_qs=TimeTable.objects.filter(date=date)
			print(time_qs,'line 815')
			present_qs=Attendance.objects.filter(date=date)
			print(present_qs,'line817')
			if(len(time_qs)>0 or len(present_qs)>0):
				qs=hours_vs_employee_given_date(present_qs,time_qs)


				return render(request,'recognition/view_attendance_date.html', {'form' : form,'qs' : qs })
			else:
				messages.warning(request, f'No records for selected date.')
				return redirect('view-attendance-date')

	else:
		

			form=DateForm()
			return render(request,'recognition/view_attendance_date.html', {'form' : form, 'qs' : qs})
	
#EMPLOYE 
@login_required
def view_my_attendance_employee_login(request):
	if request.user.username=='admin':
		return redirect('not-authorised')
	qs=None
	time_qs=None
	present_qs=None
	if request.method=='POST':
		form=DateForm_2(request.POST)
		if form.is_valid():
			u=request.user
			time_qs=TimeTable.objects.filter(employee=u)
			present_qs=Attendance.objects.filter(employee=u)
			date_from=form.cleaned_data.get('date_from')
			date_to=form.cleaned_data.get('date_to')
			if date_to < date_from:
					messages.warning(request, f'Invalid date selection.')
					return redirect('view-my-attendance-employee-login')
			else:
					

					time_qs=time_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
					present_qs=present_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
				
					if (len(time_qs)>0 or len(present_qs)>0):
						qs=hours_vs_date_given_employee(present_qs,time_qs,admin=False)
						print(qs)
						return render(request,'recognition/view_my_attendance_employee_login.html', {'form' : form, 'qs' :qs})
					else:
						
						messages.warning(request, f'No records for selected duration.')
						return redirect('view-my-attendance-employee-login')
	else:
		

			form=DateForm_2()
			return render(request,'recognition/view_my_attendance_employee_login.html', {'form' : form, 'qs' :qs})
	
#EMPLOYE PROFILE
@login_required
def view_my_employee_profile(request):
    qs=Employee.objects.get(username=request.user.username)
    s=Employee.objects.filter(username=request.user.username).values()
    today=datetime.date.today()
    employeeAttendence=Attendance.objects.filter(employee=qs).filter(isPresent=True)
    num_days_worked_month = employee_present_in_month(employeeAttendence)
    a=employeeAttendence.filter(date=today).exists()
    print("878")
    print(num_days_worked_month)
    return render(request,'recognition/employeeProfile.html',{'qs':qs, 'a':a, 'days': num_days_worked_month})
    
#EDIT PROFILE
# update view for details
@login_required
def edit_my_employee_profile(request,id):
    if request.method == 'POST':
        profile_form = empEdit(request.POST, request.FILES, instance=request.user)
        print('test')
        print(profile_form)
        
        
        if  profile_form.is_valid():
            
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            print('tt')
            return redirect('view-my-employee-profile')
        
    else:
        
        profile_form = empEdit(instance=request.user)
         

    return render(request, 'recognition/edit_employee_profile.html', {'profile_form': profile_form})







    
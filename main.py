'''#############################################################
################# DXF continuous line to gcode #################
################# Made by Justin Adrian Halim  #################
################# For 3D Printing Concrete     #################
#############################################################'''
##--------------------------------------------------------------------------------------------##
Current_Version = '2.1'
#Version 1.1: Added nearestpoint function
#Version 1.2: Added double wall feature
#Version 1.2.1: Fixed doubled points during pathing
#Version 1.2.2: Fixed double wall separation bug
#Version 1.3: Adding tearing movement?
#Version 2.0: Complete overhaul with Tkinter and RawTurtle
#Version 2.1: Added RawTurtle speed option, restrict some entries to pseudo - float only, minor code cleaning
##--------------------------------------------------------------------------------------------##

import tkinter as tk
from tkinter import filedialog
import math
import turtle
from DefaultValues import create_instance_default_values

#Creating the window using tkinter
window = tk.Tk()
window.title("Wall Nutz xd something app" + "   Version: " + str(Current_Version))
window.minsize(width=960, height=540)
window.iconbitmap("ico.ico")

#Setting up variables and default values for entries.
namevar = tk.StringVar()
double_wall = tk.StringVar()
wall_separation = tk.StringVar()
x_startpoint = tk.StringVar()
y_startpoint = tk.StringVar()
lyr_n = tk.StringVar()
lyr_h = tk.StringVar()
rawspeed = tk.StringVar()
default_values = create_instance_default_values()

#Setting up an easy way to call a StringVar object from their _name. Useful to reduce repetitive trace functions
string_vars = {
    wall_separation._name: wall_separation,
    x_startpoint._name: x_startpoint,
    y_startpoint._name: y_startpoint,
    lyr_n._name: lyr_n,
    lyr_h._name: lyr_h
}

#Set up some global variables
filename = None
filepath = None

##########################################################################
##########################################################################

#Get default values and insert it into the entries
def Load_Default_Values():
    double_wall_entry.delete(0, tk.END)
    double_wall_entry.insert(0, default_values.get_defdoublewall())
    wall_separation_entry.delete(0, tk.END)
    if 't' in double_wall.get() or 'T' in double_wall.get() or 'y' in double_wall.get() or 'Y' in double_wall.get():
        wall_separation_entry.insert(0, default_values.get_defwallsep())
    x_startpoint_entry.delete(0, tk.END)
    x_startpoint_entry.insert(0, default_values.get_defstartx())
    y_startpoint_entry.delete(0, tk.END)
    y_startpoint_entry.insert(0, default_values.get_defstarty())
    lyr_n_entry.delete(0, tk.END)
    lyr_n_entry.insert(0, default_values.get_deflyr_n())
    lyr_h_entry.delete(0, tk.END)
    lyr_h_entry.insert(0, default_values.get_deflyr_h())

#Check if all entries are filled
def Check_if_values_filled(variable_list_to_check):
    for i in variable_list_to_check:
        #print(i)
        if i.get() == '':
            return False
    return True

#Testing messagebox (later use)
def Submitappend():
    tk.messagebox.showinfo(message="Name is: "+ str(namevar.get()), title='testing123')

#Restrict Double Wall entry to only one character, and if it is 't' or 'y', enable wall separation entry
def double_wall_func(var, index, mode):
    if len(double_wall.get()) > 1:
        double_wall.set(double_wall.get()[-1])

    if 't' in double_wall.get() or 'T' in double_wall.get() or 'y' in double_wall.get() or 'Y' in double_wall.get():
        wall_separation_entry.config(state=tk.NORMAL)

    else:
        wall_separation_entry.config(state=tk.DISABLED)
        wall_separation.set('')
double_wall.trace_add('write',double_wall_func)

#Used to restrict RawTurtle speed to the integer values in the board() function
def raw_speed_func(var, index, mode):
    if rawspeed.get() == '':
        pass
    elif ord(rawspeed.get()[-1]) > 57:
        rawspeed.set(rawspeed.get()[:-1])
    elif ord(rawspeed.get()[-1]) < 48:
        rawspeed.set(rawspeed.get()[:-1])
    elif int(rawspeed.get()) >= 99:
        rawspeed.set(str(int(rawspeed.get()) % 100))
rawspeed.trace_add('write',raw_speed_func)

#Restrict float variables. only 0 - 9, and maximum one '.' is allowed
def float_check_func(var, index, mode):
    var_value = window.globalgetvar(var)

    if var_value == '':
        pass
    elif string_vars[var].get()[-1] == '.':
        if '.' in string_vars[var].get()[:-1]:
            string_vars[var].set(string_vars[var].get()[:-1])
    elif ord(string_vars[var].get()[-1]) > 57:
        string_vars[var].set(string_vars[var].get()[:-1])
    elif ord(string_vars[var].get()[-1]) < 48:
       string_vars[var].set(string_vars[var].get()[:-1])

#Variables that should be float variables
wall_separation.trace_add('write',float_check_func)
x_startpoint.trace_add('write',float_check_func)
y_startpoint.trace_add('write',float_check_func)
lyr_n.trace_add('write',float_check_func)
lyr_h.trace_add('write',float_check_func)


##########################################################################
##########################################################################

#Behaviour when process is clicked. Sorting matrix containing line data and return the path that the printer and turtle should follow
def StartProcess():
    from readdxf import openfile, pathing, nearestpoint

    if 't' in double_wall.get() or 'T' in double_wall.get() or 'y' in double_wall.get() or 'Y' in double_wall.get():
        variable_list_to_check = [double_wall, wall_separation,x_startpoint,y_startpoint,lyr_n,lyr_h]

    else:
        variable_list_to_check = [double_wall,x_startpoint,y_startpoint,lyr_n,lyr_h]

    if Check_if_values_filled(variable_list_to_check) == False:
        empty_entry_reminder.config(text='Error: Please fill in all entries', fg='red')
    else:
        empty_entry_reminder.config(text='')

    global pathlist
    global startpoint

    file = open(filepath)
    vectorlist = openfile(file)
    startpoint = [float(x_startpoint.get()), float(y_startpoint.get())]
    pathlist, startpoint = nearestpoint(vectorlist, startpoint)
    pathlist = pathing(pathlist, startpoint)

    #These variables are used to make sure the model is centred in the RawTurtle window and not exceeding its borders
    global pre_coord_path
    pre_coord_path = list()
    if pathlist != []:
        pre_coord_path.append(pathlist[0][:2])
        for i in pathlist:
            pre_coord_path.append(i[2:])
        
        max_x = pre_coord_path[0][0]
        min_x = pre_coord_path[0][0]
        max_y = pre_coord_path[0][1]
        min_y = pre_coord_path[0][1]
        for i in pre_coord_path:
            if i[0] > max_x:
                max_x = i[0]
            if i[0] < min_x:
                min_x = i[0]
            if i[1] > max_y:
                max_y = i[1]
            if i[1] < min_y:
                min_y = i[1]

        global model_size, model_centre
        model_centre = [(max_x + min_x) / 2, (max_y + min_y) / 2]
        model_size = [max_x - min_x, max_y - min_y]
    
    #Enable play and export button once processing is finished
    play_button.config(state=tk.NORMAL)
    export_button.config(state=tk.NORMAL)

#Behaviour when browse button is clicked. We want to browse a dxf file to convert
def StartBrowse():
    #Disable process, export, and play button before browsing is successful.
    process_button.config(state=tk.DISABLED)
    export_button.config(state=tk.DISABLED)
    play_button.config(state=tk.DISABLED)

    #Creates a browse window and set up variables to be processed
    tempdir = filedialog.askopenfile(title='Please select a dxf file', filetypes=[("DXF files","*.dxf")])
    global filename
    global filepath

    if tempdir != None:
        a = 0
        i = 0
        while i < len(tempdir.name):
            if tempdir.name[i] == '/' :
                a = i
            i+=1
        filename = tempdir.name[a+1:]
        filename_label.config(text='Selected file: ' + filename)
        filepath = tempdir.name

        #Successful browse, enables process button
        if filename[-3:] == 'dxf':
            process_button.config(state=tk.NORMAL)
        
        else:
            print('please select dxf file')

#Behaviour when export button is clicked. Turns the printing path into a GCode with the appropriate amount of layers, layer height, and double wall behaviour
def StartExport():
    from readdxf import turn_to_gcode
    import os

    if 't' in double_wall.get() or 'T' in double_wall.get() or 'y' in double_wall.get() or 'Y' in double_wall.get(): 
        doublewallstate = True
    else:
        doublewallstate = False
        wall_separation.set('0')

    #Define the GCode file name and destination folder
    filecreate = filename[:-4] + ".gcode"
    destination = os.path.dirname(__file__) + '/' + default_values.get_destfoldname() + '/'

    gcoded = turn_to_gcode(filecreate, destination, pathlist, lyr_n=lyr_n.get(), lyr_h=lyr_h.get(), startpoint=startpoint, 
                           doublewall=doublewallstate, wall_separation=wall_separation.get(), Current_Version=Current_Version)

    #Confirmation of a successful export
    empty_entry_reminder.config(text=filecreate + ' created', fg='black')
    print("File " + str(filecreate) + " created")
    print('File directory: ' + destination)

##########################################################################
##########################################################################

#frame1 is the left frame, frame2 is the right frame
frame1 = tk.Frame(window)
frame2 = tk.Frame(window)

#position and behaviour of frame1 and frame2 when window size changes
frame1.grid(row=0, column=0,sticky='news', padx=50)
frame2.grid(row=0, column=1,sticky='news')
window.columnconfigure(0,weight=1)
window.columnconfigure(1,weight=2)
window.rowconfigure(0,weight=1)

##### Left Frame #####

#Top Label and a button to load default values into the entries
left_side_label = tk.Label(frame1, text='Values')
left_side_label.grid(row=0,column=1,sticky='W')
load_default_button = tk.Button(frame1, text='Load Default Values', command=Load_Default_Values)
load_default_button.grid(row=0,column=1,sticky='E')

#Double Wall label and entry
left_frame1 = tk.Frame(frame1)
left_frame1.grid(row=2,column=1,sticky='news',columnspan=2)
double_wall_label = tk.Label(left_frame1, text='Double Wall? (T/F)')
double_wall_entry = tk.Entry(left_frame1, textvariable=double_wall)
double_wall_label.grid(row=0,column=0,sticky='W')
double_wall_entry.grid(row=0,column=1,sticky='E')
left_frame1.columnconfigure(0, weight=1)
left_frame1.columnconfigure(1, weight=1)
left_frame1.rowconfigure(0,weight=1)

#Wall separation label and entry
left_frame2 = tk.Frame(frame1)
left_frame2.grid(row=4,column=1,sticky='news',columnspan=2)
wall_separation_label = tk.Label(left_frame2, text='Wall Separation (mm)')
wall_separation_entry = tk.Entry(left_frame2, textvariable=wall_separation)
wall_separation_label.grid(row=0,column=0,sticky='W')
wall_separation_entry.grid(row=0,column=1,sticky='E')
left_frame2.columnconfigure(0, weight=1)
left_frame2.columnconfigure(1, weight=1)
left_frame2.rowconfigure(0,weight=1)
wall_separation_entry.config(state=tk.DISABLED)

#x_startpoint label and entry
left_frame3 = tk.Frame(frame1)
left_frame3.grid(row=6,column=1,sticky='news',columnspan=2)
x_startpoint_label = tk.Label(left_frame3, text='X - Start Point (mm)')
x_startpoint_entry = tk.Entry(left_frame3, textvariable=x_startpoint)
x_startpoint_label.grid(row=0,column=0,sticky='W')
x_startpoint_entry.grid(row=0,column=1,sticky='E')
left_frame3.columnconfigure(0, weight=1)
left_frame3.columnconfigure(1, weight=1)
left_frame3.rowconfigure(0,weight=1)

#y_startpoint label and entry
left_frame4 = tk.Frame(frame1)
left_frame4.grid(row=8,column=1,sticky='news',columnspan=2)
y_startpoint_label = tk.Label(left_frame4, text='Y - Start Point (mm)')
y_startpoint_entry = tk.Entry(left_frame4, textvariable=y_startpoint)
y_startpoint_label.grid(row=0,column=0,sticky='W')
y_startpoint_entry.grid(row=0,column=1,sticky='E')
left_frame4.columnconfigure(0, weight=1)
left_frame4.columnconfigure(1, weight=1)
left_frame4.rowconfigure(0,weight=1)

#layer number label and entry
left_frame5 = tk.Frame(frame1)
left_frame5.grid(row=10,column=1,sticky='news',columnspan=2)
lyr_n_label = tk.Label(left_frame5, text='Number of Layers')
lyr_n_entry = tk.Entry(left_frame5, textvariable=lyr_n)
lyr_n_label.grid(row=0,column=0,sticky='W')
lyr_n_entry.grid(row=0,column=1,sticky='E')
left_frame5.columnconfigure(0, weight=1)
left_frame5.columnconfigure(1, weight=1)
left_frame5.rowconfigure(0,weight=1)

#layer height label and entry
left_frame6 = tk.Frame(frame1)
left_frame6.grid(row=12,column=1,sticky='news',columnspan=2)
lyr_h_label = tk.Label(left_frame6, text='Layer Height (in mm)')
lyr_h_entry = tk.Entry(left_frame6, textvariable=lyr_h)
lyr_h_label.grid(row=0,column=0,sticky='W')
lyr_h_entry.grid(row=0,column=1,sticky='E')
left_frame6.columnconfigure(0, weight=1)
left_frame6.columnconfigure(1, weight=1)
left_frame6.rowconfigure(0,weight=1)

#Defining behaviour of frame 1 contents when changing window size
frame1.rowconfigure(tuple(range(16)), weight=1)
frame1.columnconfigure(tuple(range(8)),weight=1)

##### Right side #####

#Top Label
right_side_label = tk.Label(frame2, text='Print path preview')
right_side_label.grid(row=0,column=0,sticky='W')

#Defining the first right frame that contains rawturtle and the three buttons below it
right_frame1 = tk.Frame(frame2)
right_frame1.grid(row=1,column=0,sticky='news',columnspan=3, padx=50)
turtle_frame = tk.Canvas(right_frame1)
turtle_frame.grid(row=0,column=1,sticky='news')


##########################################################################
##########################################################################

#Drawing the RawTurtle, defining variables for pause and stop and get its size properties
draw = turtle.RawTurtle(turtle_frame)
pause = False
stop = False
turtle_frame.update_idletasks()
x_before = turtle_frame.winfo_width()
y_before = turtle_frame.winfo_height()
#print(x_before, y_before)

#Board function to draw the turtle
def Board(a, path, size, progress = []): 
    #The variables that we can use to continue drawing after pressing pause button twice
    progresslist = progress
    pathing = []
    i = len(progress)
    for j in range (len(path) - i):
        pathing.append(path[i + j])

    #find current turtle angle before drawing
    current_angle = draw.heading()

    #drawing lines and adjusting turtle angle according to the path
    i = 1
    while i < len(pathing):
        #if unpaused - draw the next line and updates progress list
        if pause == False:
            current_coord = pathing[i-1]
            next_coord = pathing[i]
            progresslist.append(pathing[i-1])

            #finding the next line angle
            if next_coord[0] == current_coord[0]:
                if next_coord[1] >= current_coord[1]:
                    expected_angle = 90
                else:
                    expected_angle = -90

            elif next_coord[1] == current_coord[1]:
                if next_coord[0] >= current_coord[0]:
                    expected_angle = 0
                else:
                    expected_angle = 180

            else:
                if next_coord[0] - current_coord[0] >= 0:
                    expected_angle = math.atan((next_coord[1]-current_coord[1]) / 
                                               (next_coord[0]-current_coord[0])) * 180 / math.pi
                else:
                    expected_angle = 180 + math.atan((next_coord[1]-current_coord[1]) / 
                                                     (next_coord[0]-current_coord[0])) * 180 / math.pi

            rotation = expected_angle - current_angle
            while rotation <= 0:
                rotation += 360
            
            #rotate the turtle
            if rotation < 180:
                draw.left(rotation)
            else:
                draw.right(360-rotation)
            
            #adjusting turtle speed according to the inputted value. if '' set speed to 1
            if rawspeed.get() == '':
                draw.speed(1)
            elif int(rawspeed.get())  > 0:
                draw.speed(int(rawspeed.get()))

            #draw the next line and update the current angle
            draw.setpos(next_coord[0], next_coord[1])
            current_angle = expected_angle

        #behaviour if stop button is pressed, executed after a line is finished
        if stop == True:
            progresslist = path[:-1]
            draw.clear()
            draw.penup()
            draw.setpos(zero_now[0],zero_now[1])
            draw.pendown()
            i = len(pathing) - 1
        i+=1
    
    #behaviour if pause button is pressed, executed instead of updating values and drawing the next line
    if pause == True:
        pause_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.NORMAL)
        global pg_list
        pg_list = progresslist

    #behaviour when the turtle finishes drawing
    if len(progresslist) == len (path) - 1:
        #browse, process, play button is normal. pause and stop button disabled
        browse_button.config(state=tk.NORMAL)
        process_button.config(state=tk.NORMAL)
        play_button.config(state=tk.NORMAL)
        #window.resizable(width=True, height=True)
        pause_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        progresslist = []
        pg_list = []
        
        #changes stop variable back to false after the turtle goes back to the centre
        if stop == True:
            Stop()

#behaviour when start button is pressed
def StartBoard():
    #browse, play, process button disabled. pause and stop button enabled
    #window.resizable(width=False, height=False)
    browse_button.config(state=tk.DISABLED)
    play_button.config(state=tk.DISABLED)
    process_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)

    #find the size and centre of the rawturtle screen, done in case the window changes its size
    turtle_frame.update_idletasks()
    x_now = turtle_frame.winfo_width()
    y_now = turtle_frame.winfo_height()
    #print(x_now, y_now)

    x = ((x_now) *19/20) /2
    x_b = ((x_before) *19/20) /2
    y = ((y_now) *19/20) /2
    y_b = ((y_before) *19/20) /2
    global zero_now
    zero_now = [x - x_b, y_b - y]

    #Finding how much should the model be scaled
    if model_size[0] == 0 and model_size[1] == 0:
        scale = 1

    elif model_size[0] == 0 or model_size[1] == 0:
        scale = 1/max(model_size[0] / x_now, model_size[1] / y_now) * 18/20

    else:
        scale = math.sqrt((x_now * y_now) / (3 * model_size[0] * model_size[1]))

    if scale * model_size[0] > x_now or scale * model_size[1] > y_now:
        scale = 1/max(scale * model_size[0] / x_now, scale * model_size[1] / y_now) * 18/20 * scale

    #Aligning the centre of the model to the centre of the RawTurtle
    global coord_path
    coord_path = [[(i[0] - model_centre[0]) * scale + zero_now[0], 
                   (i[1] - model_centre[1]) * scale + zero_now[1]] for i in pre_coord_path]
    
    '''print(model_size)
    print(model_centre)
    print(coord_path)'''

    #Clear RawTurtle screen
    draw.clear()

    #Draw the four corners of the model
    draw.penup()
    draw.speed(0)
    draw.setpos(0,0)
    draw.setpos((model_size[0] / 2) * scale + zero_now[0], (model_size[1] / 2) * scale + zero_now[1])
    draw.write((round(model_centre[0] + model_size[0]/2, 3), round(model_centre[1] + model_size[1]/2, 3)), font=('Arial', 6, 'normal'))
    draw.dot()
    draw.setpos((- model_size[0] / 2) * scale + zero_now[0], (model_size[1] / 2) * scale + zero_now[1])
    draw.write((round(model_centre[0] - model_size[0]/2, 3), round(model_centre[1] + model_size[1]/2, 3)), font=('Arial', 6, 'normal'))
    draw.dot()
    draw.setpos(( - model_size[0] / 2) * scale + zero_now[0], (- model_size[1] / 2) * scale + zero_now[1])
    draw.write((round(model_centre[0] - model_size[0]/2, 3), round(model_centre[1] - model_size[1]/2, 3)), font=('Arial', 6, 'normal'))
    draw.dot()
    draw.setpos((+ model_size[0] / 2) * scale + zero_now[0], (- model_size[1] / 2) * scale + zero_now[1])
    draw.write((round(model_centre[0] + model_size[0]/2, 3), round(model_centre[1] - model_size[1]/2, 3)), font=('Arial', 6, 'normal'))
    draw.dot()

    #initial drawing speed
    draw.speed(1)

    #go to the first coordinate and start drawing
    draw.setpos(coord_path[0][0], coord_path[0][1])
    draw.pendown()
    Board (draw, coord_path, size=0, progress=[])

#Behaviour when pause button is pressed
def PauseBoard():
    #play button is disabled, pause button is global so that the board function stops its loop
    global pause
    play_button.config(state=tk.DISABLED)

    #resumes the board
    if pause == True:
        pause = False # here
        pause_button.config(text='Pause')
        stop_button.config(state=tk.NORMAL)
        Board(draw, coord_path, 0, pg_list)
    
    #pauses the board
    else:
        pause = True # and here
        pause_button.config(text='Resume', state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)

#Behaviour when stop button is pressed. Complete the next line, clear the board and go to the centre
def Stop():
    #set global variables to influence the board and pause function
    global stop
    global pause 

    #behaviour when stop is pressed while turtle is paused
    if pause == True:
        pause = False
        pause_button.config(text='Pause', state=tk.DISABLED)
        draw.clear()
        draw.penup()
        draw.setpos(zero_now[0],zero_now[1])
        draw.pendown()
        browse_button.config(state=tk.NORMAL)
        play_button.config(state=tk.NORMAL)
        process_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        #window.resizable(width=True, height=True)
        global pg_list
        pg_list = []

    #behaviour that will be called to flip the stop state back to false after stopped drawing
    elif stop == True:
        #window.resizable(width=True, height=True)
        pause_button.config(state=tk.DISABLED)
        stop = False

    #stops drawing, standard behaviour
    else:
        #window.resizable(width=True, height=True)
        pause_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        stop = True

##########################################################################
##########################################################################

#Frame inside right_frame1, below the RawTurtle, that contains the three buttons
right_frame2 = tk.Frame(right_frame1)
right_frame2.grid(row=1,column=1,sticky='new')

#play, pause and stop button. Label that reminds the user to browse a file or displays the loaded file.
play_button = tk.Button(right_frame2,text='Play', command = StartBoard)
play_button.grid(row=0,column=0,sticky='W')
play_button.config(state=tk.DISABLED)
pause_button = tk.Button(right_frame2,text='Pause', command = PauseBoard)
pause_button.grid(row=0,column=1,sticky='W')
pause_button.config(state=tk.DISABLED)
stop_button = tk.Button(right_frame2,text='Stop', command=Stop)
stop_button.grid(row=0,column=2,sticky='W')
stop_button.config(state=tk.DISABLED)
filename_label = tk.Label(right_frame2, text='Insert a file by pressing [Browse]', padx=50)   
filename_label.grid(row=0,column=3,sticky='W')

#Frame below the three buttons to determine the RawTurtle speed
speed_frame = tk.Frame(right_frame1)
speed_frame.grid(row=2, column=1, columnspan=2, sticky='w', pady=10)
raw_speed_label = tk.Label(speed_frame, text='Speed (1-99)')
raw_speed_label.grid(row=0, column=0, sticky='w')
raw_speed_entry = tk.Entry(speed_frame, textvariable=rawspeed)
rawspeed.set('1')
raw_speed_entry.grid(row=0, column=1, sticky='w')

#browse, process, and export button
right_frame3 = tk.Frame(frame2)
right_frame3.grid(row=2,column=0,sticky='news', pady=10)
browse_button = tk.Button(right_frame3,text='Browse', command=StartBrowse)
process_button = tk.Button(right_frame3,text='Process', command=StartProcess)
process_button.config(state=tk.DISABLED)
export_button = tk.Button(right_frame3,text='Export', command=StartExport)
export_button.config(state=tk.DISABLED)
browse_button.grid(row=1,column=1,sticky='ew')
process_button.grid(row=1,column=3,sticky='ew')
export_button.grid(row=1,column=5,sticky='ew')
right_frame3.columnconfigure(tuple(range(7)),weight=1)

#A label that reminds the user to fill in the entries
empty_entry_reminder = tk.Label(right_frame3)
empty_entry_reminder.grid(row=0, column=0, columnspan=7, sticky='n')

#Behaviour of frame 2 widgets when the window size changes
frame2.columnconfigure(0,weight=1)
frame2.rowconfigure(0,weight=1)
frame2.rowconfigure(1,weight=5)
frame2.rowconfigure(2,weight=1)
right_frame1.columnconfigure(0, weight=1)
right_frame1.columnconfigure(1, weight=3)
right_frame1.columnconfigure(2, weight=1)
right_frame1.rowconfigure(0, weight=3)
#right_frame1.rowconfigure(1, weight=1)

window.mainloop()


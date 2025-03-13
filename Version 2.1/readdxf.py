def openfile(file):
    '''get line list from dxf and put it as a list of vectors'''
    isBlock = 0 
    lineblock = list()
    '''extract the important part / BLOCK part of the dxf only'''  
    for line in file:
        if (isBlock == 0):
            if (line.strip() == "*MODEL_SPACE"):
                lineblock.append(line.strip())
                isBlock = 1
        elif(isBlock == 1):
            lineblock.append(line.strip())
            if (line.strip() == "DICTIONARY"):
                isBlock = 0

    linedata = list()
    isInLine = False
    b = 0
    '''Find lines, and extract the starting and final (x,y) and combine into vectors'''
    while b < len(lineblock):
        if (lineblock[b] == "LINE"):
            isInLine = True
            temp_linedata = [0,0,0,0] #xs, ys, xf, yf
        elif (isInLine == True and b < len(lineblock) - 2):
            if (lineblock[b+2] == "0"):
                linedata.append(temp_linedata)
                isInLine = False
            else:    
                if (lineblock[b] == "8"):
                    if (lineblock[b+1]=="1"):
                        isInLine = False
                elif (lineblock[b]=="10"):
                    temp_linedata[0]= round(float(lineblock[b+1]), 3)
                elif (lineblock[b]=="20"):
                    temp_linedata[1]= round(float(lineblock[b+1]), 3)
                elif (lineblock[b]=="11"):
                    temp_linedata[2]= round(float(lineblock[b+1]), 3)
                elif (lineblock[b]=="21"):
                    temp_linedata[3]= round(float(lineblock[b+1]), 3)
                b += 1
            #need to end line, put temp data to linedata object
        b += 1

    #print ("Gathered line data :\n", linedata)      ########
    
    return linedata

def pathing(lines, startpoint):
    #print(startpoint)
    '''This is to sort a list of vectors into one continuous path'''
    pathlist = list()
    add = 0
    for a in lines:
        if (a[0]==startpoint[0] and a[1] == startpoint[1]):
            pathlist.append(a)
            startpoint = [a[2], a[3]]
            add = 1
            break
        elif (a[2]==startpoint[0] and a[3] == startpoint[1]):
            temp = [a[0],a[1],a[2],a[3]]
            pathlist.append([a[2],a[3],a[0],a[1]])
            startpoint = [a[0], a[1]]
            add = 2
            break

    if(add == 1):
        lines.remove(pathlist[len(pathlist)-1])
        return pathlist + pathing(lines, startpoint)
    
    elif(add == 2):
        lines.remove(temp)
        return pathlist + pathing(lines, startpoint)
    #print(pathlist)
    return pathlist

def turn_to_gcode(filecreate, destination, pathlist, lyr_n, lyr_h, startpoint, doublewall, wall_separation = 0, Current_Version = '0'):
    import os
    #print(pathlist)
    lyr_n = int(lyr_n)
    lyr_h = int(lyr_h)
    wall_separation = int(wall_separation)

    '''Write into GCode file'''
    temp_write = list()
    filepath = destination + filecreate
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    f = open(filepath, "w")
    for a in printheader(lyr_n, lyr_h, Current_Version):
        f.write(str(a)+"\n")
    
    e=1
    lyr = 1
    while lyr < lyr_n + 1:
        '''1st Wall'''
        temp_write.append(";WALL 1 START LAYER " + str(lyr))
        temp_write.append("G0 X" + str(startpoint[0]) + " Y" + str(startpoint[1]))
        for a in pathlist:
            temp_write.append("G1 X" + str(a[2]) + " Y" + str(a[3]) + " E" + str(e))
            e += 1
        temp_write.append(";WALL 1 END LAYER " + str(lyr))
        temp_write.append("")  

        if (doublewall == True):
            #insert tearing movement
            '''2nd Wall'''
            max_y = 0
            for i in pathlist:
                if (max_y < i[1]):
                    max_y = i[1]
            mirror_plane = max_y + wall_separation / 2

            temp_write.append(";WALL 2 START LAYER " + str(lyr))
            temp_write.append("G0 X" + str(startpoint[0]) + " Y" + str(2 * mirror_plane - startpoint[1]))
            for a in pathlist:
                temp_write.append("G1 X" + str(a[2]) + " Y" + str(2 * mirror_plane - a[3]) + " E" + str(e))
                e += 1
            temp_write.append(";WALL 2END LAYER " + str(lyr))
            temp_write.append("")  
            #insert tearing movement
        
        temp_write.append(";AFTER LAYER MOVE UP")
        temp_write.append("G0 Z" + str((lyr + 1) * lyr_h))
        temp_write.append("")  
        lyr += 1

    for a in temp_write:
        f.write(str(a)+"\n")

    for a in printfooter():
        f.write(str(a)+"\n")

def maxynearestpoint(pathlist, refpoint):
    '''Finding maximum y point to use as y-axis reference for the startpoint'''
    max_y = 0
    for i in pathlist:
        if (max_y < i[1]):
            max_y = i[1]
    refpoint[1] = max_y
    return nearestpoint(pathlist, refpoint)

def nearestpoint(pathlist, refpoint):
    #print(pathlist)
    '''Finding the closest point in the model to start the GCode file with'''
    testcase = pathlist
    for i in testcase:
        b = i[2] - i[0]
        a = i[1] - i[3]
        c = i[0] * i[3] - i[1] * i[2]
        if pow(a,2) + pow(b,2) == 0:
            x0 = i[0]
            y0 = i[1]
        else:
            x0 = (b * (b * refpoint[0] - a * refpoint[1]) - a * c) / (pow(a, 2) + pow(b,2))
            y0 = (a * (a * refpoint[1] - b * refpoint[0]) - b * c) / (pow(a, 2) + pow(b,2))
        pointinsidesgmt = 0
        if (i[0] <= x0 <= i[2] or i[2] <= x0 <= i[0]):
            if (i[1] <= y0 <= i[3] or i[3] <= y0 <= i[1]):
                i.extend([x0, y0, pow(x0 - refpoint[0], 2) + pow(y0 - refpoint[1], 2)])
                pointinsidesgmt = 1
        if (pointinsidesgmt == 0):
            d1 = (pow(i[0] - refpoint[0], 2) + pow(i[1] - refpoint[1], 2))
            d2 = (pow(i[2] - refpoint[0], 2) + pow(i[3] - refpoint[1], 2))
            if (d1 <= d2):
                i.extend([i[0], i[1], d1])
            else:
                i.extend([i[2], i[3], d2])
        pass
    '''Update the pathlist to start with the closest path'''
    a = 0
    i = 0
    while i < len(testcase):
        if (testcase[i][-1] < testcase[a][-1]):
            a = i
        i+=1
    templist = list()
    k = a
    #print(k)
    #print(testcase)
    x0 = testcase[k][-3]
    y0 = testcase[k][-2]
    templist.append([testcase[k][-3], testcase[k][-2], testcase[k][2], testcase[k][3]])
    k+=1
    while k < len(testcase):
        templist.append([testcase[k][0], testcase[k][1], testcase[k][2], testcase[k][3]])
        k+=1
    k = 0
    while k < a:
        templist.append([testcase[k][0], testcase[k][1], testcase[k][2], testcase[k][3]])
        k+=1
    if (refpoint != [x0,y0]):
        templist.append([testcase[k][0], testcase[k][1], testcase[k][-3], testcase[k][-2]])

    #print("Generated path :\n", templist)       #########

    return (templist, [x0, y0])


##--------------------------------------------------------------------------------------------##

def printheader(lyr_n, lyr_h, Current_Version):
    '''Header'''
    header = [
        ";HEADER",
        ";GCODE FOR 3DCP - BY JUSTIN ADRIAN HALIM",
        ";VERSION: " + str(Current_Version),
        ";NUMBER OF LAYERS:" + str(lyr_n),
        ";LAYER HEIGHT:" + str(lyr_h),
        ";END_OF_HEADER",
        "",
        "T0",
        "M82 ;Absolute Extrusion",
        "G92 E0",
        "M109 S025",
        "G280 S1"
        "",
        "G0 F600 X0 Y0 Z0",
        "G0 X0 Y0 Z" + str(lyr_h),
        ""
    ]
    return header

def printfooter():
    '''Footer'''
    footer = [
        ";FOOTER",
        "M140 S0",
        "M107",
        "G91",
        "G1 E-2 F2700",
        "G1 E-2 Z0.2 F2400",
        "G1 X5 Y5 F3000",
        "G1 Z10",
        "G90",
        "M140 S0",
        "M204 S3000",
        "M205 X20 Y20",
        "M107",
        "M82",
        "M104 S0",
        "M104 T1 S0",
        ";END OF GCODE"
    ]
    return footer

##--------------------------------------------------------------------------------------------##



##--------------------------------------------------------------------------------------------##


##--------------------------------------------------------------------------------------------###
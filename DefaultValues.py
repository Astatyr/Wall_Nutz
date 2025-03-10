'''Insert Default values here'''
default_doublewall = 'F'
default_wall_separation = 20
default_startpoint_x = 0
default_startpoint_y = 0
default_lyr_n = 5
default_lyr_h = 10
destination_folder_name = 'GCode_Files'

####################################################################################################

class default_values:
    def __init__(self):
        self.__default_doublewall = default_doublewall
        self.__default_wall_separation = default_wall_separation
        self.__default_startpoint_x = default_startpoint_x
        self.__default_startpoint_y = default_startpoint_y
        self.__default_lyr_n = default_lyr_n
        self.__default_lyr_h = default_lyr_h
        self.__destination_folder_name = destination_folder_name
    
    def get_defdoublewall(self):
        return self.__default_doublewall
    
    def get_defwallsep(self):
        return self.__default_wall_separation
    
    def get_defstartx(self):
        return self.__default_startpoint_x
    
    def get_defstarty(self):
        return self.__default_startpoint_y
    
    def get_deflyr_n(self):
        return self.__default_lyr_n
    
    def get_deflyr_h(self):
        return self.__default_lyr_h
    
    def get_destfoldname(self):
        return self.__destination_folder_name
    
def create_instance_default_values():
    return default_values()


#Description: utility to extract time and PID voltage data from data in the Archive Folder
#Resultant Data is stored in the file Time_PID_Volt folder

def pid_voltage_getter(filename):
    '''Gets the PID voltage from txt files in archive
    Returns a new .txt file name orignal filename + pid voltage with
    time and pid voltage data'''

    file = open(filename, mode = "r")

    new_filename = filename[0:-4] + "_PID_voltage" + ".txt"
    new_file = open(new_filename, mode = 'a')

    for line in file:
        
        #These are sensor logs
        if line[0] == '#':
            new_file.write(line)

        #this is the data, "date time voltage"
        else:
            l = line.split(sep = ", ")
            new_line = l[0] + ', ' + l[-7] + '\n'
            new_file.write(new_line)
    

    file.close()
    new_file.close()

lst_of_files = [
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190722_Sponge_IPA/20190722_Sponge_Ipa_A.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190722_Sponge_IPA/20190722_Sponge_Ipa_B.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190723_Sponge_Benzene/20190723_Sponge_Benzene_CombinedA.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190723_Sponge_Benzene/20190723_Sponge_Benzene_CombinedB.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190723_Sponge_Benzene/20190723_Sponge_Benzene_CombinedC.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190724_Sponge_Benzaldehyde/20190724_Sponge_Benzaldehyde_combined_A.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190724_Sponge_Benzaldehyde/20190724_Sponge_Benzaldehyde_combined_B.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190724_Sponge_Benzaldehyde/20190724_Sponge_Benzaldehyde_combined_C.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190725_Sponge_Limonene/20190725_Sponge_Limonene_Combined_A.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190725_Sponge_Limonene/20190725_Sponge_Limonene_Combined_B.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190725_Sponge_Limonene/20190725_Sponge_Limonene_Combined_C.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190731_Sponge_MEK/20190731_Sponge_MEK_Combined_A.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190731_Sponge_MEK/20190731_Sponge_MEK_Combined_B.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_A.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_B.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_C.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_D.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_E.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_F.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_G.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190820_Sponge_Toluene/20190820_Sponge_Toluene_H.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190821_Sponge_oXylene/20190820_overnight_Sponge_oXylene.monitor.txt.TESTING',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190821_Sponge_oXylene/20190821_Sponge_oXylene.monitor.txt',
    '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190822_Sponge_Benzene/20190822_Sponge_Benzene.monitor.txt',
]

def main():
    for filename in lst_of_files:
        pid_voltage_getter(filename)

if __name__ == '__main__':
    main()
from VOC_LIB import VOC
import matplotlib.pyplot as plt


def combine(l): #l is a list
    '''returns time and concetnration data as a tuple, ([time_data],[concentration_data])'''
    
    time_data = l[0].get_time_data()

    comb_data = l[0].get_new_conc_data()
    
    for chemical in l[1:]:
        chem_conc_data = chemical.get_new_conc_data()
        for index,value in enumerate(chem_conc_data):
            comb_data[index] = value + comb_data[index]

    return (time_data,comb_data)

chemical_1 = VOC('Benzene',500)
chemical_2 = VOC('Toulene',500)

l_of_chemicals = [chemical_1,chemical_2]

time, concentration = combine(l_of_chemicals)

plt.figure(figsize = (12, 4))
plt.subplot(121)
plt.plot(time, concentration)
plt.xlabel('Time')
plt.ylabel('Output')
plt.tight_layout()
plt.show()


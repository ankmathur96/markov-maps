filepath = 'C:/Users/raspberry/Documents/UC Berkeley/Sophomore S2/EE126/project/markov-maps/'
city_zips = open(filepath + 'business_zipcodes', 'r')
zip_count_dic = {}
lines = city_zips.readlines()
for line in lines:
    try:
        line = line.split('\n')[0]
        if int(line) > 90000:
            if line in zip_count_dic:
                zip_count_dic[line] += 1
            else:
                zip_count_dic[line] = 1
    except ValueError:
        pass


filepath = 'C:/Users/raspberry/Documents/UC Berkeley/Sophomore S2/EE126/project/markov-maps/'
zip_locs = open(filepath + 'lat_long_zip', 'r')

zip_pos_dic = {}
lines = zip_locs.readlines()
count = 0
for i in range(len(lines)-1):
    line_arr_curr = lines[i].split()
    line_arr_next = lines[i+1].split()
    if len(line_arr_curr) > 2:
        if int(line_arr_curr[0])+1 == int(line_arr_next[0]):
            zip_pos_dic[line_arr_curr[0]] = (float(line_arr_curr[1]), float(line_arr_curr[2]))
        else:
            if int(line_arr_next[0])-int(line_arr_curr[0]) > 100:
                print(i)
            for j in range(int(line_arr_next[0])-int(line_arr_curr[0])):
                count += 1
                zip_pos_dic[str(int(line_arr_curr[0])+j)] = (float(line_arr_curr[1]), float(line_arr_curr[2]))


zip_combined_dic = {}
count = 0
for zipcode in zip_count_dic:
    if zipcode not in zip_pos_dic:
        count+=1
    else:
        zip_combined_dic[zipcode] = (zip_pos_dic[zipcode][0], zip_pos_dic[zipcode][1], zip_count_dic[zipcode])

import numpy as np
import matplotlib.pyplot as plt

lat_list = [zip_combined_dic[zipcode][0] for zipcode in zip_combined_dic]
long_list = [zip_combined_dic[zipcode][1] for zipcode in zip_combined_dic] 
area_list = [zip_combined_dic[zipcode][2] for zipcode in zip_combined_dic] 
rad_list = [(area/np.pi)**(0.5) for area in area_list]
# plt.scatter(lat_list, long_list, s = rad_list, c = 'g')
# plt.show()
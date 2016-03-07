import geocoder
import os

int_dict = {}
old_int_file = 'intersection_data.csv'
if os.path.isfile(old_int_file):
    with open(old_int_file, 'r') as int_dest_old:
        for line in int_dest_old:
            st1, st2, lat, lng = line.rstrip().split(',')
            int_dict[(st1, st2)] = (lat, lng)
added_count = 0
duplicate_count = 0
skip_end_count = 0
added = open('added.csv', 'w')
with open('unfound.csv', 'w') as unfound:
    with open('sf_intersections.csv', 'r') as int_src:
        int_src.readline() # removes the header
        for line in int_src:
            line_info = line.rstrip().split(',')
            st1, st2 = sorted(line_info[1:3])
            sts = (st1, st2)
            if 'END' in sts:
                skip_end_count += 1
                continue
            if sts in int_dict:
                duplicate_count += 1
                continue
            addr = geocoder.google('Intersection of %s and %s, San francisco, CA, United States' % (st1, st2))
            addr_lat_lng = addr.latlng
            if len(addr_lat_lng) != 2:
                line_str = '%s,%s,%s\n' % (st1, st2, str(addr_lat_lng))
                print 'unfound %s' % (line_str)
                unfound.write(line_str)
                addr_lat_lng = ['', '']
            int_dict[sts] = addr_lat_lng
            lat, lng = addr_lat_lng

            line_str = '%s,%s,%s,%s\n' % (st1, st2, lat, lng)
            added.write(line_str)
            added_count += 1
            if added_count % 100 == 0:
                print 'Found 100 more'
added.close()
print 'total added: %s' % (added_count)
print 'total skipped: %s' % (duplicate_count)
print 'total end: %s' % (skip_end_count)
with open('intersection_data_new.csv', 'w') as int_dest:
    for (st1, st2), (lat, lng) in int_dict.iteritems():
        line_str = '%s,%s,%s,%s\n' % (st1, st2, lat, lng)
        int_dest.write(line_str)

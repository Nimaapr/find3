import matplotlib.pyplot as plt
# I have to add access points in another way
import sys


# Get the three inputs from command-line arguments
device_num = sys.argv[1]
location_all = sys.argv[2]
# family= "site4"
family= sys.argv[3]


# location = location -1 : numbers start from 1.
def show_floorplan(device_num, location_all, family):
    floor_level = location_all[:2]
    location = location_all[2:4]
    # floor_str = "/app/main/static/img2/org_floorplan" + str(floor_level) + ".png"
    try:
        floor_str = "/data/data/org_floorplan" + family + str(floor_level) + ".png"
    except Exception as e:
        # If an error occurs, write it to a file
        with open("/app/main/static/img2/error_log.txt", "a") as error_file:
            error_file.write(str(e) + "\n")

    img_array = plt.imread(floor_str)
    fig, ax = plt.subplots()
    ax.imshow(img_array)
#     real access points
#     access_points= [(0,0),(0,0.9), (0, 1.8), (0,2.7), 
#                     (0.9, 2.7), (0.9, 1.8), (0.9, 0.9), (0.9, 0)]
#   (0.0) = (450, 180)
    access_points = [(450,180),(450,270), (450, 360), (450,450), 
                    (630, 450), (630, 360), (630, 270), (630, 180)]
    position = access_points[int(location)-1]
    ax.add_patch(plt.Circle(position, radius=10, color='r'))
    ax.annotate(f"Device {device_num}", position, color='r')
    # fig.savefig('/app/main/static/img2/floorplan{}.png'.format(floor_level))
    fig.savefig('/app/main/static/img2/floorplan.png')
    # plt.show()
    with open('/app/main/static/img2/empty_file_inside.txt', 'w') as file:
        file.write('/app/main/static/img2/floorplan{}.png'.format(floor_level) + "\n")
        file.write(f"Device {device_num}" + "\n")
        file.write(str(position) + "\n")

# floor_level = 1
# device_num = 12
# location = 7

show_floorplan(device_num, location_all, family)


with open('/app/main/static/img2/empty_file_outside.txt', 'w') as f:
    # f.write(floor_level + "\n")
    # f.write(type(floor_level) + "\n")
    f.write(device_num + "\n")
    f.write(location_all + "\n")

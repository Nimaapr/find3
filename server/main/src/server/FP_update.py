import matplotlib.pyplot as plt
from PIL import Image
# I have to add access points in another way



def show_floorplan(floor_level, device_num, location):
    with open('/app/main/static/img2/empty_file_inside.txt', 'w'):
        file.write(floor_level + "\n")
        file.write(device_num + "\n")
        file.write(location + "\n")
#     floor_str = "/app/main/static/img2/org_floorplan" + str(floor_level) + ".png"
#     img = Image.open(floor_str)
#     img_array = plt.imread(floor_str)
#     fig, ax = plt.subplots()
#     ax.imshow(img_array)
# #     real access points
# #     access_points= [(0,0),(0,0.9), (0, 1.8), (0,2.7), 
# #                     (0.9, 2.7), (0.9, 1.8), (0.9, 0.9), (0.9, 0)]
# #   (0.0) = (450, 180)
#     access_points = [(450,180),(450,270), (450, 360), (450,450), 
#                     (630, 450), (630, 360), (630, 270), (630, 180)]
#     position = access_points[int(location)]
#     ax.add_patch(plt.Circle(position, radius=10, color='r'))
#     ax.annotate(f"Device {device_num}", position, color='r')
#     fig.savefig('/app/main/static/img2/floorplan{}.png'.format(floor_level))
    # plt.show()

# floor_level = 1
# device_num = 12
# location = 7
# show_floorplan(floor_level, device_num, location)

with open('/app/main/static/img2/empty_file_outside.txt', 'w'):
    pass
    # file.write(floor_level + "\n")
    # file.write(device_num + "\n")
    # file.write(location + "\n")
# this part for test

# floor_str = "/static/img2/org_floorplan1.png"
# img = Image.open(floor_str)
# img_array = plt.imread(floor_str)
# fig, ax = plt.subplots()
# ax.imshow(img_array)
# #     real access points
# #     access_points= [(0,0),(0,0.9), (0, 1.8), (0,2.7), 
# #                     (0.9, 2.7), (0.9, 1.8), (0.9, 0.9), (0.9, 0)]
# #   (0.0) = (450, 180)
# access_points = [(450,180),(450,270), (450, 360), (450,450), 
#                 (630, 450), (630, 360), (630, 270), (630, 180)]
# position = access_points[4]
# ax.add_patch(plt.Circle(position, radius=10, color='r'))
# ax.annotate(f"Device device122", position, color='r')
# fig.savefig('/static/img2/floorplan1.png')
a_file = open("fi_image_list_2294645.txt")

lines_to_read = [3]

for position, line in enumerate(a_file):
  #Iterate over each line and its index
  if position in lines_to_read:
      print(line)
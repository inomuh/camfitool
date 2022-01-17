from class_list_creator import ListCreator as lst
def main():

    a = [1, 2, 3, 4]
    b = [4]
    c = [x for x in a if x not in b] # list subtractor
    print(c)

main()
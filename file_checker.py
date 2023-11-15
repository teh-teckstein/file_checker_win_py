import os
if __name__ == "__main__":
    path = "."
    for root, d_names, f_names in os.walk(path):
        print(root, d_names, f_names)
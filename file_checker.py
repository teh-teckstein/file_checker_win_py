import os
if __name__ == "__main__":
    path = os.path.abspath(os.sep)
    #path = "."
    size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            size += os.stat(fp).st_size
 
# display size        
print("Folder size: " + str(size))
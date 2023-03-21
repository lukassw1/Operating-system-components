
# File System

The project creates a virtual disk in a binary file and provides a console application that takes orders. Possible operations are listed below.

### Used libraries

pickle, datetime, argparse 

## Manual
ls: list current directory contents

ls -la: list current directory content data

cd: go to the root directory

cd [relative path directory]: go to the indicated directory

mkdir [new directory name]: create a new directory in the current directory

mkdir [new directory name/next directory name]: create nested directories

cp [disk file path] [new file name in virtual disk]: copy file from disk to the current directory

get [file name in virtual disk] [new file name in disk]: copy file from current directory in virtual disk to disk

rm [file/directory name in virtual disk]: remove the file or directory from the current directory

shutdown: close the application with a virtual disk

diskusage: show usage of disk

man: shows manual with available commands on a virtual disk
import pickle
import argparse
from constants import INODE_SIZE, INODE_TABLE_SIZE, SUPERBLOCK_SIZE
from SuperBlock import SuperBlock
from INode import INode
from functions import mkdir, ls, cp, cd, get, man, rm, ls_la, diskusage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="enter the path to the virtual disk")
    args = parser.parse_args()
    PATH = args.path
    INODE_TABLE = []
    current_super = 0
    try:
        with open(PATH, 'rb+') as file:
            print(f"An existing file has been loaded with path/name: {PATH}")
            superblock_bytes = file.read(SUPERBLOCK_SIZE)
            current_super: SuperBlock = pickle.loads(superblock_bytes)
            print(f"Last modification date: {current_super.get_time()}")
            INODE_TABLE = []
            for i in range(INODE_TABLE_SIZE // INODE_SIZE):
                file.seek(SUPERBLOCK_SIZE + (i * INODE_SIZE))
                inode_bytes = file.read(INODE_SIZE)
                if inode_bytes != bytes(INODE_SIZE) and inode_bytes:
                    current_inode: INode = pickle.loads(inode_bytes)
                    INODE_TABLE.append(current_inode)
    except FileNotFoundError:
        odp = input("file with the given name does not exist, create a new one? (y,n)")
        if odp != "y":
            return
        with open(PATH, 'wb+') as file:
            new_super = SuperBlock("proba")
            current_super = new_super
            pickle.dump(new_super, file=file)
            file.seek(SUPERBLOCK_SIZE)
            main_dir = INode("~", True, SUPERBLOCK_SIZE)
            INODE_TABLE.append(main_dir)
            pickle.dump(main_dir, file=file)
            print(f"Created new file with path/name: {PATH}")
    current_inode = INODE_TABLE[0]
    inner_path = "~"
    while True:
        command = input(f"\033[34m{inner_path}\033[0m$ ")
        command = command.split(" ")
        if command[0] == "ls":
            if len(command) == 1:
                ls(current_inode, PATH)
            elif command[1] == "-la":
                ls_la(current_inode, PATH)
        elif command[0] == "cd":
            current_inode, inner_path = cd(command, current_inode, INODE_TABLE, PATH, inner_path)
        elif command[0] == "mkdir":
            INODE_TABLE, current_inode, current_super = mkdir(command[1], current_inode, PATH, INODE_TABLE, current_super)
        elif command[0] == "cp":
            if len(command) != 3:
                print("cp command is called with 2 arguments, see man for more information")
            else:
                current_super, current_inode, INODE_TABLE = cp(command, current_inode, PATH, INODE_TABLE, current_super)
        elif command[0] == "get":
            if len(command) != 3:
                print("get command is called with 2 arguments, see man for more information")
            else:
                get(command, current_inode, PATH)
        elif command[0] == "rm":
            current_inode, current_super = rm(command[1], current_inode, PATH, INODE_TABLE, current_super)
        elif command[0] == "man":
            man()
        elif command[0] == "shutdown":
            break
        elif command[0] == "diskusage":
            diskusage(PATH, current_super, INODE_TABLE[0])
        else:
            print("Unknown command")


if __name__ == "__main__":
    main()

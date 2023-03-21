FILE_SIZE = 1048576 * 2             # 2 mega
SUPERBLOCK_SIZE = 1024 * 4          # 4 kilo
INODE_TABLE_SIZE = 1024 * 50        # 50 kilo
INODE_SIZE = 1024 * 2               # 2 kilo
DATA_BLOCK_SIZE = 1024 * 4          # 4 kilo
MANUAL = "\nls : list current directory contents\n" + \
        "ls -la : list current directory content data\n" + \
        "cd : go to root directory\n" + \
        "cd [relative path directory] : go to indicated directory\n" + \
        "mkdir [new directory name] : create new directory in current directory\n" + \
        "mkdir [new directory name/next directory name] : craete nested directories\n" + \
        "cp [disk file path] [new file name in virtual disk] : copy file from disk to current directory\n" + \
        "get [file name in virtual disk] [new file name in disk] : copy file from current directory in virtual disk to disk\n" + \
        "rm [file/directory name in virtual disk] : remove file or directory from current directory\n" + \
        "shutdown : close application with virtual disk\n" + \
        "diskusage : show us\n" + \
        "man : shows manual with available commands on virtual disk\n"

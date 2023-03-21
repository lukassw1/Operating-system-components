from datetime import datetime
from constants import FILE_SIZE, INODE_SIZE, INODE_TABLE_SIZE, SUPERBLOCK_SIZE, DATA_BLOCK_SIZE
import pickle


class SuperBlock:
    def __init__(self, filename) -> None:
        self.size = 0
        self.disk_name = filename
        self.time = datetime.now()
        self.free_blocks = (FILE_SIZE - INODE_TABLE_SIZE - SUPERBLOCK_SIZE) // DATA_BLOCK_SIZE
        self.allocated_blocks = 0
        self.max_blocks_amount = (FILE_SIZE - INODE_TABLE_SIZE - SUPERBLOCK_SIZE) // DATA_BLOCK_SIZE
        self.max_inode_amount = INODE_TABLE_SIZE // INODE_SIZE
        self.allocated_inodes = 1
        pass

    def get_disk_name(self):
        return self.disk_name

    def get_time(self):
        return self.time

    def added_new_inode(self):
        self.allocated_inodes += 1

    def upadate_time(self):
        self.time = datetime.now()

    def save_to_file(self, file_handle) -> None:
        self.upadate_time()
        file_handle.seek(0)
        pickle.dump(self, file=file_handle)

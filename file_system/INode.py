import pickle
from datetime import datetime


class INode:
    def __init__(self, name: str, dir: bool, address: int) -> None:
        self.time = datetime.now()
        self.name: str = name
        self.dir: bool = dir
        self.inodes_addresses: dict = {}
        self.datablocks_addresses: list = []
        self.address: int = address

    def is_dir(self) -> bool:
        return self.dir

    def upadate_time(self):
        self.time = datetime.now()

    def add_inode_address(self, new_name: str, inode_address: int):
        self.inodes_addresses[new_name] = inode_address

    def add_datablock_address(self, block_address: int):
        self.datablocks_addresses.append(block_address)

    def find_inode_address(self, file_name: str) -> int:
        return self.inodes_addresses[file_name]

    def get_inodes_adresses(self) -> dict:
        return self.inodes_addresses

    def get_datablocks_addresses(self) -> list:
        return self.datablocks_addresses

    def get_name(self) -> str:
        return self.name

    def get_time(self):
        return self.time

    def get_address(self) -> int:
        return self.address

    def save_to_file(self, file_handle) -> None:
        self.upadate_time()
        file_handle.seek(self.address)
        pickle.dump(self, file=file_handle)

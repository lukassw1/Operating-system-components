import pickle
from constants import INODE_SIZE, INODE_TABLE_SIZE, SUPERBLOCK_SIZE, DATA_BLOCK_SIZE, MANUAL, FILE_SIZE
from INode import INode
from SuperBlock import SuperBlock


def mkdir(argument: str, current_dir: INode, path: str, cur_table, super: SuperBlock):
    command = argument.split("/")
    orginal_address = current_dir.get_address()
    with open(path, 'rb+') as virtual_disk:
        for new_dir_name in command:
            for i in range(INODE_TABLE_SIZE // INODE_SIZE):
                virtual_disk.seek(SUPERBLOCK_SIZE + (i * INODE_SIZE))
                inode_bytes = virtual_disk.read(INODE_SIZE)
                if inode_bytes == bytes(INODE_SIZE) or not inode_bytes:
                    current_dir.add_inode_address(new_dir_name, SUPERBLOCK_SIZE + (i * INODE_SIZE))
                    current_dir.save_to_file(virtual_disk)
                    new_inode = INode(new_dir_name, True, SUPERBLOCK_SIZE + (i * INODE_SIZE))
                    new_inode.save_to_file(virtual_disk)
                    super.added_new_inode()
                    super.save_to_file(virtual_disk)
                    cur_table.append(new_inode)
                    current_dir = new_inode
                    break
        virtual_disk.seek(orginal_address)
        inode_bytes = virtual_disk.read(INODE_SIZE)
        current_dir = pickle.loads(inode_bytes)
    return cur_table, current_dir, super


def ls(current_dir: INode, path: str):
    with open(path, 'rb+') as virtual_disk:
        for address in list(current_dir.get_inodes_adresses().values()):
            virtual_disk.seek(address)
            current_inode_bytes = virtual_disk.read(INODE_SIZE)
            current_inode: INode = pickle.loads(current_inode_bytes)
            if current_inode.is_dir():
                print(f"\033[34m {current_inode.get_name()} \033[0m", end=" ")
            else:
                print(f" {current_inode.get_name()} ", end=" ")
    if len(list(current_dir.get_inodes_adresses().values())) != 0:
        print("")


def ls_la(current_dir: INode, path: str):
    print("Name | Last modified | Allocated data blocks | Allocated INodes | Sum of allocated memory (in bytes)")
    with open(path, 'rb+') as virtual_disk:
        for address in list(current_dir.get_inodes_adresses().values()):
            virtual_disk.seek(address)
            current_inode_bytes = virtual_disk.read(INODE_SIZE)
            current_inode: INode = pickle.loads(current_inode_bytes)
            if current_inode.is_dir():
                print(f"\033[34m {current_inode.get_name()} \033[0m", end=" | ")
                print(f"{current_inode.get_time()}", end=" | ")
                adb, ain = calculate_content(current_inode, path, 0, 1, virtual_disk)
                print(f"{adb}", end=" | ")
                print(f"{ain}", end=" | ")
                print(f"{(adb * DATA_BLOCK_SIZE) + (ain * INODE_SIZE)}",  end=" | ")
                print("")
            else:
                print(f" {current_inode.get_name()} ", end=" | ")
                print(f"{current_inode.get_time()}", end=" | ")
                ain = 1
                adb = len(current_inode.get_datablocks_addresses())
                print(f"{adb}", end=" | ")
                print(f"{ain}", end=" | ")
                print(f"{(adb * DATA_BLOCK_SIZE) + (ain * INODE_SIZE)}",  end=" | ")
                print("")


def calculate_content(current_dir: INode, path: str, db_sum: int, in_sum: int, file_handle):
    for address in list(current_dir.get_inodes_adresses().values()):
        in_sum += 1
        file_handle.seek(address)
        current_inode_bytes = file_handle.read(INODE_SIZE)
        current_inode: INode = pickle.loads(current_inode_bytes)
        if current_inode.is_dir():
            db_sum, in_sum = calculate_content(current_inode, path, db_sum, in_sum, file_handle)
        else:
            db_sum += len(current_inode.get_datablocks_addresses())
    return db_sum, in_sum


def cd(argument: list, current_inode: INode, cur_table: list, path: str, inner_p: str):
    if len(argument) == 1:
        return cur_table[0], "~"
    else:
        name = argument[1]
        names = name.split("/")
        with open(path, 'rb+') as virtual_disk:
            for name in names:
                try:
                    address = current_inode.find_inode_address(name)
                except KeyError:
                    print("Unkown directory")
                    return current_inode, inner_p
                virtual_disk.seek(address)
                inode_bytes = virtual_disk.read(INODE_SIZE)
                new_inode: INode = pickle.loads(inode_bytes)
                if not new_inode.is_dir():
                    print("Cannot cd into file")
                    return current_inode, inner_p
                current_inode = new_inode
                inner_p = inner_p + "/" + name
        return current_inode, inner_p


def cp(arguments: list, current_dir: INode, path: str, cur_table: list, super: SuperBlock):
    path_to_file = arguments[1]
    file_name = arguments[2]
    file_bytes = []
    with open(path_to_file, 'rb+') as file:
        while True:
            if len(file_bytes) > super.free_blocks:
                raise ValueError("Not enough space on virtual disk")
            file.seek(len(file_bytes) * DATA_BLOCK_SIZE)
            block = file.read(DATA_BLOCK_SIZE)
            if block:
                file_bytes.append(block)
            else:
                break
    with open(path, 'rb+') as virtual_disk:
        for i in range(INODE_TABLE_SIZE // INODE_SIZE):
            virtual_disk.seek(SUPERBLOCK_SIZE + (i * INODE_SIZE))
            inode_bytes = virtual_disk.read(INODE_SIZE)
            if inode_bytes == bytes(INODE_SIZE) or not inode_bytes:
                current_dir.add_inode_address(file_name, SUPERBLOCK_SIZE + (i * INODE_SIZE))
                file_inode = INode(file_name, False, SUPERBLOCK_SIZE + (i * INODE_SIZE))
                index_bytes = 0
                for j in range(super.max_blocks_amount):
                    virtual_disk.seek(SUPERBLOCK_SIZE + INODE_TABLE_SIZE + (j * DATA_BLOCK_SIZE))
                    block_bytes = virtual_disk.read(DATA_BLOCK_SIZE)
                    if block_bytes == bytes(DATA_BLOCK_SIZE) or not block_bytes:
                        file_inode.add_datablock_address(SUPERBLOCK_SIZE + INODE_TABLE_SIZE + (j * DATA_BLOCK_SIZE))
                        virtual_disk.seek(SUPERBLOCK_SIZE + INODE_TABLE_SIZE + (j * DATA_BLOCK_SIZE))
                        virtual_disk.write(file_bytes[index_bytes])
                        index_bytes += 1
                        super.allocated_blocks += 1
                        super.free_blocks -= 1
                        super.upadate_time()
                        if index_bytes == len(file_bytes):
                            break
                current_dir.save_to_file(virtual_disk)
                file_inode.save_to_file(virtual_disk)
                super.added_new_inode()
                super.save_to_file(virtual_disk)
                cur_table.append(file_inode)
                break
    return super, current_dir, cur_table


def get(arguments: list, current_dir: INode, path: str) -> None:
    file_bytes = bytes()
    file_name = arguments[1]
    new_name = arguments[2]
    try:
        file_node_address = current_dir.find_inode_address(file_name)
    except KeyError:
        print(f"There is not '{file_name}' file in this directory")
        return
    with open(path, 'rb+') as virtual_disk:
        virtual_disk.seek(file_node_address)
        inode_bytes = virtual_disk.read(INODE_SIZE)
        file_inode: INode = pickle.loads(inode_bytes)
        for block_address in file_inode.get_datablocks_addresses():
            virtual_disk.seek(block_address)
            block_bytes = virtual_disk.read(DATA_BLOCK_SIZE)
            block_bytes.replace(b'\x00', b'')
            file_bytes = file_bytes + block_bytes
    with open(new_name, 'wb') as file_on_disk:
        # pickle.dump(file_bytes, file=file_on_disk)
        file_on_disk.write(file_bytes)


def man():
    print(MANUAL)


def rm(argument: str, current_node: INode, path: str, cur_table: list, super: SuperBlock):
    with open(path, 'rb+') as virtual_disk:
        try:
            address = current_node.find_inode_address(argument)
        except KeyError:
            print(f"There is no directory/file named '{argument}'")
            return
        virtual_disk.seek(address)
        inode_bytes = virtual_disk.read(INODE_SIZE)
        inode_to_delete: INode = pickle.loads(inode_bytes)
        if inode_to_delete.is_dir():
            super = remove_catalog(inode_to_delete, virtual_disk, super)
        else:
            super = remove_file(inode_to_delete, virtual_disk, super)
        del current_node.inodes_addresses[argument]
        current_node.save_to_file(virtual_disk)
    return current_node, super


def remove_catalog(current_dir: INode, file_handle, super: SuperBlock):
    addresses_to_delete = list(current_dir.get_inodes_adresses().values())
    for address in addresses_to_delete:
        file_handle.seek(address)
        current_inode_bytes = file_handle.read(INODE_SIZE)
        current_inode: INode = pickle.loads(current_inode_bytes)
        if current_inode.is_dir():
            super = remove_catalog(current_inode, file_handle, super)
        else:
            super = remove_file(current_inode, file_handle, super)
    address = current_dir.get_address()
    file_handle.seek(address)
    empty_space = bytes(INODE_SIZE)
    file_handle.write(empty_space)
    super.allocated_inodes -= 1
    super.save_to_file(file_handle)
    return super


def remove_file(inode: INode, file_handle, super: SuperBlock):
    for data_block_address in inode.get_datablocks_addresses():
        file_handle.seek(data_block_address)
        empty_space = bytes(DATA_BLOCK_SIZE)
        file_handle.write(empty_space)
        super.allocated_blocks -= 1
    address = inode.get_address()
    file_handle.seek(address)
    empty_space = bytes(INODE_SIZE)
    file_handle.write(empty_space)
    super.allocated_inodes -= 1
    super.save_to_file(file_handle)
    return super


def diskusage(path: str, super: SuperBlock, root_inode: INode):
    print("Virtual disk information: ")
    print(f"Last modified: {super.get_time()}")
    print(f"Usage of INodes: {super.allocated_inodes}/{super.max_inode_amount}")
    print(f"Usage of DataBlocks: {super.allocated_blocks}/{super.max_blocks_amount}")
    print(f"Usage of memory (in bytes): {SUPERBLOCK_SIZE + (super.allocated_inodes * INODE_SIZE) + (super.allocated_blocks * DATA_BLOCK_SIZE)}/{FILE_SIZE}")
    percent = (SUPERBLOCK_SIZE + (super.allocated_inodes * INODE_SIZE) + (super.allocated_blocks * DATA_BLOCK_SIZE)) / FILE_SIZE
    percent = round(percent * 100, 3)
    print(f"Usage of memory: {percent}%")

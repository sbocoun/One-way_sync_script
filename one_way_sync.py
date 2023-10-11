import time
import os
import hashlib
import shutil
import argparse


def is_valid_dir(new_path):
    """Return a normalized version of new_path iff it is a valid directory
    path and raise a NotADirectoryError otherwise."""

    if os.path.isdir(new_path):
        return os.path.abspath(new_path)
    else:
        raise NotADirectoryError(new_path)


def parse_arguments() -> argparse.Namespace:
    """Parse the source_dir, replica_dir, and synchronization
    frequency into a new Namespace object."""

    parser = (argparse.ArgumentParser
              (description="One-way synchronization script between two chosen "
                           "directories. After execution, and then periodically"
                           " after a certain duration (the chosen frequency), "
                           "the contents of the replica directory are modified "
                           "to match the source directory."))
    parser.add_argument('source_dir', type=is_valid_dir,
                        help='The system path of the desired source directory. '
                             'An error will be raised if the path contains a '
                             'space but is not enclosed in quotes.')
    parser.add_argument('replica_dir', type=is_valid_dir,
                        help='The system path of the desired replica '
                             'directory. An error will be raised if the path '
                             'contains a space but is not enclosed in quotes.')
    parser.add_argument("-f", "--frequency", type=int, default=60,
                        help='The duration (in seconds) between '
                             'synchronizations. Defaults to 60 seconds.')
    parser.add_argument("-l", "--log_dir", type=str,
                        default=f'{os.path.realpath(os.getcwd())}',
                        help='If a log file already exists, you may enter its '
                             'directory path. If it doesn\'t, or you would like'
                             ' to create a log in a different directory, '
                             'please enter the desired directory path. If the '
                             'path contains a space, please surround it with '
                             'quotes. If log_dir is left blank, or the '
                             'inputted path is invalid, the log file will be '
                             'created in the current working directory.')
    return parser.parse_args()


def add_to_log(log_msg: str) -> None:
    """Append the current time and log_msg to the log file."""

    log = open("sync_log.txt", "a")
    curr_time = time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(time.time()))
    log.write(f"[{curr_time}] {log_msg} \n")


def check_for_log(log_dir: str) -> str:
    """If log_dir is a valid directory, change the current working directory
    to log_dir and locate or create a log file. If it is invalid, search for or
    create a log file in the current working directory. Return the log path."""

    if os.path.isdir(log_dir):
        os.chdir(os.path.abspath(log_dir))
        log_file = os.path.join(log_dir, "sync_log.txt")
        if os.path.isfile(log_file):
            return log_file
        else:
            add_to_log("Log created.")
            return log_file

    else:
        log_file = os.path.join(os.path.abspath(os.getcwd()), "sync_log.txt")
        if os.path.isfile("sync_log.txt"):
            return log_file
        else:
            add_to_log("Log created.")
            return log_file


def is_subdir(a_dir: str, b_dir: str) -> bool:
    """Compare two valid directory paths and return True iff b_dir is a
    subdirectory of a_dir.

    Preconditions: a_dir and b_dir are both valid directory paths."""

    # Normalizes the directory paths, e.g. in case they're relative.
    norm_a_dir = os.path.abspath(a_dir)
    norm_b_dir = os.path.abspath(b_dir)
    # If b_dir is a subdirectory of a_dir, the path of a_dir will be contained
    # in the path of b_dir.
    if norm_a_dir == os.path.commonpath([norm_a_dir, norm_b_dir]):
        return True
    else:
        return False


def is_valid_replica(s_dir: str, r_dir: str) -> bool:
    """Return True iff r_dir is a valid directory path, neither s_dir nor
    r_dir are subdirectories of each other, and r_dir and s_dir are not the
    same directory.

    Precondition: s_dir is a valid directory path."""

    if not os.path.isdir(r_dir):
        print(f'\"{r_dir}" is not a valid directory, please make another input.'
              f' If you\'d like to terminate this script, please enter "-1" as '
              f'the directory path.')
        return False
    if r_dir == s_dir:
        print(f'\"{r_dir}" has already been chosen as the source '
              f'directory, please choose another replica directory. If you\'d '
              f'like to terminate this script, please enter "-1" as the '
              f'directory path.')
        return False
    elif is_subdir(s_dir, r_dir):
        print(f'You cannot choose \"{r_dir}" as the replica directory '
              f'because it is a subdirectory of the chosen source '
              f'directory. Please choose another replica directory. '
              f'If you\'d like to terminate this script, please enter "-1" '
              f'as the directory path.')
        return False
    elif is_subdir(r_dir, s_dir):
        print(f'You cannot choose \"{r_dir}" as the replica directory '
              f'because it contains the chosen source directory. Please '
              f'choose another replica directory. If you\'d like to '
              f'terminate this script, please enter "-1" as the '
              f'directory path.')
        return False
    else:
        return True


def compare_files(file_a: str, file_b: str) -> bool:
    """Compare file_a and file_b by generating corresponding hashes using the
    MD5 standard, and return True iff the hashes are identical.

    Precondition: file_a and file_b are valid file paths."""

    # While no longer secure as an encryption standard, MD5 is still quick and
    # the only consequence of a collision is the unnecessary replacement of a
    # single file.
    with open(file_a, "rb") as f_a:
        digest_a = hashlib.md5(f_a.read()).hexdigest()
    with open(file_b, "rb") as f_b:
        digest_b = hashlib.md5(f_b.read()).hexdigest()
    if digest_a == digest_b:
        return True
    else:
        return False


def sync_files(file_a: str, file_b: str, file_b_dir: str) -> None:
    """Compare file_a and file_b, and if they are not identical, replace file_b
    with file_a in file_b_dir. Record in the log if file_b is updated.

    Precondition: file_a and file_b are valid file paths and file_b_dir is a
    valid directory path containing file_b."""

    if compare_files(file_a, file_b):
        return None
    else:
        try:
            os.remove(file_b)
            # While shutil may not preserve all file metadata, as opposed to
            # native OS shell commands via os.system, it is guaranteed to work
            # with all OS shells.
            shutil.copy2(file_a, file_b_dir)
            add_to_log(f'"{file_b}" updated.')
            print(f'"{file_b}" updated.')
        except OSError:
            add_to_log(f'"{file_b}" failed to update.')
            print(f'"{file_b}" failed to update.')


def copy_file(file_path: str, target_dir: str) -> None:
    """Copy the file located at file_path to target_dir and log it.

    Precondition: file_path is a valid file path and target_dir is a valid
    directory path."""

    try:
        shutil.copy2(file_path, target_dir)
        add_to_log(f'File "{file_path}" copied to the directory '
                   f'"{target_dir}".')
        print(f'File "{file_path}" copied to the directory '
              f'"{target_dir}".')
    except OSError:
        # In case of various system I/O failures such as 'file not
        # found' or 'disk full'
        add_to_log(f'File "{file_path}" failed to copy to the '
                   f'directory "{target_dir}".')
        print(f'File "{file_path}" failed to copy to the '
              f'directory "{target_dir}".')


def copy_dir(dir_a, dir_b) -> None:
    """Create a subdirectory in dir_b with the same name as dir_a and copy
     the contents of dir_a into it while logging every file that's copied.

    Precondition: dir_a and dir_b are valid directory paths"""

    dir_a_name = os.path.basename(dir_a)
    # new_dir is the path of the new subdirectory made in dir_b
    new_dir = os.path.join(dir_b, dir_a_name)
    os.mkdir(new_dir)
    dir_a_contents = os.listdir(dir_a)  # A list containing the names of the
    # folders and files in dir_a
    for dir_a_entry in dir_a_contents:
        path_in_dir_a = os.path.join(dir_a, dir_a_entry)
        path_in_new_dir = os.path.join(new_dir, dir_a_entry)
        if os.path.isfile(path_in_dir_a):
            try:
                shutil.copy2(path_in_dir_a, path_in_new_dir)
                add_to_log(f'File "{path_in_dir_a}" copied to the directory '
                           f'"{path_in_new_dir}".')
                print(f'File "{path_in_dir_a}" copied to the directory '
                      f'"{path_in_new_dir}".')
            except OSError:
                add_to_log(f'File "{path_in_dir_a}" could not be copied to the '
                           f'directory "{path_in_new_dir}".')
                print(f'File "{path_in_dir_a}" could not be copied to the '
                      f'directory "{path_in_new_dir}".')
                continue
        else:
            # If path_in_dir_a isn't a file, it's a directory, so copy_dir can
            # be recursively applied to recreate it in the new directory.
            copy_dir(path_in_dir_a, new_dir)


def remove_from_dir(removable_paths: list[str], bloated_dir: str) -> None:
    """Remove the files and directories listed in removable_paths from
    bloated_dir while logging every file that is removed.

    Precondition: bloated_dir is a valid directory path and removable_paths
    only contains names of files or directories located in bloated_dir."""

    for removable_entry in removable_paths:
        removable_entry_path = os.path.join(bloated_dir, removable_entry)
        if os.path.isfile(removable_entry_path):
            try:
                os.remove(removable_entry_path)
                add_to_log(f'Removed the file "{removable_entry_path}" from '
                           f'"{bloated_dir}."')
                print(f'Removed the file "{removable_entry_path}" from '
                      f'"{bloated_dir}."')
            except OSError:
                add_to_log(f'File "{removable_entry_path}" could not be removed'
                           f' from the directory "{bloated_dir}".')
                print(f'File "{removable_entry_path}" could not be removed '
                      f'from the directory "{bloated_dir}".')
                continue
        elif len(os.listdir(removable_entry_path)) == 0:
            # In this case, removable_entry_path is an empty directory, so it
            # can be removed.
            os.rmdir(removable_entry_path)
        elif os.path.isdir(removable_entry_path):
            # In this case, removable_entry_path may still contain files, so the
            # function remove_from_dir should be applied recursively to remove
            # and log them.
            remove_from_dir(os.listdir(removable_entry_path),
                            removable_entry_path)
            # Now remove_from_dir is an empty directory, so it can also be
            # removed
            os.rmdir(removable_entry_path)


def sync_directories(s_dir: str, r_dir: str) -> None:
    """Compare the contents of the directories s_dir and r_dir and adjust the
    contents of r_dir to match the contents of s_dir.

    Precondition: s_dir, r_dir are valid directory paths and neither is a
    subdirectory of the other."""

    source_contents = os.listdir(s_dir)
    # source_contents contains the names of the directories and files in s_dir.
    replica_contents = os.listdir(r_dir)
    # replica_contents contains the names of the directories and files in r_dir.
    for source_entry in source_contents:
        s_entry_path = os.path.join(s_dir, source_entry)
        r_entry_path = os.path.join(r_dir, source_entry)
        if source_entry in replica_contents and os.path.isfile(s_entry_path):
            # source_entry is a file that exists in both s_dir and r_dir, so
            # both versions have to be compared and the latter possibly updated.
            sync_files(s_entry_path, r_entry_path, r_dir)
            replica_contents.remove(source_entry)
        elif source_entry in replica_contents and os.path.isdir(s_entry_path):
            # source_entry is a directory that exists in both s_dir and r_dir,
            # so sync_directories can be applied recursively.
            sync_directories(s_entry_path, r_entry_path)
            replica_contents.remove(source_entry)
        elif os.path.isfile(s_entry_path):
            # source_entry is a file that exists in s_dir but not r_dir, so it
            # can be copied over to r_dir.
            copy_file(s_entry_path, r_dir)
        else:
            # source_entry is a directory that exists in s_dir but not r_dir,
            # so it can be copied over to r_dir.
            copy_dir(s_entry_path, r_dir)
    # The contents of s_dir are now in r_dir, however, r_dir may still contain
    # files or folders that aren't in s_dir. By removing the names of files
    # and folders in both s_dir and r_dir from replica_contents during the
    # main loop of sync_directories, after its completion replica_contents
    # contains the names of all excess files and folders in r_dir.
    remove_from_dir(replica_contents, r_dir)


if __name__ == '__main__':
    args = parse_arguments()
    while not is_valid_replica(args.source_dir, args.replica_dir):
        args.replica_dir = input("Please enter a valid replica directory:")
        # The following if/elif statements strip unnecessary surrounding
        # characters from file paths inputted in quotes.
        if args.replica_dir[0] == "\"":
            args.replica_dir = args.replica_dir.strip("\"")
        elif args.replica_dir[0] == "\'":
            args.replica_dir = args.replica_dir.strip("\'")
        if args.replica_dir == "-1":
            exit()
    args.log_dir = check_for_log(args.log_dir)
    print("\nYou have run a one-way synchronization script. Synchronization "
          "will be performed as follows:")
    print(f"- Source directory: {args.source_dir}")
    print(f"- Replica directory: {args.replica_dir}")
    print(f"- Log file path: {args.log_dir}")
    print(f"- Synchronization frequency: {args.frequency} second(s)")
    print("Synchronization can still be aborted with a keyboard interrupt "
          "(Ctrl+C).\n")
    add_to_log(f'Synchronization begun with "{args.source_dir}" as the source '
               f'directory, "{args.replica_dir}" as the replica directory, '
               f'and a {args.frequency} second update frequency.')
    while True:
        try:
            sync_directories(args.source_dir, args.replica_dir)
            add_to_log(f"Synchronization process complete. Waiting for "
                       f"{args.frequency} second(s).")
            sync_completed_at = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(time.time()))
            print(f"[{sync_completed_at}] Synchronization process complete. "
                  f"Waiting for {args.frequency} second(s).")
            time.sleep(args.frequency)
        except KeyboardInterrupt:
            add_to_log("Synchronization terminated.\n")
            print("Synchronization terminated. Goodbye.\n")
            exit()

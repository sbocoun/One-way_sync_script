import time
import os
import hashlib
import shutil


def add_to_log(log_msg: str) -> None:
    """Append the current time and log_msg to the log file located in the
    same directory as the synchronization script."""

    log = open("synch_log.txt", "a")
    curr_time = time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(time.time()))
    log.write(f"[{curr_time}] {log_msg} \n")


def create_log_file() -> None:
    """Check the CWD for an existing log file and create one if it doesn't
    already exist."""
    if os.path.isfile("synch_log.txt"):
        print("\nLog file found.")
    else:
        add_to_log("Log file created.")
        print("\nLog file created in the CWD.")


def obtain_source_dir() -> str:
    """Obtain a valid directory path for the source folder. If an invalid path
    is given, users can either end the script or input another path."""

    while True:
        new_s_dir = input(r"Please input a valid source directory path: ")
        if new_s_dir == "-1":
            exit()
        elif os.path.isdir(new_s_dir):
            return os.path.abspath(new_s_dir)
        else:
            print(f'"{new_s_dir}" is not a valid directory, please try '
                  f'again. If you\'d like to terminate this script, '
                  f'please enter "-1" as the directory path.')


def is_subdir(a_path: str, b_path: str) -> bool:
    """Compare two valid directory paths and return True iff b_path is a
    subdirectory of a_path.

    Precondition: a_path and b_path are both valid directory paths."""

    # Normalize the directory path formats between OS
    norm_a_path = os.path.abspath(a_path)
    norm_b_path = os.path.abspath(b_path)
    if norm_a_path.startswith(norm_b_path):
        return True
    else:
        return False


def obtain_replica_dir(s_dir: str) -> str:
    """Obtain a valid directory path for the replica folder. If an invalid path
    is chosen, such as the current source path, users can either end the script
    or input another path.

    Precondition: s_path is a valid directory path."""

    while True:
        new_r_dir = input(r"Please input a valid replica directory path: ")
        if new_r_dir == "-1":
            exit()
        elif new_r_dir == s_dir:
            print(f'\"{new_r_dir}" has already been chosen as the source '
                  f'directory, please try again. If you\'d like to terminate '
                  f'this script, please enter "-1" as the directory path.')
        elif os.path.isdir(new_r_dir):
            if is_subdir(s_dir, new_r_dir):
                print(f'You cannot choose \"{new_r_dir}" because it is a '
                      f'subdirectory of the chosen source directory, '
                      f'please choose another replica directory. If you\'d '
                      f'like to terminate this script, please enter "-1" as '
                      f'the directory path.')
            elif is_subdir(new_r_dir, s_dir):
                print(f'You cannot choose \"{new_r_dir}" because it contains '
                      f'the chosen source directory, please choose another '
                      f'replica directory. If you\'d like to terminate this '
                      f'script, please enter "-1" as the directory path.')
            else:
                # Normalize the directory path format, e.g. between OS
                return os.path.abspath(new_r_dir)
        else:
            print(f'"{new_r_dir}" is not a valid directory, please try '
                  f'again. If you\'d like to terminate this script, please '
                  f'enter "-1" as the directory path.')


def obtain_sync_frequency() -> int:
    """Obtain a valid synchronization frequency, in minutes, by which the
    script will sync the source and replica folders. If an invalid duration is
    chosen, users can either end the script or make another input."""

    while True:
        new_update_duration = input("Please input your desired "
                                    "synchronization frequency (in minutes): ")
        if new_update_duration == "-1":
            exit()
        elif new_update_duration.isnumeric() and int(new_update_duration) > 0:
            return int(new_update_duration)
        else:
            print(f'"{new_update_duration}" is not a valid synchronization '
                  f'frequency, please try again. If you\'d like to terminate '
                  f'this script, please enter "-1" as the synchronization '
                  f'frequency.')


def confirm_sync_start(s_dir: str, r_dir: str, s_frequency: int) -> None:
    """Relay the chosen source path, replica path, and sync frequency back to
    the user for verification and terminate the script if requested."""

    confirmation = input(f"\nYou have chosen \"{s_dir}\" as the source "
                         f"folder, \"{r_dir}\" as the replica folder,"
                         f"\nand a {s_frequency}-minute synchronization "
                         f"frequency. If you'd like to terminate this script, "
                         f"please enter \"-1\". Any other input will prompt the"
                         f" script\nto begin synchronization. Please enter "
                         f"your response: ")
    if confirmation == "-1":
        exit()
    else:
        add_to_log(f"Synchronization begun with \"{s_dir}\" as the "
                   f"source directory, \"{r_dir}\" as the replica directory,"
                   f"and a {s_frequency}-minute synchronization "
                   f"frequency.")


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


def update_files(file_a: str, file_b: str, file_b_dir: str) -> None:
    """Compare file_a and file_b, and if they are not identical, replace file_b
    with file_a in file_b_dir.

    Precondition: file_a and file_b are valid file paths, while file_b_dir is a
    valid directory path."""

    if compare_files(file_a, file_b):
        return None
    else:
        os.remove(file_b)
        # While shutil may not preserve all file metadata, as opposed to native
        # OS shell commands via os.system, it is guaranteed to work with all
        # OS shells.
        shutil.copy2(file_a, file_b_dir)
        add_to_log(f'"{file_b} updated.')
        print(f'"{file_b} updated.')


def copy_dir(dir_a, dir_b) -> None:
    """Create a subdirectory in dir_b with the same name as dir_a and copy
     the contents of dir_a into it while logging every file that's copied.

    Precondition: dir_a and dir_b are valid directory paths"""

    dir_a_name = os.path.basename(dir_a)
    new_dir = dir_b + "\\" + dir_a_name
    os.mkdir(new_dir)
    dir_a_contents = os.listdir(dir_a)
    for entry in dir_a_contents:
        entry_path = dir_a + "\\" + entry
        new_dir_path = new_dir + "\\" + entry
        if os.path.isfile(entry_path):
            shutil.copy2(entry_path, new_dir_path)
            add_to_log(f'File "{entry_path}" copied to the directory '
                       f'"{new_dir_path}".')
            print(f'File "{entry_path}" copied to the directory '
                  f'"{new_dir_path}".')
        else:
            copy_dir(entry_path, new_dir_path)


def remove_from_dir(removable_paths: list[str], bloated_dir: str) -> None:
    """Remove the files and directories listed in removable_paths from
    corresponding_dir while logging every file that is removed.

    Precondition: corresponding_dir is a valid directory path and
    removable_paths contains only names of files or directories contained in
    corresponding_dir."""

    for removable_entry in removable_paths:
        removable_entry_path = bloated_dir + "\\" + removable_entry
        if os.path.isfile(removable_entry_path):
            os.remove(removable_entry_path)
            add_to_log(f'Removed the file "{removable_entry_path}" from '
                       f'"{bloated_dir}."')
            print(f'Removed the file "{removable_entry_path}" from '
                  f'"{bloated_dir}."')
        elif len(os.listdir(removable_entry_path)) == 0:
            os.rmdir(removable_entry_path)
        else:
            remove_from_dir(os.listdir(removable_entry_path),
                            removable_entry_path)


def sync_directories(s_dir: str, r_dir: str) -> None:
    """Compare the contents of s_dir and r_dir and adjust the contents of r_dir
    to match the contents of s_dir.

    Precondition: s_dir, r_dir are valid directory paths and neither is a
    subdirectory of the other."""

    source_contents = os.listdir(s_dir)
    replica_contents = os.listdir(r_dir)
    for entry in source_contents:
        s_entry_path = s_dir + "\\" + entry
        r_entry_path = r_dir + "\\" + entry
        if entry in replica_contents and os.path.isfile(s_entry_path):
            update_files(s_entry_path, r_entry_path, r_dir)
            replica_contents.remove(entry)
        elif entry in replica_contents and os.path.isdir(s_entry_path):
            sync_directories(s_entry_path, r_entry_path)
            replica_contents.remove(entry)
        elif os.path.isfile(s_entry_path):
            shutil.copy2(s_entry_path, r_dir)
            add_to_log(f'File "{s_entry_path}" copied to the directory '
                       f'"{r_dir}".')
            print(f'File "{s_entry_path}" copied to the directory '
                  f'"{r_dir}".')
        else:
            copy_dir(s_entry_path, r_dir)
    # All content from the source directory has either been copied to or updated
    # in the replica directory, so the remaining files in r_dir can be removed.
    remove_from_dir(replica_contents, r_dir)


if __name__ == '__main__':
    print("You have run a one-way synchronization script. You will be "
          "prompted to choose a source directory, replica directory, and "
          "synchronization frequency (in minutes). \nSynchronization "
          "can still be aborted after valid folders and a valid "
          "synchronization frequency have been chosen. After synchronization "
          "begins, all changes will be recorded\nin a log file located in the "
          "current working directory.")
    create_log_file()
    source_path = obtain_source_dir()
    replica_path = obtain_replica_dir(source_path)
    sync_frequency = obtain_sync_frequency()
    sec_until_sync = sync_frequency * 60
    confirm_sync_start(source_path, replica_path, sync_frequency)
    while True:
        try:
            sync_directories(source_path, replica_path)
            sync_completed_at = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(time.time()))
            add_to_log(f"Synchronization process complete. Waiting for "
                       f"{sync_frequency} minutes.")
            print(f"[{sync_completed_at}] Synchronization process complete. "
                  f"Waiting for {sync_frequency} minute(s).")
            time.sleep(sec_until_sync)
        except KeyboardInterrupt:
            add_to_log("Synchronization terminated.")
            print("Synchronization terminated. Goodbye.")
            exit()

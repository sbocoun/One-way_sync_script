# One-way_Sync_Script
A simple one-way synchronization script written in Python.

**usage:** one_way_sync.py  [-h]  [-f FREQUENCY]  [-l LOG_DIR]  source_dir  replica_dir

**Verbose description:** One-way synchronization script between two chosen directories. After execution, and then periodically after a certain duration (the chosen frequency), the contents of the replica directory are modified to match the source  
directory.

| Positional arguments: |  |
| --- | --- |
| source_dir |  The system path of the desired source directory. An error will be raised if the path contains a <br /> space but is not enclosed in quotes.   |
| replica_dir |  The system path of the desired replica directory. An error will be raised if the path contains a <br /> space but is not enclosed in quotes. |
	
| options: |  |
| --- | --- |
| -h, --help | Show this help message and exit. |
|-f FREQUENCY, --frequency FREQUENCY | The duration (in seconds) between synchronizations. Defaults to 60 seconds. |
|-l LOG_DIR, --log_dir LOG_DIR | If a log file already exists, you may enter its directory path. <br /> If it doesn't, or you would like to create a log in a different directory, <br /> please enter the desired directory path. If the path contains a space, <br /> please surround it with quotes. If log_dir is left blank, or the inputted <br /> path is invalid, the log file will be created in the current working directory. |

**Additional Restrictions:** source_dir and replica_dir cannot be subdirectories of each other, nor can they be the same directory.

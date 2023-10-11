# One-way_Sync_Script
A simple one-way synchronization script written in Python.

usage: one_way_sync.py [-h] [-f FREQUENCY] [-l LOG_DIR] source_dir replica_dir

One-way synchronization script between two chosen directories. After execution, and then periodically after a certain duration (the chosen frequency), the contents of the replica directory are modified to match the source  
directory.

positional arguments:
  source_dir            The system path of the desired source directory. An error will be raised if the path contains a space but is not enclosed in quotes.
  replica_dir           The system path of the desired replica directory. An error will be raised if the path contains a space but is not enclosed in quotes.
	
options:
  -h, --help            show this help message and exit
  -f FREQUENCY, --frequency FREQUENCY
                        The duration (in seconds) between synchronizations. Defaults to 60 seconds.
  -l LOG_DIR, --log_dir LOG_DIR
                        If a log file already exists, you may enter its directory path. If it doesn't, or you would like to create a log in a different directory, please enter the desired directory path. If the path 
												contains a space, please surround it with quotes. If log_dir is left blank, or the inputted path is invalid, the log file wll be created in the current working directory.

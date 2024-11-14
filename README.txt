###File types:

.icc: IntelliCheck commands file containing imported data from a BackBox machine
.icy: IntelliCheck icy commands translated from .icc files


&&&Folder structure:

icc - Default folder for imported .icc files. Translating is done from this folder.
icy - Default folder for .icy files. Compiling is done from this folder.
compiled - Default folder for compiled .icc files. Uploading is done from this folder.


***Core files:

importIC.py - Imports data from BackBox and stores it in .icc files so they can get translated to .icy files.

translator.py - Translates .icc files into .icy files so they can be edited and modified using the midlanguage syntax.

compiler.py - Compiles .icy syntax into .icc data files that can be pushed to the BackBox and stores them in "compiled" folder.

uploader.py - Uploads .icc files from "compiled" folder to BackBox.

icylib.py - Contains necessary functions that are used by multiple scripts, along side the configuration file path for the BackBox machine to fetch/upload to and folder path used for storing .icy and .icc files.

conf folder - contains the json file(s) with the IP, username and password in order to connect to the BackBox machine(s).

syntax_description - Detailed explaination of the icy syntax.


**Highly recommended for comfort while working with a shell and VIM:

alias.sh - Used for "icyget" and "icyset" CLI commands instead of running python3 icyset/icyget. Needs to be sourced by your shell's configuration file.

icyget.py - Script that combines importIC.py and translator.py functionality for an easy to use single command that downloads and converts automations into .icy file and opens it with VIM.
Example usage:
python3 icyget.py fortinet fortigate ssl
Will search for an IntelliCheck signature that contains the three words (order non-specific, case insensitive) "fortinet","fortigate","ssl" on the BackBox server configured, allowing you to select the signature via a numbered list, or download all.
Will attempt to open in VIM if single signature selected.

icyopen.py - Script that opens .icy file in vim, instead of using vim PATH/TO/ICYDIR/ICYFILE.icy
Example usage:
python3 icyopen.py icy_file_name
will open icy_file_name.icy from your icydir in VIM.

icyset.py - Script that combines compiler.py and uploader.py to allow compiling and uploading from .icy script to BackBox IntelliCheck.
Example usage:
python3 icyset.py icy/icy_file.icy
Will compile icy_file.icy into icc file and store it in your icc folder, then upload it to the BackBox machine.


*addatives:

.gitignore

commonCommands.icy - Command commands that can be easily copy pasted.


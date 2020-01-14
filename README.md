# raname_and_upload

A utility tool to batch prepend created/modified dates to file names and upload to Google Drive for backup.

It was created due to Google Drive not preserving original file creation/modification dates. Once it is uploaded, you can only see when a file was uploaded and modified inside Google Drive. This is inconvenient. 

To solve this, this script prepends original file creation or modification datetime to the file name and then uploads it to a folder you can specify on your Google Drive. If the folder is not specified, it defaults to "AutoUploaded" folder the script will create on Google Drive. 

For uploading to work, you need to get a Google Drive API and save it to the app folder. File needs to be named "client_secrets.json"

This article describes how to correctly set up Google Drive API: 
https://medium.com/@annissouames99/how-to-upload-files-automatically-to-drive-with-python-ee19bb13dda

```
optional arguments:
  -h, --help            show this help message and exit
  -id INPUT_DIRECTORY, --input_directory INPUT_DIRECTORY
                        Input folder where files you want to modify and upload
                        to cloud (default: None)
  -if INPUT_FILE, --input_file INPUT_FILE
                        Input file you want to modify and upload to cloud
                        (default: None)
  -d DESTINATION_FOLDER, --destination_folder DESTINATION_FOLDER
                        the destination folder (default: AutoUploaded)
  -ud, --update_date    Use this argument if you need to remove old modified
                        date prefix from your files before uploading (default:
                        False)
  -cr, --creation_date  Use this argument if you need to prepend a creation
                        date instead of modified date to your file (default:
                        False)
  -uo, --upload_only    Use this argument if only need to upload files without
                        renaming (default: False)
```
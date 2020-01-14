import os, time
from platform import system
import argparse
import sys
import collections
import ntpath
from datetime import datetime
import dateutil.parser as date_parser
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from psutil import disk_partitions
from subprocess import Popen, PIPE
from gdrive_uploader import GdriveUploader


class MyParser(argparse.ArgumentParser):
    """A parser that displays argparse's help message by default."""

    def error(self, message):
        self.print_help()
        sys.exit(1)


class FileWorker:
    DEFAULT_DATETIME_FORMAT = "%Y-%m-%d_%H:%M:%S"
    DEFAULT_DESTINATION_FOLDER = "AutoUploaded"

    def __init__(self):
        self.gdrive = GdriveUploader()
        self.parser = MyParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-id",
            "--input_directory",
            help="""Input folder where files you want to modify and upload to cloud""",
        )

        group.add_argument(
            "-if",
            "--input_file",
            help="""Input file you want to modify and upload to cloud""",
        )

        self.parser.add_argument(
            "-d",
            "--destination_folder",
            help="the destination folder",
            default=self.DEFAULT_DESTINATION_FOLDER,
        )

        self.parser.add_argument(
            "-ud",
            "--update_date",
            action="store_true",
            help="""Use this argument if you need to remove old modified date prefix 
            from your files before uploading""",
        )

        self.parser.add_argument(
            "-cr",
            "--creation_date",
            action="store_true",
            help="""Use this argument if you need to prepend a creation date
            instead of modified date to your file""",
        )

    def main(self):
        args = self.parser.parse_args()
        parsed = self.check_args(args)

        if not parsed:
            print("")
            self.parser.error("Bad arguments.")

        (
            self.origin,
            self.origin_type,
            self.destination_folder,
            self.update_date,
            self.creation_date,
        ) = parsed

        files = self.rename()
        print(files)
        for file in files:
            if os.path.isfile(file["path"]):
                self.gdrive.upload(
                    file["filename"], file["path"], self.destination_folder
                )
            else:
                print(file + " is not a file")

    def rename_file(self, origin):
        head, tail = ntpath.split(origin)
        extension = tail.split(".")[1]
        path = head
        date = self.get_date_prefix(origin)
        file_name = tail.split(".")[0]
        if self.update_date and "--" in file_name:
            file_name = file_name.split("--")[1]
        os.rename(origin, f"{path}/{date}--{file_name}.{extension}")
        return {
            "filename": f"{date}--{file_name}.{extension}",
            "path": path + "/" + date + "--" + file_name + "." + extension,
        }

    def rename(self):
        if self.origin_type == "file":
            return [self.rename_file(self.origin)]
        else:
            try:
                renamed_files = []
                for path in self.get_list_of_files(self.origin):
                    full_path = os.path.join(self.origin, path)
                    if os.path.isfile(full_path):
                        rfile = self.rename_file(full_path)
                        renamed_files.append(rfile)
                return renamed_files
            except:
                return []

    def get_list_of_files(self, dirName):
        """
            For the given path, get the List of all files in the directory tree 
        """
        # create a list of file and sub directories
        # names in the given directory
        list_of_files = os.listdir(dirName)
        all_files = list()
        # Iterate over all the entries
        for entry in list_of_files:
            # Create full path
            full_path = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + self.get_list_of_files(full_path)
            else:
                all_files.append(full_path)

        return all_files

    def get_fs_type(self, path):
        """
        Get file system type
        """
        root_type = ""
        for part in disk_partitions():
            if part.mountpoint == "/":
                root_type = part.fstype
                continue

            if path.startswith(part.mountpoint):
                return part.fstype

        return root_type

    def get_file_creation_time_in_ext_filesystem(self, path):
        try:
            cmd = ["./birth", path]
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate(timeout=120)
            return self.decode_from_timestamp(out.decode("utf-8"))
        except:
            return None

    def get_file_creation_time(self, path):
        """
        Try to get the date that a file was created depending on the OS
        In Linux if the filesystem is other than ext*, modified date is used instead
        """
        if system() == "Windows":
            return self.decode_from_timestamp(str(os.path.getctime(path)))
        else:
            stat = os.stat(path)
            try:
                return self.decode_from_timestamp(str(stat.st_birthtime))
            except AttributeError:
                return self.get_file_creation_time_in_ext_filesystem(path)

    def decode_from_timestamp(self, tstamp):
        dt_object = datetime.fromtimestamp(int(tstamp.split(".")[0]))
        return date_parser.parse(str(dt_object)).strftime(self.DEFAULT_DATETIME_FORMAT)

    def get_date_prefix(self, file):
        if self.creation_date:
            return self.get_file_creation_time(file)
        else:
            mod_time = time.ctime(os.path.getmtime(f"{file}"))
            return date_parser.parse(mod_time).strftime(self.DEFAULT_DATETIME_FORMAT)

    def check_args(self, args):
        """
        Checks that command-line arguments are valid.
        """
        error = None
        origin = args.input_file or args.input_directory
        origin_type = None
        destination_folder = args.destination_folder or self.DEFAULT_DESTINATION_FOLDER
        update_date = False or args.update_date
        creation_date = False or args.creation_date
        if os.path.isfile(origin):
            origin_type = "file"
        elif os.path.isdir(origin):
            origin_type = "folder"
        else:
            print(f"{origin} does not exist")
            error = True

        if error:
            return None

        return_params = collections.namedtuple(
            "Params",
            [
                "origin",
                "origin_type",
                "destination_folder",
                "update_date",
                "creation_date",
            ],
        )
        return return_params(
            origin, origin_type, destination_folder, update_date, creation_date
        )


if __name__ == "__main__":
    FileWorker().main()

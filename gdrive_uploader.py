from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GdriveUploader:
    def __init__(self):
        self.gauth = GoogleAuth()
        # Try to load saved client credentials
        self.gauth.LoadCredentialsFile("mycreds.txt")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile("mycreds.txt")

        self.drive = GoogleDrive(self.gauth)

    def upload(self, filename, path, destination_folder):
        directory = self.get_drive_folder(destination_folder)
        f = self.drive.CreateFile({"title": filename, "parents":  [{"id": directory}]})
        f.SetContentFile(path)
        f.Upload()

    def get_folder_id(self, foldername):
        file_list = self.drive.ListFile(
            {"q": "'root' in parents and trashed=false"}
        ).GetList()
        id = None
        for file1 in file_list:
            if file1["title"] == foldername:
                id = file1["id"]
        return id

    def get_drive_folder(self, foldername):
        id = self.get_folder_id(foldername)
        if id == None:
            new_folder = self.drive.CreateFile(
                {"title": foldername, "mimeType": "application/vnd.google-apps.folder"}
            )
            new_folder.Upload()
            id = self.get_folder_id(foldername)
        return id

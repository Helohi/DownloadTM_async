from pydrive2.auth import GoogleAuth as ga2
from pydrive2.drive import GoogleDrive as gd2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from addition.functions import log, run_in_thread


def CreateAuthFiles(gauthparam):
    """ Create authorized variable """
    gauthparam.LoadCredentialsFile("mycreds.txt")
    if gauthparam.credentials is None:
        log("Bot don't find mycreds.txt or you don't authorized")
    elif gauthparam.access_token_expired:
        gauthparam.Refresh()
    else:
        gauthparam.Authorize()
    gauthparam.SaveCredentialsFile("mycreds.txt")
    return gauthparam


# Authorization in Google Drive
gauth, gauth2 = GoogleAuth(), ga2()
gauth = CreateAuthFiles(gauth)
gauth2 = CreateAuthFiles(gauth2)


def upload_file(path: str, title: str = None, folder: str = None) -> GoogleDrive.CreateFile:
    """ Uploading files to the Google Drive """
    # Preparing variables
    if not folder:
        folder = '1azbHPoW8rOeeVV08szvRWQAWrjJcn0mz'
    if not title:
        title = 'video.mp4'

    # Creating a google drive variable
    drive = GoogleDrive(gauth)

    # Creating a file to folder
    file = drive.CreateFile({'title': title, 'parents': [{'id': folder}]})
    file.SetContentFile(path)
    try:
        file.Upload()
    except BaseException:
        try:
            log("PyDrive couldn't deliver it, going to PyDrive2")
            drive2 = gd2(gauth2)

            file = drive2.CreateFile(
                {'title': title, 'parents': [{'id': folder}]})
            file.SetContentFile(path)
            file.Upload()
        except BaseException as err:
            log(type(err), err)
            raise ValueError('File is too big')

    # Insert the permission and uploading file.
    new_permission = {
        'id': 'anyoneWithLink',
        'type': 'anyone',
        'value': 'anyoneWithLink',
        'withLink': True,
        'role': 'reader'
    }
    permission = file.auth.service.permissions().insert(
        fileId=file['id'], body=new_permission, supportsTeamDrives=True).execute(http=file.http)

    del permission
    return file['alternateLink']


@run_in_thread
def delete_all_files_from_folders(folder: str = None, num: int = 20):
    """ Delete files from folder  """
    if not folder:
        folder = '1azbHPoW8rOeeVV08szvRWQAWrjJcn0mz'

    # Get list of files
    file_list = get_all_files(folder=folder)[::-1]

    # Deleting all files from folders
    for file in file_list[:num]:
        file.Delete()

    del file_list
    return True


@run_in_thread
def delete_one_file(file_name: str, folder: str = None):
    if folder is None:
        folder = '1azbHPoW8rOeeVV08szvRWQAWrjJcn0mz'

    # Delete file
    try:
        for file in get_all_files(folder=folder):
            if file['title'] == file_name:
                file.Delete()
                return True
    except BaseException as err:
        log(f"{type(err)} : {err}")
    return False


def get_all_files(folder: str = '1azbHPoW8rOeeVV08szvRWQAWrjJcn0mz') -> list:
    """ Get all files from folder in Google Drive
    :param folder: Folder from wich all files will get or None"""
    # Checking vars
    drive = GoogleDrive(gauth)
    if not folder:
        return drive.ListFile({'q': "trashed=false"}).GetList()

    # List all files
    return drive.ListFile({'q': f"'{folder}' in parents and trashed=false"}).GetList()


@run_in_thread
def check_drive(max_files: int = 30, decrease: int = 20):
    if len(get_all_files('1azbHPoW8rOeeVV08szvRWQAWrjJcn0mz')) > max_files:
        delete_all_files_from_folders(num=decrease)


if __name__ == '__main__':
    print(len(get_all_files()))
    if (amount := int(input('How many files to delete (to cancel write "0")\n'))) != 0:
        delete_all_files_from_folders(num=amount)

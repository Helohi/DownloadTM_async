from functions import google_search, install_youtube, is_data_wrong, links
from googleapi import upload_file, delete_one_file
from os import remove


def test_is_data_wrong():
    assert is_data_wrong('https://www.youtube.com/?video=ZKSDJRFKR') == ''
    assert is_data_wrong('https://www.youtube.com/?playlist=FSDserfsdfSESe') == "This is a playlist, please choose a video"
    assert is_data_wrong('https://www.google.com/url=fsdfsdfsdfsdfsd') == "Please send https://youtu... link(not google link)"
    assert is_data_wrong('https://files.icq.net') == "It is neither link nor query"


def test_install_video():
    assert install_youtube(url='https://www.youtube.com/watch?v=GM_3IlttE-I', res=360, path='Test.mp4') != None
    remove("Test.mp4")


def test_google_search():
    assert len(google_search(query='hello', limit=16)[1]) == 16


def test_upload_file():
    file_name = 'text1.txt'
    with open(f'{file_name}', 'w') as file:
        file.write('it is test file')
    assert upload_file(f'{file_name}', title=f'{file_name}') !=  None
    assert delete_one_file(f'{file_name}') == True
    remove(f'{file_name}')

def test_links():
    assert len(links()[1]) == 5 or len(links()[1]) == 1
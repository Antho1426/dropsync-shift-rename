#!/usr/local/bin/python3.8


# dropsync_shift_rename.py


import glob
import os
import platform
import shutil
from argparse import ArgumentParser
from datetime import datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path

import osascript  # pip3 install osascript
from PIL import Image  # pip3 install Pillow
from termcolor import colored

# ====================
DEBUG_MODE_ON = False
# ====================


# Setting the current working directory automatically

project_path = os.getcwd()  # getting the path leading to the current working directory
os.getcwd()  # printing the path leading to the current working directory
# setting the current working directory based on the path leading to the current working directory
os.chdir(project_path)


# Required packages


# Initializations
DASH_SIGN: str = '-'
POINT_SIGN: str = '.'
SLASH_SIGN: str = '/'
UNDERSCORE_SIGN: str = '_'
SENT_FOLDER: str = 'Sent'
PRIVATE_FOLDER: str = 'Private'
WHATSAPP_TYPE: str = 'WhatsApp'
TELEGRAM_TYPE: str = 'Telegram'
SNAPCHAT_TYPE: str = 'Snapchat'
MUSIC_DOWNLOAD_TYPE: str = 'MusicDownload'
VIDMATE_TYPE: str = 'VidMate'
INSTANDER_TYPE: str = 'Instander'
WHATSAPP_SHORT: str = 'WA'
DROPSYNCFILES_DIRECTORY_PATH: str = '/Users/anthony/Dropbox/DropsyncFiles/Media_UnidirectionalSync_AndroidToMac'
CAMERA_UPLOADS_DIRECTORY_PATH: str = '/Users/anthony/Dropbox/Camera Uploads'
RETURNED_MESSAGE: str = '\n⚠️ List of empty folders (i.e. that currently do not contain files to be moved):'
NB_EMPTY_FOLDERS: int = 0


# Helper functions

def copy_dir(dir_path):
    """
    Creates a copy of the directory in which media files are synced using
    Dropsync Ultimate Android app.

    Args:
        dir_path (str): Source directory path in which media files are synced.

    Returns:
        dir_path_dst (str): Destination directory path (i.e., directory holding
                            the source directory copy).
    """

    # Computing current date
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Defining source and destination directories
    dir_path_src = dir_path
    dir_path_dst = dir_path_src + '_Copy_' + dt_string
    # Copying source directory (and its entire content, including hidden files) to destination directory
    shutil.copytree(dir_path_src, dir_path_dst, symlinks=False, ignore=None,
                    copy_function=shutil.copy2, ignore_dangling_symlinks=False, dirs_exist_ok=False)

    return dir_path_dst


def notify(message: str, title: str, subtitle: str, sound: str):
    """
    Posts macOS X notification.

    Args:
        message (str): The message
        title (str): The title
        subtitle (str): The subtitle
        sound (str): The macOS X sound
    """

    code, out, err = osascript.run(
        'display notification "{0}" with title "{1}" subtitle "{2}" sound name "{3}"'.format(message, title, subtitle, sound))


def empty_folder(directory_path: str):
    """
    Empties a folder by removing all the files and folders it contains.

    Args:
        directory_path (str): The path of the folder whose contents are to be deleted.
    """

    files = glob.glob(directory_path + '/*')
    for f in files:
        if os.path.isdir(f):
            # In case of a folder
            shutil.rmtree(f)
        else:
            # In case of a file
            os.remove(f)


def move_files(files_path_list: list, dest_folder_path: str):
    """
    Moves all the files from a directory to another.

    Args:
        files_path_list (list): List containing the paths of the files to be moved.
        dest_folder_path (str): Path of the destination folder in which the files
                                have to be moved.
    """

    translation_dict = {
        " ": "\ ",
        "(": "\(",
        ")": "\)",
        "[": "\[",
        "]": "\]",
        "&": "\&",
        "'": "\\'",  # handling paths including apostrophe
    }

    for file_path in files_path_list:
        src_path = file_path
        command = 'mv ' + src_path.translate(str.maketrans(translation_dict)) + \
            ' ' + dest_folder_path.translate(str.maketrans(translation_dict))
        returned_value = os.system(command)
        # prints "0" (this means that the command run successfully)
        print("\tmv 'returned_value': ", returned_value)


def creation_date(file_path: str) -> float:
    """
    - Tries to get the date in [ms] when a file was created, falling back to when
      it was last modified if that isn't possible.
    - See http://stackoverflow.com/a/39501288/1709587 for explanation.
    - Cf. "python get file date creation"
      (https://www.codegrepper.com/code-examples/python/python+get+file+date+creation)

    Args:
        file_path (str): The path of the file whose creation date has to be retrieved.

    Returns:
        creation_date (str): The creation date in [ms] of the file.
    """

    if platform.system() == 'Windows':
        creation_date = os.path.getctime(file_path)
        return creation_date

    else:
        stat = os.stat(file_path)
        try:
            creation_date = stat.st_birthtime
            return creation_date

        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            creation_date = stat.st_mtime
            return creation_date


def ms_to_date(file_path: str) -> str:
    """
    - Converts milliseconds to my standard date format YYYY-MM-DD_HH-MM-SS.
    - Cf. "How to convert milliseconds to date and time format?"
      (https://stackoverflow.com/questions/56468152/how-to-convert-milliseconds-to-date-and-time-format)

    Args:
        file_path (str): The path of the file whose creation date has to be retrieved.

    Returns:
        date_formatted (str): The date formatted as YYYY-MM-DD_HH-MM-SS.
    """

    date_ms = creation_date(file_path)
    date_formatted = str(datetime.fromtimestamp(
        date_ms)).replace(':', '-').replace(' ', '_')

    return date_formatted


def rename_files(list_of_file_paths: list, type: str) -> list:
    """
    Renames all the files of a particular folder.

    Args:
        - list_of_file_paths (list): List containing all the file paths of the
          particular folder.
        - type (str): The type of platform the file is coming from (e.g.
          'WhatsApp', 'Telegram', etc.).

    Returns:
        renamed_list_of_file_paths (list): List containing all the renamed
        file paths of the particular folder.
    """

    renamed_list_of_file_paths = []
    if len(list_of_file_paths) > 0:
        parent_folder_path = str(
            Path(list_of_file_paths[0]).parent) + SLASH_SIGN

        if type == WHATSAPP_TYPE:
            for file_path in list_of_file_paths:
                if not file_path.split('/')[-1][0].isdigit():
                    file_date = ms_to_date(file_path)
                    file_num = file_path.split(
                        '/')[-1].split('-')[2].replace(WHATSAPP_SHORT, WHATSAPP_TYPE + UNDERSCORE_SIGN)
                    file_path_new = parent_folder_path + file_date + UNDERSCORE_SIGN + file_num
                    renamed_list_of_file_paths.append(file_path_new)
                    os.rename(file_path, file_path_new)
                else:
                    print(colored('⚠️  Warning!\n', 'red'),
                          '  WhatsApp files have already been renamed!')
                    renamed_list_of_file_paths.append(file_path)

        elif type == TELEGRAM_TYPE:
            for file_path in list_of_file_paths:
                file_date = ms_to_date(file_path)
                file_num = TELEGRAM_TYPE + UNDERSCORE_SIGN + \
                    file_path.split('/')[-1].split('_')[1]
                file_path_new = parent_folder_path + file_date + UNDERSCORE_SIGN + file_num
                renamed_list_of_file_paths.append(file_path_new)
                os.rename(file_path, file_path_new)

        elif type == SNAPCHAT_TYPE:
            for file_path in list_of_file_paths:
                file_date = ms_to_date(file_path)
                file_num = SNAPCHAT_TYPE + UNDERSCORE_SIGN + \
                    file_path.split('.')[0][-4:] + \
                    POINT_SIGN + file_path.split('.')[-1]
                file_path_new = parent_folder_path + file_date + UNDERSCORE_SIGN + file_num
                renamed_list_of_file_paths.append(file_path_new)
                os.rename(file_path, file_path_new)

        elif type == VIDMATE_TYPE or type == MUSIC_DOWNLOAD_TYPE:
            for file_path in list_of_file_paths:
                file_date_long = ms_to_date(file_path)
                file_date = file_date_long.split('.')[0]
                file_name = file_path.split('/')[-1]
                file_path_new = parent_folder_path + file_date + UNDERSCORE_SIGN + file_name
                renamed_list_of_file_paths.append(file_path_new)
                os.rename(file_path, file_path_new)

        elif type == INSTANDER_TYPE:
            for file_path in list_of_file_paths:
                file_date_long = ms_to_date(file_path)
                file_date = file_date_long.split('_')[0]
                instagram_name = file_path.split('/')[-2]
                file_name = file_path.split('/')[-1]
                file_number_and_extension = file_name.split('-')[-1]
                file_path_new = parent_folder_path + file_date + UNDERSCORE_SIGN + \
                    instagram_name + UNDERSCORE_SIGN + file_number_and_extension
                renamed_list_of_file_paths.append(file_path_new)
                os.rename(file_path, file_path_new)

    else:
        print(colored('⚠️  Warning!\n', 'red'),
              '  The list of files to rename is empty!')

    return renamed_list_of_file_paths


def get_list_of_files(dir_path: str) -> list:
    """
    - Creates a list of files in directory and subdirectories using os.listdir()
      (For the given path, gets the list of all files in the directory tree).
    - Cf. "Python : How to get list of files in directory and sub directories"
      (https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/)

    Args:
        dir_path (str): Path of the target directory.

    Returns:
        files_list (list): List containing the paths of the different files
        contained in the given directory and its subdirectories.
    """

    files_and_folders_list = os.listdir(dir_path)
    files_list = list()
    # Iterating over all the entries
    for entry in files_and_folders_list:
        # Creating full path
        full_path = os.path.join(dir_path, entry)
        # If entry is a directory then getting the list of files in this directory
        if os.path.isdir(full_path):
            files_list = files_list + get_list_of_files(full_path)
        # Appending the file to the list in case it is not a hidden file
        elif not full_path.split('/')[-1].startswith('.'):
            files_list.append(full_path)

    return files_list


def convert_to_mp3(list_of_audio_paths: list) -> list:
    """
    Converts audio a list of audio files of any type to mp3.

    Args:
        list_of_audio_paths (list): List containing the paths of the different
        audio files.

    Returns:
        list_of_audio_paths_mp3 (list): List containing the paths of the
        different audio files with ".mp3" extension.
    """

    list_of_audio_paths_mp3 = []
    if len(list_of_audio_paths) > 0:
        parent_folder_path = str(
            Path(list_of_audio_paths[0]).parent) + SLASH_SIGN
        for audio_path in list_of_audio_paths:
            # Getting the extension of the audio file
            file_extension = audio_path.split('/')[-1].split('.')[-1]
            # Temporarily renaming the audio file
            temp_name = 'audio_file' + POINT_SIGN + file_extension
            temp_path = parent_folder_path + temp_name
            os.rename(audio_path, temp_path)
            temp_path_mp3 = temp_path.replace(file_extension, 'mp3')
            # Converting audio file to ".mp3" format
            command = 'ffmpeg -i ' + \
                temp_path.replace(' ', '\ ') + ' ' + \
                temp_path_mp3.replace(' ', '\ ')
            returned_value = os.system(command)
            # prints "0" (this means that the command run successfully)
            print("  ffmpeg 'returned_value': ", returned_value)
            # Renaming back the audio file to its original name
            audio_path_mp3 = audio_path.replace(file_extension, 'mp3')
            os.rename(temp_path_mp3, audio_path_mp3)
            # Removing the original renamed audio file
            os.remove(temp_path)
            # Appending the audio file path to "list_of_audio_paths_mp3"
            list_of_audio_paths_mp3.append(audio_path_mp3)
    else:
        print(colored('⚠️  Warning!\n', 'red'),
              '  The list of files to convert to ".mp3" is empty!')

    return list_of_audio_paths_mp3


# Parsing the input argument
if not DEBUG_MODE_ON:
    # Creating ArgumentParser
    parser = ArgumentParser(description='"dropsync_shift_rename.py" is a Python\
        program that automatically renames, moves and eventually converts any\
        kind of files from the "DropsyncFiles" folder to the "Camera Uploads"\
        folder.')
    args = parser.parse_args()
    # Copying directory content (in order to keep all synchronised files intact
    # in order to be able to identify where the error came from in the event
    # that an error has occurred during the execution of the program below)
    DROPSYNCFILES_DIRECTORY_PATH_COPY = copy_dir(DROPSYNCFILES_DIRECTORY_PATH)


# Main process
# Launching initial macOS X notification
notify(title='dropsync_shift_rename.py',
       subtitle='Running dropsync_shift_rename.py script',
       message='→ Renaming and moving process started...',
       sound='Blow')


# ░██╗░░░░░░░██╗██╗░░██╗░█████╗░████████╗░██████╗░█████╗░██████╗░██████╗░
# ░██║░░██╗░░██║██║░░██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
# ░╚██╗████╗██╔╝███████║███████║░░░██║░░░╚█████╗░███████║██████╔╝██████╔╝
# ░░████╔═████║░██╔══██║██╔══██║░░░██║░░░░╚═══██╗██╔══██║██╔═══╝░██╔═══╝░
# ░░╚██╔╝░╚██╔╝░██║░░██║██║░░██║░░░██║░░░██████╔╝██║░░██║██║░░░░░██║░░░░░
# ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝░░░░░
# (Made with "BIG TEXT Letters Font Generator" (cf.: https://fsymbols.com/generators/tarty/))
# 1) WhatsApp
print('\n1) WhatsApp')
print('-----------')

# Targeted folder paths
if DEBUG_MODE_ON:
    WHATSAPP_ANIMATED_GIFS_PATH: str = project_path + \
        '/tests/WhatsApp/WhatsApp Animated Gifs/'
    WHATSAPP_AUDIO_PATH: str = project_path + '/tests/WhatsApp/WhatsApp Audio/'
    WHATSAPP_IMAGES_PATH: str = project_path + '/tests/WhatsApp/WhatsApp Images/'
    WHATSAPP_STICKERS_PATH: str = project_path + '/tests/WhatsApp/WhatsApp Stickers/'
    WHATSAPP_VIDEOS_PATH: str = project_path + '/tests/WhatsApp/WhatsApp Video/'
    WHATSAPP_VOICE_NOTES_PATH: str = project_path + \
        '/tests/WhatsApp/WhatsApp Voice Notes/'
    CAMERA_UPLOADS_PATH: str = project_path + '/tests/Camera Uploads/'
else:
    WHATSAPP_ANIMATED_GIFS_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Animated Gifs/'
    WHATSAPP_AUDIO_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/WhatsApp/WhatsApp Audio/'
    WHATSAPP_IMAGES_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Images/'
    WHATSAPP_STICKERS_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Stickers/'
    WHATSAPP_VIDEOS_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/WhatsApp/WhatsApp Video/'
    WHATSAPP_VOICE_NOTES_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Voice Notes/'
    CAMERA_UPLOADS_PATH: str = CAMERA_UPLOADS_DIRECTORY_PATH

# Untargeted folder paths
if DEBUG_MODE_ON:
    WHATSAPP_MISC_PATH: str = project_path + '/tests/WhatsApp/MISC/'
    WHATSAPP_WALLPAPER_PATH: str = project_path + '/tests/WhatsApp/WallPaper/'
    WHATSAPP_DOCUMENTS_PATH: str = project_path + \
        '/tests/WhatsApp/WhatsApp Documents/'
    WHATSAPP_PROFILE_PHOTOS_PATH: str = project_path + \
        '/tests/WhatsApp/WhatsApp Profile Photos/'
else:
    WHATSAPP_MISC_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/WhatsApp/MISC/'
    WHATSAPP_WALLPAPER_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/WhatsApp/WallPaper/'
    WHATSAPP_DOCUMENTS_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Documents/'
    WHATSAPP_PROFILE_PHOTOS_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + \
        '/WhatsApp/WhatsApp Profile Photos/'
untargeted_folders_list = [
    WHATSAPP_MISC_PATH,
    WHATSAPP_WALLPAPER_PATH,
    WHATSAPP_DOCUMENTS_PATH,
    WHATSAPP_PROFILE_PHOTOS_PATH
]

# A) "WhatsApp Images"
print(' A) "WhatsApp Images"')
if os.path.isdir(WHATSAPP_IMAGES_PATH):
    # A.1) Renaming "WhatsApp Images" file names
    print('  A.1) Renaming "WhatsApp Images" file names')
    extensions = ['*.jpg', '*.jpeg']
    list_of_img_paths = []
    for ext in extensions:
        list_of_img_paths += glob.glob(WHATSAPP_IMAGES_PATH + ext)
    renamed_list_of_img_paths = rename_files(list_of_img_paths, WHATSAPP_TYPE)
    if len(renamed_list_of_img_paths) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Images'
        NB_EMPTY_FOLDERS += 1
    # A.2) Emptying "Sent" folder
    print('  A.2) Emptying "Sent" folder')
    empty_folder(WHATSAPP_IMAGES_PATH + SENT_FOLDER)
    # A.3) Emptying "Private" folder
    print('  A.3) Emptying "Private" folder')
    empty_folder(WHATSAPP_IMAGES_PATH + PRIVATE_FOLDER)
    # A.4) Moving the files to the "Camera Uploads" folder
    print('  A.4) Moving the files to the "Camera Uploads" folder')
    move_files(renamed_list_of_img_paths, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# B) "WhatsApp Video"
print(' B) "WhatsApp Video"')
if os.path.isdir(WHATSAPP_VIDEOS_PATH):
    # B.1) Renaming "WhatsApp Video" file names
    print('  B.1) Renaming "WhatsApp Video" file names')
    list_of_vid_paths = glob.glob(WHATSAPP_VIDEOS_PATH + '*.mp4')
    renamed_list_of_vid_paths = rename_files(list_of_vid_paths, WHATSAPP_TYPE)
    if len(renamed_list_of_vid_paths) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Video'
        NB_EMPTY_FOLDERS += 1
    # B.2) Emptying "Sent" folder
    print('  B.2) Emptying "Sent" folder')
    empty_folder(WHATSAPP_VIDEOS_PATH + SENT_FOLDER)
    # B.3) Emptying "Private" folder
    print('  B.3) Emptying "Private" folder')
    empty_folder(WHATSAPP_VIDEOS_PATH + PRIVATE_FOLDER)
    # B.4) Moving the files to the "Camera Uploads" folder
    print('  B.4) Moving the files to the "Camera Uploads" folder')
    move_files(renamed_list_of_vid_paths, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# C) "WhatsApp Stickers"
print(' C) "WhatsApp Stickers"')
if os.path.isdir(WHATSAPP_STICKERS_PATH):
    list_of_sticker_paths = glob.glob(WHATSAPP_STICKERS_PATH + '*.webp')
    for sticker_path in list_of_sticker_paths:
        # C.1) Converting sticker from ".webp" to ".png"
        print('  C.1) Converting sticker from ".webp" to ".png"')
        # (Cf. "Image Conversion (JPG ⇄ PNG/JPG ⇄ WEBP) with Python",
        # https://medium.com/@ajeet214/image-type-conversion-jpg-png-jpg-webp-png-webp-with-python-7d5df09394c9)
        im = Image.open(sticker_path).convert('RGBA')
        im.save(sticker_path.replace('.webp', '.png'), 'png')
        # C.2) Deleting ".webp" sticker
        print('  C.2) Deleting ".webp" sticker')
        os.remove(sticker_path)
    # C.3) Renaming PNG "WhatsApp Stickers" file names
    print('  C.3) Renaming PNG "WhatsApp Stickers" file names')
    list_of_sticker_png_paths = glob.glob(WHATSAPP_STICKERS_PATH + '*.png')
    renamed_list_of_sticker_paths = rename_files(
        list_of_sticker_png_paths, WHATSAPP_TYPE)
    if len(renamed_list_of_sticker_paths) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Stickers'
        NB_EMPTY_FOLDERS += 1
    # C.4) Moving the files to the "Camera Uploads" folder
    print('  C.4) Moving the files to the "Camera Uploads" folder')
    move_files(renamed_list_of_sticker_paths, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# D) "WhatsApp Audio"
print(' D) "WhatsApp Audio"')
if os.path.isdir(WHATSAPP_AUDIO_PATH):
    # D.1) Shifting all files from the "Sent" directory in the "WhatsApp Audio" directory
    if os.path.isdir(WHATSAPP_AUDIO_PATH+SENT_FOLDER+SLASH_SIGN):
        print('  D.1) Shifting all files from the "Sent" directory in the "WhatsApp Audio" directory')
        files_in_sent = [WHATSAPP_AUDIO_PATH+SENT_FOLDER+SLASH_SIGN+f for f in listdir(
            WHATSAPP_AUDIO_PATH+SENT_FOLDER+SLASH_SIGN) if isfile(join(WHATSAPP_AUDIO_PATH+SENT_FOLDER+SLASH_SIGN, f))]
        move_files(files_in_sent, WHATSAPP_AUDIO_PATH)
    # D.2) Getting all files in "WhatsApp Audio" directory (".opus", ".mp3", ".m4a", etc.)
    print('  D.2) Getting all files in "WhatsApp Audio" directory (".opus", ".mp3", ".m4a", etc.)')
    files_in_whatsapp_audio = [f for f in listdir(
        WHATSAPP_AUDIO_PATH) if isfile(join(WHATSAPP_AUDIO_PATH, f))]
    # D.3) Removing hidden files from list of files to convert
    print('  D.3) Removing hidden files from list of files to convert')
    files_in_whatsapp_audio = [
        f for f in files_in_whatsapp_audio if not (f.startswith('.'))]
    # D.4) Listing all paths of audio files
    print('  D.4) Listing all paths of audio files')
    list_of_audio_paths = [WHATSAPP_AUDIO_PATH +
                           f for f in files_in_whatsapp_audio]
    # D.5) Renaming "WhatsApp Audio" file names
    print('  D.5) Renaming "WhatsApp Audio" file names')
    renamed_list_of_audio_paths = rename_files(
        list_of_audio_paths, WHATSAPP_TYPE)
    if len(renamed_list_of_audio_paths) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Audio'
        NB_EMPTY_FOLDERS += 1
    # D.6) Removing ".mp3" files from list of files to convert
    print('  D.6) Removing ".mp3" files from list of files to convert')
    list_of_audio_paths_already_mp3 = [
        f for f in renamed_list_of_audio_paths if f.endswith('.mp3')]
    list_of_audio_paths_no_mp3 = [
        f for f in renamed_list_of_audio_paths if f not in list_of_audio_paths_already_mp3]
    # D.7) Converting audio files to mp3
    print('  D.7) Converting audio files to mp3')
    list_of_audio_paths_mp3 = convert_to_mp3(
        list_of_audio_paths_no_mp3) + list_of_audio_paths_already_mp3
    # D.8) Moving the files to the "Camera Uploads" folder
    print('  D.8) Moving the files to the "Camera Uploads" folder')
    move_files(list_of_audio_paths_mp3, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# E) "WhatsApp Voice Notes"
print(' E) "WhatsApp Voice Notes"')
if os.path.isdir(WHATSAPP_VOICE_NOTES_PATH):
    # E.1) Gathering all (".opus") files of the different subfolders
    print('  E.1) Gathering all (".opus") files of the different subfolders')
    list_of_files_in_subfolders = get_list_of_files(WHATSAPP_VOICE_NOTES_PATH)
    # E.2) Moving all (".opus") files at the root of the "WhatsApp Voice Notes" folder
    print('  E.2) Moving all (".opus") files at the root of the "WhatsApp Voice Notes" folder')
    move_files(list_of_files_in_subfolders, WHATSAPP_VOICE_NOTES_PATH)
    # E.3) Deleting the emptied folders
    print('  E.3) Deleting the emptied folders')
    folders_list = [WHATSAPP_VOICE_NOTES_PATH+f for f in os.listdir(
        WHATSAPP_VOICE_NOTES_PATH) if os.path.isdir(WHATSAPP_VOICE_NOTES_PATH+f)]
    for f in folders_list:
        os.rmdir(f)
    # E.4) Renaming "WhatsApp Voice Notes" file names
    print('  E.4) Renaming "WhatsApp Voice Notes" file names')
    list_of_files_in_whatsapp_voice_notes = [
        '/'.join(f.split('/')[:-2])+SLASH_SIGN+f.split('/')[-1] for f in list_of_files_in_subfolders]
    renamed_list_of_files = rename_files(
        list_of_files_in_whatsapp_voice_notes, WHATSAPP_TYPE)
    if len(renamed_list_of_files) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Voice Notes'
        NB_EMPTY_FOLDERS += 1
    # E.5) Converting audio files to mp3
    print('  E.5) Converting audio files to mp3')
    list_of_files_mp3 = convert_to_mp3(renamed_list_of_files)
    # E.6) Moving the files to the "Camera Uploads" folder
    print('  E.6) Moving the files to the "Camera Uploads" folder')
    move_files(list_of_files_mp3, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# F) "WhatsApp Animated Gifs"
print(' F) "WhatsApp Animated Gifs"')
if os.path.isdir(WHATSAPP_ANIMATED_GIFS_PATH):
    # F.1) Renaming "WhatsApp Animated Gifs" file names
    print('  F.1) Renaming "WhatsApp Animated Gifs" file names')
    list_of_anim_gifs_paths = glob.glob(WHATSAPP_ANIMATED_GIFS_PATH + '*.mp4')
    renamed_list_of_anim_gifs_paths = rename_files(
        list_of_anim_gifs_paths, WHATSAPP_TYPE)
    if len(renamed_list_of_anim_gifs_paths) == 0:
        RETURNED_MESSAGE += '\n • WhatsApp Animated Gifs'
        NB_EMPTY_FOLDERS += 1
    # F.2) Emptying "Sent" folder
    print('  F.2) Emptying "Sent" folder')
    empty_folder(WHATSAPP_ANIMATED_GIFS_PATH + SENT_FOLDER)
    # F.3) Emptying "Private" folder
    print('  F.3) Emptying "Private" folder')
    empty_folder(WHATSAPP_ANIMATED_GIFS_PATH + PRIVATE_FOLDER)
    # F.4) Moving the files to the "Camera Uploads" folder
    print('  F.4) Moving the files to the "Camera Uploads" folder')
    move_files(renamed_list_of_anim_gifs_paths, CAMERA_UPLOADS_PATH)
else:
    NB_EMPTY_FOLDERS += 1

# G) Empty untargeted folders
for folder_path in untargeted_folders_list:
    empty_folder(folder_path)


# ████████╗███████╗██╗░░░░░███████╗░██████╗░██████╗░░█████╗░███╗░░░███╗
# ╚══██╔══╝██╔════╝██║░░░░░██╔════╝██╔════╝░██╔══██╗██╔══██╗████╗░████║
# ░░░██║░░░█████╗░░██║░░░░░█████╗░░██║░░██╗░██████╔╝███████║██╔████╔██║
# ░░░██║░░░██╔══╝░░██║░░░░░██╔══╝░░██║░░╚██╗██╔══██╗██╔══██║██║╚██╔╝██║
# ░░░██║░░░███████╗███████╗███████╗╚██████╔╝██║░░██║██║░░██║██║░╚═╝░██║
# ░░░╚═╝░░░╚══════╝╚══════╝╚══════╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝
# 2) Telegram
print('\n2) Telegram')
print('-----------')

if DEBUG_MODE_ON:
    TELEGRAM_PATH: str = project_path + '/tests/Telegram/'
else:
    TELEGRAM_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/Telegram/'
TELEGRAM_IMAGES_PATH: str = TELEGRAM_PATH + 'Telegram Images/'

# A) Emptying all folders apart from "Telegram Images"
print(' A) Emptying all folders apart from "Telegram Images"')
telegram_directory_contents = os.listdir(TELEGRAM_PATH)
for folder in telegram_directory_contents:
    telegram_directory = TELEGRAM_PATH+folder+SLASH_SIGN
    if os.path.isdir(telegram_directory) and telegram_directory != TELEGRAM_IMAGES_PATH:
        print(f' Emptying "{folder}" folder...')
        empty_folder(TELEGRAM_PATH+folder)

# B) "Telegram Images"
print(' B) "Telegram Images"')
# B.1) Renaming "Telegram Images" file names
print('  B.1) Renaming "Telegram Images" file names')
list_of_img_paths = glob.glob(TELEGRAM_IMAGES_PATH + "/*.jpg")
renamed_list_of_img_paths = rename_files(list_of_img_paths, TELEGRAM_TYPE)
if len(renamed_list_of_img_paths) == 0:
    RETURNED_MESSAGE += '\n • Telegram Images'
    NB_EMPTY_FOLDERS += 1
# B.2) Moving the files to the "Camera Uploads" folder
print('  B.2) Moving the files to the "Camera Uploads" folder')
move_files(renamed_list_of_img_paths, CAMERA_UPLOADS_PATH)


# ░██████╗███╗░░██╗░█████╗░██████╗░░█████╗░██╗░░██╗░█████╗░████████╗
# ██╔════╝████╗░██║██╔══██╗██╔══██╗██╔══██╗██║░░██║██╔══██╗╚══██╔══╝
# ╚█████╗░██╔██╗██║███████║██████╔╝██║░░╚═╝███████║███████║░░░██║░░░
# ░╚═══██╗██║╚████║██╔══██║██╔═══╝░██║░░██╗██╔══██║██╔══██║░░░██║░░░
# ██████╔╝██║░╚███║██║░░██║██║░░░░░╚█████╔╝██║░░██║██║░░██║░░░██║░░░
# ╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░░░░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░
# 3) Snapchat
print('\n3) Snapchat')
print('-----------')

if DEBUG_MODE_ON:
    SNAPCHAT_PATH: str = project_path + '/tests/Snapchat/'
else:
    SNAPCHAT_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/Snapchat/'

# A) Renaming "Snapchat" file names
print(' A) Renaming "Snapchat" file names')
extensions = ['*.JPG', '*.jpg', '*.mp4']
list_of_file_paths = []
for ext in extensions:
    list_of_file_paths += glob.glob(SNAPCHAT_PATH + ext)
renamed_list_of_file_paths = rename_files(list_of_file_paths, SNAPCHAT_TYPE)
if len(renamed_list_of_file_paths) == 0:
    RETURNED_MESSAGE += '\n • Snapchat'
    NB_EMPTY_FOLDERS += 1

# B) Moving the files to the "Camera Uploads" folder
print(' B) Moving the files to the "Camera Uploads" folder')
move_files(renamed_list_of_file_paths, CAMERA_UPLOADS_PATH)


# ███╗░░░███╗██╗░░░██╗░██████╗██╗░█████╗░██████╗░░█████╗░░██╗░░░░░░░██╗███╗░░██╗██╗░░░░░░█████╗░░█████╗░██████╗░
# ████╗░████║██║░░░██║██╔════╝██║██╔══██╗██╔══██╗██╔══██╗░██║░░██╗░░██║████╗░██║██║░░░░░██╔══██╗██╔══██╗██╔══██╗
# ██╔████╔██║██║░░░██║╚█████╗░██║██║░░╚═╝██║░░██║██║░░██║░╚██╗████╗██╔╝██╔██╗██║██║░░░░░██║░░██║███████║██║░░██║
# ██║╚██╔╝██║██║░░░██║░╚═══██╗██║██║░░██╗██║░░██║██║░░██║░░████╔═████║░██║╚████║██║░░░░░██║░░██║██╔══██║██║░░██║
# ██║░╚═╝░██║╚██████╔╝██████╔╝██║╚█████╔╝██████╔╝╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚███║███████╗╚█████╔╝██║░░██║██████╔╝
# ╚═╝░░░░░╚═╝░╚═════╝░╚═════╝░╚═╝░╚════╝░╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚══╝╚══════╝░╚════╝░╚═╝░░╚═╝╚═════╝░
# 4) MusicDownload
# (YouTube video to mp3 converter Android app)
print('\n4) MusicDownload')
print('--------------')

if DEBUG_MODE_ON:
    MUSIC_DOWNLOAD_PATH: str = project_path + '/tests/MusicDownload/'
else:
    MUSIC_DOWNLOAD_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/MusicDownload/'

# A) Converting the audio files from ".m4a" to ".mp3"
print(' A) Converting the audio files from ".m4a" to ".mp3"')
list_of_audio_paths_m4a = glob.glob(MUSIC_DOWNLOAD_PATH + "/*.m4a")
list_of_files_mp3_converted = convert_to_mp3(list_of_audio_paths_m4a)

# B) Making list of converted ".mp3" files and original ".mp3" files
print(' B) Making list of converted ".mp3" files and original ".mp3" files')
list_of_files_mp3 = glob.glob(MUSIC_DOWNLOAD_PATH + "/*.mp3")

# C) Renaming the audio files
print(' C) Renaming the audio files')
renamed_list_of_mp3_paths = rename_files(
    list_of_files_mp3, MUSIC_DOWNLOAD_TYPE)
if len(renamed_list_of_mp3_paths) == 0:
    RETURNED_MESSAGE += '\n • MUSIC_DOWNLOAD'
    NB_EMPTY_FOLDERS += 1

# C) Moving the files to the "Camera Uploads" folder
print(' C) Moving the files to the "Camera Uploads" folder')
move_files(renamed_list_of_mp3_paths, CAMERA_UPLOADS_PATH)


# ██╗░░░██╗██╗██████╗░███╗░░░███╗░█████╗░████████╗███████╗
# ██║░░░██║██║██╔══██╗████╗░████║██╔══██╗╚══██╔══╝██╔════╝
# ╚██╗░██╔╝██║██║░░██║██╔████╔██║███████║░░░██║░░░█████╗░░
# ░╚████╔╝░██║██║░░██║██║╚██╔╝██║██╔══██║░░░██║░░░██╔══╝░░
# ░░╚██╔╝░░██║██████╔╝██║░╚═╝░██║██║░░██║░░░██║░░░███████╗
# ░░░╚═╝░░░╚═╝╚═════╝░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
# 5) VidMate
# (YouTube video downloader Android app)
print('\n5) VidMate')
print('----------')

if DEBUG_MODE_ON:
    VIDMATE_PATH: str = project_path + '/tests/VidMate/'
else:
    VIDMATE_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/VidMate/'
VIDMATE_DOWNLOAD_PATH: str = VIDMATE_PATH + 'download/'

# A) Emptying all folders apart from "download"
print(' A) Emptying all folders apart from "download"')
vidmate_directory_contents = os.listdir(VIDMATE_PATH)
for folder in vidmate_directory_contents:
    vidmate_directory = VIDMATE_PATH + folder+SLASH_SIGN
    if os.path.isdir(vidmate_directory) and vidmate_directory != VIDMATE_DOWNLOAD_PATH:
        print(f' Emptying "{folder}" folder...')
        empty_folder(VIDMATE_PATH+folder)

# B) "download"
print(' B) "download"')
# Checking if the "download" folder exists
if os.path.isdir(VIDMATE_DOWNLOAD_PATH):
    # B.1) Renaming "download" file names
    print('  B.1) Renaming "download" file names')
    list_of_vid_paths = glob.glob(VIDMATE_DOWNLOAD_PATH + "/*.mp4")
    list_of_aud_paths = glob.glob(VIDMATE_DOWNLOAD_PATH + "/*.mp3")
    list_of_paths = list_of_vid_paths + list_of_aud_paths
    renamed_list_of_paths = rename_files(list_of_paths, VIDMATE_TYPE)
    if len(renamed_list_of_paths) == 0:
        RETURNED_MESSAGE += '\n • VidMate'
        NB_EMPTY_FOLDERS += 1
    # B.2) Removing all the files with extension ".smi" and ".apk" from the "download" folder
    print('  B.2) Removing all the files with extension ".smi" and ".apk" from the "download" folder')
    # Gathering the path of all files in the "download" folder
    file_paths_download_folder = []
    for path in os.listdir(VIDMATE_DOWNLOAD_PATH):
        full_path = os.path.join(VIDMATE_DOWNLOAD_PATH, path)
        if os.path.isfile(full_path):
            file_paths_download_folder.append(full_path)
    # Deleting unwanted files from the "download" folder
    extensions = ('.smi', '.apk')
    for i in range(len(file_paths_download_folder)):
        current_file_path = file_paths_download_folder[i]
        ends_with_unwanted_extension = current_file_path.endswith(extensions)
        if ends_with_unwanted_extension:
            os.remove(current_file_path)
    # B.3) Moving the files to the "Camera Uploads" folder
    print('  B.3) Moving the files to the "Camera Uploads" folder')
    move_files(renamed_list_of_paths, CAMERA_UPLOADS_PATH)


# ██╗███╗░░██╗░██████╗████████╗░█████╗░███╗░░██╗██████╗░███████╗██████╗░
# ██║████╗░██║██╔════╝╚══██╔══╝██╔══██╗████╗░██║██╔══██╗██╔════╝██╔══██╗
# ██║██╔██╗██║╚█████╗░░░░██║░░░███████║██╔██╗██║██║░░██║█████╗░░██████╔╝
# ██║██║╚████║░╚═══██╗░░░██║░░░██╔══██║██║╚████║██║░░██║██╔══╝░░██╔══██╗
# ██║██║░╚███║██████╔╝░░░██║░░░██║░░██║██║░╚███║██████╔╝███████╗██║░░██║
# ╚═╝╚═╝░░╚══╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚══════╝╚═╝░░╚═╝
# 6) Instander
# (Instagram clone and image/video downloader Android app)
print('\n6) Instander')
print('------------')

if DEBUG_MODE_ON:
    INSTANDER_PATH: str = project_path + '/tests/Instander/'
else:
    INSTANDER_PATH: str = DROPSYNCFILES_DIRECTORY_PATH + '/Instander/'

# A) Visiting elements in "Instander" root folder
print(' A) Visiting elements in "Instander" root folder')

renamed_list_of_all_media_paths = []

for file in os.listdir(INSTANDER_PATH):

    elem_path = os.path.join(INSTANDER_PATH, file)

    if os.path.isdir(elem_path):

        # A.1) Navigating inside current subfolder
        print('  A.1) Navigating inside current subfolder')
        list_of_media_paths = [os.path.join(
            elem_path, media) for media in os.listdir(elem_path)]

        # A.1.1) Converting any ".webp" files to ".png" files
        print('   A.1.1) Converting any ".webp" files to ".png" files')
        list_of_media_paths_with_potential_webp = list_of_media_paths
        list_of_media_paths = []
        for media_path in list_of_media_paths_with_potential_webp:
            if media_path[-5:] == '.webp':
                # Converting from ".webp" to "png"
                im = Image.open(media_path).convert('RGBA')
                media_path_png = media_path[:-5]+'.png'
                im.save(media_path_png, 'png')
                # Deleting ".webp" file
                os.remove(media_path)
                # Updating media_path
                media_path = media_path_png
            list_of_media_paths.append(media_path)

        # A.1.2) Renaming media file names (image and video)
        print('   A.1.2) Renaming media file names (image and video)')
        renamed_list_of_media_paths = rename_files(
            list_of_media_paths, INSTANDER_TYPE)
        renamed_list_of_all_media_paths = renamed_list_of_all_media_paths + \
            renamed_list_of_media_paths

        # A.1.3) Moving the files to the "Camera Uploads" folder
        print('   A.1.3) Moving the files to the "Camera Uploads" folder')
        move_files(renamed_list_of_media_paths, CAMERA_UPLOADS_PATH)

    else:
        # A.2) Deleting image and video files at "Instander" folder root
        # (Because those are the media I personally posted on Instagram)
        # (Removing the file situated at "elem_path" since it is precisely a file
        # (and hence NOT a subfolder))
        print(' A.2) Deleting image and video files at "Instander" folder root')
        os.remove(elem_path)

if len(renamed_list_of_all_media_paths) == 0:
    RETURNED_MESSAGE += '\n • Instander'
    NB_EMPTY_FOLDERS += 1


# Launching final macOS X notification
if NB_EMPTY_FOLDERS > 0:
    print(RETURNED_MESSAGE)

if NB_EMPTY_FOLDERS == 10:
    notify(title='dropsync_shift_rename.py',
           subtitle='⚠️️ Process aborted!',
           message='→ There are currently no files to move from DropsyncFiles to Camera Uploads!',
           sound='Sosumi')
else:
    notify(title='dropsync_shift_rename.py',
           subtitle='🏆 Process successful!',
           message='→ Files have been renamed and moved from DropsyncFiles to Camera Uploads!',
           sound='Hero')


# Exiting the Terminal window (using AppleScript command) in case the program
# has been triggered by Alfred and the folder "/Users/anthony/Dropbox/DropsyncFiles/Media_UnidirectionalSync_AndroidToMac"
# (which path is stored in the variable "DROPSYNCFILES_DIRECTORY_PATH" and
# which corresonds to the directory in which media files are synced) has a size
# of less than 1[MB] (meaning that the program hence run successfully)
# Computing "Media_UnidirectionalSync_AndroidToMac" folder size
num_bytes = sum([sum(map(lambda fname: os.path.getsize(os.path.join(directory, fname)), files))
                for directory, folders, files in os.walk(DROPSYNCFILES_DIRECTORY_PATH)])
num_mega_bytes = round(num_bytes/1e6, 2)
# (Cf.: How do I close the Terminal in OSX from the command line? (https://superuser.com/questions/158375/how-do-i-close-the-terminal-in-osx-from-the-command-line/1385450))
if not DEBUG_MODE_ON:
    if num_mega_bytes < 1:
        osascript.run('tell application "iTerm2" to close first window')
        # Removing copy of directory in whch media files are synced only if the
        # program run successfully (this way, if there was a problem in the
        # execution of the program, the original structure of the directory in
        # which media files are synced remains saved for further investigations)
        shutil.rmtree(DROPSYNCFILES_DIRECTORY_PATH_COPY)
    else:
        warning_message = colored(
            'WARNING!', 'red', attrs=['reverse', 'blink'])
        print(f'{warning_message} Something may have gone wrong. The size of the \
                folder "Media_UnidirectionalSync_AndroidToMac" is not zero and amounts \
                to {num_mega_bytes}[MB]! Note that a copy of the original structure \
                of the directory in which media files are synced has been saved \
                at the same location on the computer for further investigations.')

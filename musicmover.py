from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError
#from mutagen.mp3 import _util
from mutagen.mp3 import MPEGInfo
from mutagen.flac import FLAC
from mutagen.ogg import OggFileType
from mutagen.aac import AAC
from mutagen.id3 import ID3, ID3NoHeaderError

from shutil import copyfile
import os
import sys

walk_dir = "/media/leo/2TBVol1/Music" #sys.argv[1]
copy_dir = "/media/leo/2TBVol2/High Quality Music"

print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

dirs = {}

def copy_file(base_dir, filename):
    full_dir = copy_dir + "/" + base_dir
    source_dir = walk_dir + "/" + base_dir

    if not os.path.isdir(full_dir):
        os.makedirs(full_dir)
        print("making dir : " + full_dir) 
    
    source_filename = source_dir + "/" + filename
    dest_filename = full_dir + "/" + filename
    #print ("Copying " + source_filename + " to " + dest_filename)

    if not os.path.isfile(dest_filename):
        copyfile(source_filename, dest_filename)
    

with open("too_low_bitrate.txt", 'wb') as low_bitrate_files:
    first_dir_char = ''
    for root, subdirs, files in os.walk(walk_dir):
        #print('--\nroot = ' + root)
        list_file_path = os.path.join(root, 'my-directory-list.txt')
        #print('list_file_path = ' + list_file_path)
        if not root in dirs:
            dirs[root] = False
    
        files_other_than_mp3 = []
        base_dir2 = root[len(walk_dir):]
        if len(base_dir2) > 0:
            first_dir_char_lower = base_dir2[1].lower()
            #print(first_dir_char_lower)
            if first_dir_char != first_dir_char_lower:
                print(first_dir_char_lower)
                first_dir_char = first_dir_char_lower
        #print(base_dir2)
        for filename in files:
            
            file_path = os.path.join(root, filename)
            if filename == "my-directory-list.txt":
                print("deleted directory list")
                os.remove(file_path)

            base_dir = file_path[len(walk_dir)+1:-len(filename)-1]
            base_dirs = base_dir.split('/')

           #print(str(base_dirs))
            
            extension = os.path.splitext(filename)[1]
            
            if extension == ".mp3":
                try:
                    mp3data = MP3(file_path)
                except HeaderNotFoundError:
                    print("ERROR - MP3 header not found for file " + file_path)
                    low_bitrate_files.write("No ID3: " + filename)
                except ID3NoHeaderError:
                    print("ERROR - MP3 header not found for file " + file_path)
                    low_bitrate_files.write("No ID3: " + filename)
                try:
                    id3data = ID3(file_path)
                except ID3NoHeaderError:
                    print("ERROR - MP3 header not found for file " + file_path)
                    low_bitrate_files.write("No ID3: " + filename)
                #mpeginfo = MPEGInfo(mp3data)
                bitrate = mp3data.info.bitrate / 1000
                if bitrate > 160:
                    #print("Keeping this track: " + filename)
                    dirs[root] = True
                    copy_file(base_dir, filename)
                # Write low quality files to text file for acquiring later
                else:
                    album = ""
                    artist = ""
                    title = ""
                    try:
                        album = id3data['TALB'].text[0]
                    except KeyError:
                        pass
                    try:
                        artist = id3data['TPE1'].text[0]
                    except KeyError:
                        pass
                    try:
                        title = id3data['TIT2'].text[0]
                    except KeyError:
                        pass
                    low_bitrate_track = artist + " - " + title + " - " + album
                    try:
                        low_bitrate_files.write(low_bitrate_track)
                    except UnicodeEncodeError:
                        print("Couldnt encode " + low_bitrate_track)
                    low_bitrate_files.write(b'\n')
            elif extension == ".flac":
                pass
                copy_file(base_dir, filename)
            elif extension == ".ogg":
                pass
                copy_file(base_dir, filename)
            elif extension == ".wma":
                low_bitrate_files.write("WMA file - " + filename)
                low_bitrate_files.write(b'\n')
            else:
                #print("Extension: " + extension)
                files_other_than_mp3.append(file_path)
                #print("Found something else " + extension + " : " + file_path)
        if dirs[root] == True:
            for file in files_other_than_mp3:
                #print("Copying other file" + file)
                copy_file(base_dir2, filename)

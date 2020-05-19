from PIL import Image
import os
import os.path
import datetime
import dateutil.parser
import shutil


def get_photos_in_folder(folder):
    result_files = []

    for root, directories, files in os.walk(folder):
        for file in files:
            extension = os.path.splitext(file)[1]
            if ('.jpg' in extension) or ('.jpeg' in extension) or ('.png' in extension):
                result_files.append(os.path.join(root, file))

    return result_files


def photo_has_date_taken(filePath):
    try:
        if Image.open(path)._getexif()[36867]:
            return True
    except:
        return False


def get_photo_date_taken(filePath):
    photoDateTime = Image.open(filePath)._getexif()[36867]
    dateTaken = datetime.datetime.strptime(photoDateTime, '%Y:%m:%d %H:%M:%S')
    return dateTaken


def has_photo_date_in_filename(filePath):
    try:
        filename = os.path.basename(filePath)
        if (dateutil.parser.parse(filename, fuzzy_with_tokens=True)[0]):
            return True
    except:
        return False


def get_photo_date_in_filename(filePath):
    filename = os.path.basename(filePath)
    date = dateutil.parser.parse(filename, fuzzy_with_tokens=True)[0]
    return date


def sort_photos_with_date_taken(sourceFolder, targetFolder):
    allPhotosToSort = get_photos_in_folder(sourceFolder)

    photosWithDateTaken = []
    for file in allPhotosToSort:
        if photo_has_date_taken(file):
            photosWithDateTaken.append(file)

    for file in photosWithDateTaken:
        # replace this with code to move the file to targetFolder/year/month/day/filename
        print(file)


def sort_photos_with_date_in_filename(sourceFolder, targetFolder):
    allPhotosToSort = get_photos_in_folder(sourceFolder)

    photosWithDateInFilename= []
    for file in allPhotosToSort:
        if has_photo_date_in_filename(file):
            photosWithDateInFilename.append(file)

    for file in photosWithDateInFilename:
        filename = os.path.basename(file)
        fileDate = get_photo_date_in_filename(file)
        targetRootPath = targetFolder + "/" + str(fileDate.strftime('%Y')) + "/" + str(fileDate.strftime('%m')) + "/" + str(fileDate.strftime('%d')) + "/"
        target = targetRootPath + filename

        print ("**************")
        print("SOURCE: " + file)
        print("DESTINATION: " + target)

        try:
            os.makedirs(os.path.dirname(targetRootPath), exist_ok=True)
            shutil.move(file, target)
            print ("STATUS: COMPLETED")
        except:
            print ("STATUS: FAILED")


print(sort_photos_with_date_in_filename("SOURCE HERE", "DESTINATION HERE"))

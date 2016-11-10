import subprocess
import os
import shutil
import re


class Printer:
    def __init__(self, params):
        pass

    def description(self):
        return 'Ouputs the file name'

    def apply(self, dirname):
        print(dirname)
        return True


class Archiver:
    def __init__(self, params):
        self.destinationDirectory = params.get('destinationDirectory', '.')

    def description(self):
        desc = 'Creates a 7zip archive of the file'
        if self.destinationDirectory != '.':
            desc += ' and save it to {}'.format(self.destinationDirectory)
        return desc

    def apply(self, filename):
        FNULL = open(os.devnull, 'w')
        if self.destinationDirectory != '.':
            match = re.search(r"[^\\\/]*$", filename)
            if match:
                archiveName = os.path.join(
                    self.destinationDirectory, match.group()) + '.7z'
            else:
                return False
        else:
            archiveName = self.destinationDirectory + '.7z'

        return 0 == subprocess.call(
            [self.binaryLocation, 'a', '-mx9', '-t7z',
             os.path.join(self.destinationDirectory, archiveName),
             filename], stdout=FNULL, stderr=subprocess.STDOUT)


class FileDeleter:
    def __init__(self, params):
        pass

    def description(self):
        return 'Deletes the file'

    def apply(self, filename):
        if os.path.isdir(filename):
            shutil.rmtree(filename)
        else:
            os.remove(filename)
        return True


class FileCopier:
    def __init__(self, params):
        self.destinationDirectory = params.get('destinationDirectory', None)

    def description(self):
        return 'Copies the file to {}'.format(self.destinationDirectory)

    def apply(self, filename):
        if os.path.isdir(filename):
            raise Exception("{} is a directory".format(filename))
        shutil.copy2(filename, self.destinationDirectory)


class TextFinder():
    def __init__(self, params):
        self.pattern = params.get('pattern', None)
        self.outputFormat = params.get('outputFormat', None)

    def description(self):
        return 'Search for a pattern in the file. ({})'

    def apply(self, filename):
        with open(filename, 'r') as f:
            content = f.read()

        for match in re.finditer(self.pattern, content,
                                 re.DOTALL | re.MULTILINE):

            if self.outputFormat:
                result = re.sub(self.pattern, self.outputFormat, match.group())
            else:
                result = match.group()
            print(result)

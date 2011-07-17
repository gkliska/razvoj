# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2010   Raphaël Valyi                                    #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

import sys
import zipfile
import os
import os.path
import getopt
import urllib
import tarfile
import shutil
import subprocess



class unzip:
    def __init__(self, verbose = False, percent = 10):
        self.verbose = verbose
        self.percent = percent
        
    def extract(self, file, dir):
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)

        # create directory structure to house files
        self._createstructure(file, dir)

        num_files = len(zf.namelist())
        percent = self.percent
        divisions = 100 / percent
        perc = int(num_files / divisions)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):

            if self.verbose == True:
                print "Extracting %s" % name
            elif perc > 0 and (i % perc) == 0 and i > 0:
                complete = int (i / perc) * percent
                print "%s%% complete" % complete

            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()


    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)


    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)

        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs



class installer:

    def install_terminatooor(self, kettle_root_directory):
        print "getting TerminatOOOR plugin from the Internet, this can take a while (>10Mo)..."
        urllib.urlretrieve('http://github.com/downloads/rvalyi/terminatooor/terminatooor1.2.1.zip', kettle_root_directory + 'terminatooor.zip')
        unzipper = unzip()
        unzipper.extract(kettle_root_directory + 'terminatooor.zip', kettle_root_directory + 'data-integration/plugins/steps/terminatooor')
        shutil.move(kettle_root_directory + 'data-integration/plugins/steps/terminatooor/jruby-ooor.jar', kettle_root_directory + 'data-integration/libext/jruby-ooor.jar')

    def update_terminatoor(self, kettle_root_directory):
        print kettle_root_directory
        os.remove(kettle_root_directory + 'data-integration/libext/jruby-ooor.jar')
        shutil.rmtree(kettle_root_directory+'data-integration/plugins/steps/terminatooor')
        self.install_terminatooor(kettle_root_directory)

    def install(self, kettle_root_directory, install_agilebi=True):
        unzipper = unzip()
        print "checking if Kettle is possibly already installed..."

        kettle_dir = kettle_root_directory + 'data-integration'
        if os.path.isdir(kettle_dir):
	        raise Exception("looks like Pentaho Data Integration (Kettle) is already installed!\nPlease remove the %s directory first if you want to re-install it." % kettle_dir)

        print "checking Java version, should be >= 1.6..."
        try:
	        retcode = subprocess.call(["java", "-version"])
        except:
	        raise Exception("looks like you don't have Java installed! Please install Java (1.6 or superior) first!")

        print "getting Pentaho Data Integration (Kettle) from the Internet, this can take a while (>80Mo)..."
        urllib.urlretrieve('http://sourceforge.net/projects/pentaho/files/Data%20Integration/4.1.0-RC1/pdi-ce-4.1.0-RC1.tar.gz/download', kettle_root_directory + 'kettle.tar.gz')
        try:
            tar = tarfile.open(kettle_root_directory + 'kettle.tar.gz', 'r:gz')
            for item in tar:
                tar.extract(item, kettle_root_directory)
        except:
            name = os.path.basename(sys.argv[0])
            print name[:name.rfind('.')], '<filename>'

        self.install_terminatooor(kettle_root_directory)
        os.mkdir(kettle_root_directory + '/data-integration/openerp_tmp/')

        if install_agilebi:
	        print "getting the AgileBI plugin from the Internet, this can take a while (>80Mo)..."
	        urllib.urlretrieve('ftp://download.pentaho.org/client/agile-bi/pmv-1.0.2-RC1.zip', kettle_root_directory + 'agilebi.zip')
	        unzipper.extract(kettle_root_directory + 'agilebi.zip', kettle_root_directory + 'data-integration/plugins/spoon')


if __name__ == '__main__':
	installer = installer()
	installer.install('../../')
	print "Done!"

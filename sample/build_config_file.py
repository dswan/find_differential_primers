#!/usr/bin/env python
#
# build_config_file.py
#
# Script to build a configuration file for the find_differential_primers.py
# script that designs candidate diagnostic primers.
#
# This script takes as input a directory containing only FASTA format files.
# Each FASTA file contains sequences relating to one biological entity that 
# will be distinguished.
#
# This script generates a config file suitable for generating candidate
# diagnostic primers per biological entity. That is, each entity (individual
# FASTA file) is assumed to specify a single class. No other class 
# information is considered.
#
# (c) The James Hutton Institute 2013
# Author: Leighton Pritchard
#
# Contact:
# leighton.pritchard@hutton.ac.uk
#
# Leighton Pritchard,
# Information and Computing Sciences,
# James Hutton Institute,
# Errol Road,
# Invergowrie,
# Dundee,
# DD6 9LH,
# Scotland,
# UK
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#=============
# IMPORTS

import logging
import logging.handlers
import os
import sys
import time
import traceback

try:
    from Bio import SeqIO
except ImportError:
    print "Biopython required for script, but not found (exiting)"
    sys.exit(1)
from optparse import OptionParser

#=============
# FUNCTIONS

# Parse command-line
def parse_cmdline(args):
    """ Parse command-line arguments for the script
    """
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-o", "--outfile", dest="outfilename",
                      action="store", default=None,
                      help="Output directory")
    parser.add_option("-i", "--indir", dest="indirname",
                      action="store", default=None,
                      help="Input directory name")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", default=False,
                      help="Give verbose output")
    parser.add_option("-f", "--force", dest="force",
                      action="store_true", default=False,
                      help="Force file overwriting")
    parser.add_option("-l", "--logfile", dest="logfile",
                      action="store", default=None,
                      help="Logfile location")
    return parser.parse_args()

# Report last exception as string
def last_exception():
    """ Returns last exception as a string, for use in logging.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return ''.join(traceback.format_exception(exc_type, exc_value, 
                                              exc_traceback))

# Get list of FASTA files in a directory
def get_input_files(dir, *ext):
    """ Returns a list of files in the input directory with the passed 
        extension

        - dir is the location of the directory containing the input files
        
        - *ext is a list of arguments describing permissible file extensions
    """
    filelist = [f for f in os.listdir(dir) \
                    if os.path.splitext(f)[-1] in ext]
    return [os.path.join(dir, f) for f in filelist]

# Get the list of FASTA files from the input directory
def get_fasta_files():
    """ Return a list of FASTA files in the input directory
    """
    infiles = get_input_files(options.indirname,# '.fna')
                              '.fasta', '.fas', '.fa', '.fna')
    logger.info("Input files:\n\t%s" % '\n\t'.join(infiles))
    return infiles


# Write configuration information to the output file
def write_config_file(fasta_files):
    """
    """
    logger.info("Writing config file to %s" % options.outfilename)
    with open(options.outfilename, 'w') as fh:
        fh.write('\n'.join(['# find_differential_primers.py configuration file',
                            '# Automatically generated by build_config_file.py, %s' % time.asctime(),
                            '#', '# This file defines the following data, in tab-separated format:',
                            '# Column 1: Entity abbreviation',
                            '# Column 2: Family/group for the Entity, comma-separated for multiple groups',
                            '# Column 3: Location of sequence data in FASTA format',
                            '# Column 4: Location of GenBank file describing features (\'-\' if none)',
                            '# Column 5: Location of ePrimer3 primer definitions (\'-\' if none)',
                            '# Column 6: Location of PrimerSearch input format primer definitions (\'-\' if none)',
                            '#', '# BLANK COLUMNS ARE IGNORED! USE \'-\' IF THERE IS NO DATA.']) + '\n\n')
        for filename in fasta_files:
            fn = os.path.split(filename)[-1]
            fstem = os.path.splitext(fn)[0]
            fh.write('\t'.join([fstem, fstem, filename, '-', '-', '-']) + '\n')

#=============
# SCRIPT

if __name__ == '__main__':

    # Parse command-line
    # options are all options - no arguments
    options, args = parse_cmdline(sys.argv)

    # We set up logging, and modify loglevel according to whether we need
    # verbosity or not
    # err_handler points to sys.stderr
    # err_handler_file points to a logfile, if named
    logger = logging.getLogger('build_config_file.py')
    logger.setLevel(logging.DEBUG)
    err_handler = logging.StreamHandler(sys.stderr)
    err_formatter = \
                  logging.Formatter('%(levelname)s: %(message)s')
    err_handler.setFormatter(err_formatter)
    if options.logfile is not None:
        try:
            logstream = open(options.logfile, 'w')
            err_handler_file = logging.StreamHandler(logstream)
            err_handler_file.setFormatter(err_formatter)
            err_handler_file.setLevel(logging.INFO)
            logger.addHandler(err_handler_file)
        except:
            logger.error("Could not open %s for logging" %
                         options.logfile)
            sys.exit(1)
    if options.verbose:
        err_handler.setLevel(logging.INFO)
    else:
        err_handler.setLevel(logging.WARNING)
    logger.addHandler(err_handler)
    logger.info('# build_config_file.py logfile')
    logger.info('# Run: %s' % time.asctime())
 
    # Report arguments, if verbose
    logger.info(options)
    logger.info(args)

    # Have we got an input and output directory? If not, exit.
    if options.indirname is None:
        logger.error("No input directory name (exiting)")
        sys.exit(1)
    logger.info("Input directory: %s" % options.indirname)
    if options.outfilename is None:
        logger.error("No output filename (exiting)")
        sys.exit(1)

    # Process input file
    fasta_files = get_fasta_files()
    # Write output config file
    if os.path.isfile(options.outfilename):
        if options.force:
            logger.warning("-f option selected, removing %s" % options.outfilename)
            os.unlink(options.outfilename)
        else:
            logger.error("Output file %s exists (exiting)" % options.outfilename)
            sys.exit(1)
    write_config_file(fasta_files)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_subcmd_extract.py

Test extract subcommand for pdp.py script

This test suite is intended to be run from the repository root using:

nosetests -v

Individual test classes can be run using, e.g.:

$ nosetests -v tests/test_subcommands.py:TestConfigSubcommand

Each command CMD available at the command-line as pdp.py <CMD> is
tested in its own class (subclassing unittest.TestCase), where the
setUp() method defines input/output files, a null logger (picked up
by nosetests), and a dictionary of command lines, keyed by test name
with values that represent the command-line options.

For each test, command-line options are defined in a Namespace,
and passed as the sole argument to the appropriate subcommand
function from subcommands.py.

(c) The James Hutton Institute 2017
Author: Leighton Pritchard

Contact:
leighton.pritchard@hutton.ac.uk

Leighton Pritchard,
Information and Computing Sciences,
James Hutton Institute,
Errol Road,
Invergowrie,
Dundee,
DD6 9LH,
Scotland,
UK

The MIT License

Copyright (c) 2017 The James Hutton Institute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import logging
import os
import unittest

from argparse import Namespace

from diagnostic_primers.scripts import subcommands

from tools import assert_dirfiles_equal


class TestExtractSubcommand(unittest.TestCase):
    """Class defining tests of the pdp.py extract subcommand."""

    def setUp(self):
        """Set parameters for tests."""
        self.confdir = os.path.join("tests", "test_input", "config")
        self.indir = os.path.join("tests", "test_input", "extract")
        self.outdir = os.path.join("tests", "test_output", "extract")
        self.alignoutdir = os.path.join("tests", "test_output", "extract_mafft")
        self.targetdir = os.path.join("tests", "test_targets", "extract")
        self.aligntargetdir = os.path.join("tests", "test_targets", "extract_mafft")
        self.filestem = "Pectobacterium_primers"
        self.mafft_exe = "mafft"
        self.scheduler = "multiprocessing"
        self.workers = 4

        # null logger
        self.logger = logging.getLogger("TestExtractSubcommand logger")
        self.logger.addHandler(logging.NullHandler())

        # Command-line Namespaces
        self.argsdict = {
            "run": Namespace(
                infilename=os.path.join(self.confdir, "testclassify.json"),
                primerfile=os.path.join(self.indir, "%s.json" % self.filestem),
                outdir=self.outdir,
                verbose=False,
                ex_force=True,
                noalign=True,
                mafft_exe=self.mafft_exe,
                scheduler=self.scheduler,
                workers=self.workers,
                disable_tqdm=True,
            ),
            "align": Namespace(
                infilename=os.path.join(self.confdir, "testclassify.json"),
                primerfile=os.path.join(self.indir, "%s.json" % self.filestem),
                outdir=self.alignoutdir,
                verbose=False,
                ex_force=True,
                noalign=False,
                mafft_exe=self.mafft_exe,
                scheduler=self.scheduler,
                workers=self.workers,
                disable_tqdm=True,
            ),
        }

    def test_extract_run(self):
        """Extract command runs normally (no alignment)."""
        args = self.argsdict["run"]
        subcommands.subcmd_extract(args, self.logger)

        # Check output:
        self.logger.info("Comparing output amplicons to targets")
        # We have to infer the output location for the extracted amplicons.
        # This is defined by the filestem of the input JSON file
        outputdir = os.path.join(args.outdir, self.filestem)
        targetdir = os.path.join(self.targetdir, self.filestem)
        assert_dirfiles_equal(outputdir, targetdir)

    def test_extract_align(self):
        """Extract command runs normally (with MAFFT alignment)."""
        args = self.argsdict["align"]
        subcommands.subcmd_extract(args, self.logger)

        # Check output:
        self.logger.info("Comparing output amplicons to targets")
        # We have to infer the output location for the extracted amplicons.
        # This is defined by the filestem of the input JSON file
        outputdir = os.path.join(args.outdir, self.filestem)
        targetdir = os.path.join(self.aligntargetdir, self.filestem)
        assert_dirfiles_equal(outputdir, targetdir)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SunPy Gallery Generator
Keith Hughitt (khughitt@umd.edu)

References
----------
1. http://nbviewer.ipython.org/github/Carreau/posts/blob/master/06-NBconvert-Doc-Draft.ipynb
2. http://ipython.org/ipython-doc/rel-1.1.0/api/generated/IPython.nbconvert.exporters.export.html

"""
import os
import glob
import json
import sunpy
import IPython.nbconvert
from IPython.config import Config
from IPython.nbformat import current as nbformat
from IPython.nbconvert import HTMLExporter
from IPython.nbconvert import RSTExporter
from IPython.display import Image

def main():
    """Main"""
    # Each sub-directory corresponds to one section in the gallery
    dirs = [x for x in os.listdir() if os.path.isdir(x)]
    dirs.remove('resources')
    dirs.remove('.git')

    # We will construct a dictionary representation of the gallery
    gallery = {}

    gallery['meta'] = {
        'sunpy': sunpy.__version__
    }
    gallery['sections'] = {}

    # Process sections
    for directory in dirs:
        os.chdir(directory)

        # Section title
        #section_name = directory.replace("_", " ").title()
        section_name = directory
        gallery['sections'][section_name] = []

        print("=" * 40)
        print("Processing section: %s" % section_name)
        print("=" * 40)

        # Convert gallery entries
        for filepath in glob.glob('*.ipynb'):
            print("--> %s" % filepath)

            # Add entry to gallery dict
            basename = os.path.splitext(filepath)[0]
            gallery['sections'][section_name].append(basename)

            # Generate HTML and thumbnail image
            convert_notebook(filepath)
            extract_notebook_thumbnail(filepath)

    # Output gallery as JSON
    os.chdir('..')
    gallery_json = json.dumps(gallery)

    with open('gallery.json', 'w') as fp:
        fp.write(gallery_json)

def convert_notebook(filepath):
    """Convert a single notebook to HTML"""
    # Convert notebook to HTML
    html_exporter = HTMLExporter(config=Config({
        'HTMLExporter': {'default_template': 'full' #'basic'
    }}))

    (body, resources) = html_exporter.from_filename(filepath)

    # Write HTML
    fp = open(filepath.replace('ipynb', 'html'), 'w')
    fp.write(body)
    fp.close()

def extract_notebook_thumbnail(filepath):
    """
    Returns a thumbnail using the last image found in the specified
    notebook.

    For now, just returns the image at it's original size.
    """
    # RSTExporter saves images separately
    rst_exporter = RSTExporter()
    (body, resources) = rst_exporter.from_filename(filepath)

    # Find image entries
    extensions = ('png', 'jpg')
    images = [x for x in resources['outputs'].keys() if x.endswith(extensions)]

    # Save image
    key = images.pop()
    ext = key[-3:]
    image = Image(data=resources['outputs'][key], format=ext)

    # Write image to disk
    fp = open(filepath.replace('ipynb', ext), 'wb')
    fp.write(image.data)
    fp.close()

if __name__ == "__main__":
    main()

===================
Genetic Collections
===================


.. image:: https://img.shields.io/pypi/v/genetic_collections.svg
        :target: https://pypi.python.org/pypi/genetic_collections
        :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/MikeTrizna/genetic_collections.svg
        :target: https://travis-ci.org/MikeTrizna/genetic_collections
        :alt: Continuous integration status

.. image:: https://readthedocs.org/projects/genetic-collections/badge/?version=latest
        :target: http://genetic-collections.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation status

A Python library for connecting genetic records with specimen data.


Installation
------------

This software requires a working installation of Python 3.5 or higher. Your Python installation should come with a command-line tool called "pip", which is used to download packages from PyPI, the Python Package Index. Run the command below, and you should be good to go!

.. code-block:: python

	pip install genetic_collections


Command Line Usage
------------------

The installation from pip should also install several command line programs that act as wrappers for the code contained here.

Here are the available command line tools:

* ncbi_inst_search

.. code-block:: bash

   $ ncbi_inst_search "Smithsonian"
   
   6 matching results found.
    Fetching biocollection entries.
    [
      {
        "Collection Type": "museum",
        "gb_count": 20697,
        "Country": "USA",
        "Institution Code": "USNM",
        "NCBI Link": "https://www.ncbi.nlm.nih.gov/biocollections/53",
        "Institution Name": "National Museum of Natural History, Smithsonian Institution"
      },
      {
        "Collection Type": "herbarium",
        "gb_count": 5269,
        "Country": "USA",
        "Institution Code": "US",
        "NCBI Link": "https://www.ncbi.nlm.nih.gov/biocollections/7399",
        "Institution Name": "Smithsonian Institution, Department of Botany"
      },
      ...
      
* gb_search

.. code-block:: bash

   $ gb_search -inst_code USNM
   
   Your search found 20697 hits in GenBank
   You can see you search results online at 
   https://www.ncbi.nlm.nih.gov/nuccore/?term=%22collection+USNM%22%5Bprop%5D
   
* gb_fetch
* bold_inst_search
* bold_search
* bold_fetch

Python Library Usage
--------------------

The best way to illustrate how the Python library can be used is to view the example workflow in the Jupyter notebook in the "examples" directory.

How to contribute
-----------------

Imposter syndrome disclaimer: I want your help. No really, I do.

There might be a little voice inside that tells you you're not ready; that you need to do one more tutorial, or learn another framework, or write a few more blog posts before you can help me with this project.

I assure you, that's not the case.

This project has some clear Contribution Guidelines and expectations that you can read here (link).

The contribution guidelines outline the process that you'll need to follow to get a patch merged. By making expectations and process explicit, I hope it will make it easier for you to contribute.

And you don't just have to write code. You can help out by writing documentation, tests, or even by giving feedback about this work. (And yes, that includes giving feedback about the contribution guidelines.)

Thank you for contributing!

Next Steps
----------

* Incorporate MIXS standards
* Add the ability to translate GenBank and BOLD results to DwC format in order to compare
* Add iDigBio and GBIF APIs as data sources for specimen data (and GenBank accessions)

Credits
-------

"How to contribute" was taken from https://github.com/adriennefriend/imposter-syndrome-disclaimer.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys


sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('./demo/'))

from sphinx.locale import _

__version__ = "1.0.0"

project = "LC-MS User Guide"
slug = re.sub(r'\W+', '-', project.lower())
version = __version__
release = __version__
author = u'Dominic Davis-Foster'
copyright = author
language = 'en'

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinxcontrib.httpdomain',
]

templates_path = ['_templates']
source_suffix = '.rst'
exclude_patterns = []

master_doc = 'index'
suppress_warnings = ['image.nonlocal_uri']
pygments_style = 'default'

intersphinx_mapping = { # Is this where those mystery links are specified?
    'rtd': ('https://docs.readthedocs.io/en/latest/', None),
    'sphinx': ('http://www.sphinx-doc.org/en/stable/', None),
}

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,  # True will show just the logo
}
html_theme_path = ["../.."]
html_logo = ""
html_show_sourcelink = False    # True will show link to source

html_context = {
    # Github Settings
    "display_github": True, # Integrate GitHub
    "github_user": "domdfcoding", # Username
    "github_repo": "GunShotMatch", # Repo name
    "github_version": "master", # Version
    "conf_py_path": "/", # Path in the checkout to the docs root
}

htmlhelp_basename = slug

latex_documents = [
  ('index', '{0}.tex'.format(slug), project, author, 'manual'),
]

man_pages = [
    ('index', slug, project, [author], 1)
]

texinfo_documents = [
  ('index', slug, project, author, slug, project, 'Miscellaneous'),
]


# Extensions to theme docs
def setup(app):
    from sphinx.domains.python import PyField
    from sphinx.util.docfields import Field

    app.add_object_type(
        'confval',
        'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            PyField(
                'type',
                label=_('Type'),
                has_arg=False,
                names=('type',),
                bodyrolename='class'
            ),
            Field(
                'default',
                label=_('Default'),
                has_arg=False,
                names=('default',),
            ),
        ]
    )

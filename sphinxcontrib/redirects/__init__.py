"""
    sphinxcontrib.redirects
    ~~~~~~~~~~~~~~~~~~~~~~~

    Generate redirects for moved pages when using the HTML builder.

    See the README file for details.

    :copyright: Copyright 2017 by Stephen Finucane <stephen@that.guru>
    :license: BSD, see LICENSE for details.
"""

import os

from sphinx.builders import html as builders
from sphinx.locale import __
from sphinx.util import status_iterator

TEMPLATE = """<html>
  <head><meta http-equiv="refresh" content="0; url={to_path}"/></head>
  <body>
  This page has moved. Redirecting...
  <script>
  window.location.href = '{to_path}' + (window.location.search || '') + (window.location.hash || '');
  </script>
  </body>
</html>
"""


def generate_redirects(app):

    path = os.path.join(app.srcdir, app.config.redirects_file)
    if not os.path.exists(path):
        app.info("Could not find redirects file at '%s'" % path)
        return


    if isinstance(app.config.source_suffix, list):
        in_suffix = app.config.source_suffix[0]
    elif isinstance(app.config.source_suffix, dict):
        in_suffix = list(app.config.source_suffix.keys())[0]
    else:
        app.warn("The source suffix can not be resolved. Skipping redirects...")
        return

    # TODO(stephenfin): Add support for DirectoryHTMLBuilder
    if not type(app.builder) == builders.StandaloneHTMLBuilder:
        app.warn("The 'sphinxcontib-redirects' plugin is only supported "
                 "by the 'html' builder. Skipping...")
        return

    with open(path) as redirects_file:
        redirects = dict([line.rstrip().split(' ') for line in redirects_file.readlines()])

    for from_path in status_iterator(redirects.keys(), __('creating redirects'), 'blue', len(redirects),
                                     app.verbosity):
        to_path = redirects[from_path]
        from_path = '{}{}'.format(from_path[:len(in_suffix) * -1], '.html')
        to_path_prefix = '..%s' % os.path.sep * (
            len(from_path.split(os.path.sep)) - 1)
        to_path = to_path_prefix + to_path.replace(in_suffix, '.html')

        redirected_filename = os.path.join(app.builder.outdir, from_path)
        redirected_directory = os.path.dirname(redirected_filename)
        if not os.path.exists(redirected_directory):
            os.makedirs(redirected_directory)

        with open(redirected_filename, 'w') as f:
            f.write(TEMPLATE.format(to_path=to_path))


def setup(app):
    app.add_config_value('redirects_file', 'redirects', 'env')
    app.connect('builder-inited', generate_redirects)

"""
For testing with Firefox at command line. Example:
    python -m chartio {email} {password} {dashboard_url} "Filter Value 1,Filter Value 2"

Uses FireFox and will write PDF to `chartio_test.pdf`

Useful for debugging interactively:
  from IPython.core.debugger import Tracer
  Tracer()() # to break into ipdb
"""

import sys
from chartio import ChartioDashboardRetriever
username, password, dashboard_url, filter_values_str = sys.argv[1:5]
filter_values = filter_values_str.split(',')
chartio = ChartioDashboardRetriever(username, password, debug=True)
chartio.get_pdf_for_dashboard(dashboard_url, filter_values)
chartio.close()

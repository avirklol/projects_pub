# IMPORTS
import taipy as tp
from taipy.gui import Html as HTML
import numpy as np

# APP INSTANTIATION


root_html = "<p>Multi-page application</p>"
page1_html = "<h2>This is page 1</h2>"
page2_html = "<h2>This is page 2</h2>"

pages = {
    "/": HTML(root_html),
    "page1": HTML(page1_html),
    "page2": HTML(page2_html)
}

tp.Gui(pages=pages, css_file='intelligent_debtor/styles.css').run()

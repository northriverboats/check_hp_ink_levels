#!/usr/bin/env python3
"""Checks the ink level in an HP Designjet Z5200 and emails admin if low

Usage:


License:
    BSD Clause 3 License

    Copyright (c) 2022, Fredrick W. Warren
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
from urllib.request import urlopen
import click
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def query_plotter():
    """Read plotter status page"""
    url = os.getenv('URL')
    with urlopen(url) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")

    # find the correct table
    table = soup.find('caption', text = 'Cartridges').find_parent('table')
    headers = ['letter', 'cartridge', 'status', 'level', 'capacity',
               'warranty', 'part']

    # build list of dictionary rows
    table_data = []
    for row in table.findAll("tr")[1:]:
        t_row = {}
        for t_d, t_h in zip(row.find_all("td"), headers):
            t_row[t_h] = t_d.text.replace('\n', '').strip()
        table_data.append(t_row)

    # compute cartridges that are low on ink
    return [row for row in table_data if row['level'][:-2] < '11']


# pylint: disable=no-value-for-parameter
@click.command()
@click.option('--debug', '-d', is_flag=True,
    help='show debug output do not email')
def main(debug):
    """check ink levels and email results"""
    if debug:
        print('boo')
    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))
    print(query_plotter())

if __name__ == "__main__":
    main()

# vim: ts=2 sw=2 et

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
from emailer import Email

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """

    try:
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def mail_results(subject, body):
    """send actual emails"""
    m_from = os.getenv('MAIL_FROM')
    m_to = os.getenv('MAIL_TO')
    mail = Email(os.getenv('MAIL_SERVER'))
    mail.setFrom(m_from)
    for email in m_to.split(','):
        mail.addRecipient(email)
    # mail.addCC(os.getenv('MAIL_FROM'))

    mail.setSubject(subject)
    mail.setTextBody("You should not see this text in a MIME aware reader")
    mail.setHtmlBody(body)
    mail.send()

def email_admins(low, status):
    """eamil admins about cartridge status"""
    subject = "Need to reorder ink for plotter"
    body = f"""
        <p>Time to order some more of the following inkjet ink</p>
        <pre>{low}</pre>
        <br />
        <p>These are the overall cartridge levels</p>
        <pre>{status}</pre>
    """
    mail_results(subject, body)

def email_status(low, status):  # pylint: disable=unused-argument
    """eamil admins about cartridge status"""
    subject = "HP Z5200 Plotter Ink Cartridge Status Report"
    body = f"""
        <p>These are the overall cartridge levels</p>
        <pre>{status}</pre>
				<p>For more details please click <a href="http://10.10.200.130/">here</a>.</p>
    """
    mail_results(subject, body)



def format_list(cartridges):
    """format cartridge list"""

    text  = ""
    for row in cartridges:
        line = (f"    {row['cartridge']:20}  "
                f"{'(' + row['letter'] + ')':4}  "
                f"{row['part']}  "
                f"{row['level']:>5}  "
                f"{row['status']}\n")
        text += line
    return text


def query_plotter():
    """Read plotter status page"""

    url = os.getenv('URL')
    threshold = os.getenv('THRESHOLD')
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

    # cartridges status
    status = format_list(table_data)

    # compute cartridges that are low on ink
    low = format_list(
        [row for row in table_data if row['level'][:-2] <= threshold ])
    return low, status


# pylint: disable=no-value-for-parameter
@click.command()
@click.option('--debug', '-d', is_flag=True,
    help='show debug output do not email')
@click.option('--status', '-s', is_flag=True,
    help='just print/show status')
def main(debug, status):
    """check ink levels and email results"""

    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))
    low, status_levels = query_plotter()
    if debug:
        print("Cartridge Status")
        print(status_levels)
        return
    if status:
        email_status(low, status_levels)
        return
    if low:
        email_admins(low, status_levels)


if __name__ == "__main__":
    main()

# vim: ts=4 sw=4 et

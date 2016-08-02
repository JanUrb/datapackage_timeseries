__author__ = 'Jan'
"""
To download the xls for Denmark, just call the download_xls_file() in the notebook.

TODO: Sometimes the server returns a malformed table! Investigate if the code/request is wrong or the server code
    is not done properly.
"""
import requests
from bs4 import BeautifulSoup
import datetime
import os
import logging

log = logging.getLogger('download_denmark')
log.setLevel(logging.INFO)

_TARGET_URL = r'http://www.energinet.dk/en/el/engrosmarked/udtraek-af-markedsdata/Sider/default.aspx?language=en'
_REQUEST_URL = r'http://www.energinet.dk/_layouts/Markedsdata/Framework/Integrations/MarkedsdataExcelOutput.aspx'
_POST_PARAMETER_FILE = 'post_parameter.txt'


def _extract_dotNet_variables():
    log.debug('Extracting dotNet variables')
    s = requests.Session()
    r = s.get(_TARGET_URL)
    if r.status_code != 200:
        raise requests.ConnectionError

    soup = BeautifulSoup(r.content, 'lxml')
    # extract viewstate
    view_state = soup.select('#__VIEWSTATE')[0]['value']
    # extract evenvalidation
    event_validation = soup.select('#__EVENTVALIDATION')[0]['value']
    return view_state, event_validation, s


def _construct_parameter(view_state, event_validation, file_path):
    log.debug('Constructing post parameter')
    parameter = {}
    with open(file_path, 'r') as para_file:
        lines = para_file.read().splitlines()
        # last element is endDate. It has to be changed to current date
        current_time = datetime.datetime.now()
        current_date = current_time.strftime("%d-%m-%Y")
        lines[-1] = 'endDate=' + current_date
        # split lines into dictionary
        for key_value in lines:
            try:
                key, value = key_value.split('=')
                parameter[key] = value
            except:
                log.warning('Error: ' + key_value)

        # add view_state and event_validation
        parameter['__VIEWSTATE'] = view_state
        parameter['__EVENTVALIDATION'] = event_validation
        log.debug(parameter['startDate'])
        log.debug(parameter['endDate'])

        return parameter


def _download_excel(parameter, session, output_path):
    """
    This function downloads the xls file from the website. To download, you have to send a post request with parameters
    that specify the data you want first. After that you request the xls/html file.

    Parameters
    ----------
    parameter : Specifies the data (ASP.NET Web Form)
    session : The session that was used for extracting the variables
    output_path : Defines the location for the downloaded xls file

    Returns
    -------

    """
    log.info('Downloading xls file.')
    header = {
        'referer': r'http://www.energinet.dk/_layouts/Markedsdata/framework/integrations/markedsdatatemplate.aspx?language=en',
        'content-type': 'application/vnd.ms-excel; charset=utf-8',
        'accept-language': 'de,en-US;q=0.7,en;q=0.3',
        'accept-encoding': 'gzip, deflate',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'connection': 'keep-alive'
    }
    # Specifies the data you want.
    p = session.post(_REQUEST_URL, data=parameter, headers=header)

    log.debug('post header: ' + str(p.headers))

    # Gets the data you want.
    r = session.get(_REQUEST_URL, stream=True, headers=header)
    log.debug('header: ' + str(r.headers))
    with open(output_path, 'wb') as out_file:
        for chunk in r.iter_content(chunk_size=1024):
            out_file.write(chunk)

    log.info('Download completed')


def download_xls_file(output_directory='', output_file_name='danish.xls'):
    """
    Prepares the parameters and downloads the xls file.
    Parameters
    ----------
    output_directory : Directory where the xls file is saved.
    output_file_name : Name of the downloaded file.

    Returns
    -------

    """
    loc = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    para_path = os.path.join(loc, _POST_PARAMETER_FILE)
    output_path = os.path.join(output_directory, output_file_name)
    view, event, session = _extract_dotNet_variables()
    parameter_dict = _construct_parameter(view, event, para_path)
    _download_excel(parameter_dict, session, output_path)


if __name__ == '__main__':
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    download_xls_file()

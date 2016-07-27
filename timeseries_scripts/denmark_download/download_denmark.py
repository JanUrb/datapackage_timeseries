import requests
from bs4 import BeautifulSoup
import datetime
import os

# import logging
# TODO: Comments, make it callable from a notebook.
_TARGET_URL = r'http://www.energinet.dk/en/el/engrosmarked/udtraek-af-markedsdata/Sider/default.aspx'
_REQUEST_URL = r'http://www.energinet.dk/_layouts/Markedsdata/Framework/Integrations/MarkedsdataExcelOutput.aspx'
_FILE_NAME = 'danish.xls'

def _extract_dotNet_variables():
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
    parameter = {}
    with open(file_path, 'r') as para_file:
        lines = para_file.read().splitlines()
        # 2nd last element is endDate. It has to be changed to current date
        current_time = datetime.datetime.now()
        current_date = current_time.strftime("%d-%m-%Y")
        print(current_date)
        lines[-2] = 'endDate='+current_date
        # split lines into dictionary
        for key_value in lines:
            try:
                key, value = key_value.split('=')
                parameter[key] = value
            except:
                print('Error: ' + key_value)


        # add view_state and event_validation
        parameter['__VIEWSTATE'] = view_state
        parameter['__EVENTVALIDATION'] =  event_validation

        return parameter


def _download_excel(parameter, session, output_path):
    post = session.post(_REQUEST_URL, data = parameter)
    print(post.status_code)
    # get excel
    r = session.get(_REQUEST_URL, stream=True)
    print()
    with open(output_path, 'wb') as out_file:
        for chunck in r.iter_content(chunk_size=1024):
            out_file.write(chunck)






if __name__ == '__main__':
    # get file path
    loc = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    para_path = os.path.join(loc, 'post_parameter.txt')
    output_path = os.path.join(loc, _FILE_NAME)
    print(output_path)

    view, event, session = _extract_dotNet_variables()
    parameter_dict = _construct_parameter(view, event, para_path)
    _download_excel(parameter_dict, session, output_path)

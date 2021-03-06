"""
 Google (Images)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   no
 @results     HTML chunks with JSON inside
 @stable      no
 @parse       url, title, img_src
"""

from datetime import date, timedelta
from json import loads
from lxml import html
from searx.url_utils import urlencode

# engine dependent config
categories = ['images']
paging = True
safesearch = True
time_range_support = True
number_of_results = 100

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=isch'\
    '&yv=2'\
    '&{search_options}'
time_range_attr = "qdr:{range}"
time_range_custom_attr = "cdr:1,cd_min:{start},cd_max{end}"
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}


# do search-request
def request(query, params):
    search_options = {
        'ijn': params['pageno'] - 1,
        'start': (params['pageno'] - 1) * number_of_results
    }

    if params['time_range'] in time_range_dict:
        search_options['tbs'] = time_range_attr.format(range=time_range_dict[params['time_range']])
    elif params['time_range'] == 'year':
        now = date.today()
        then = now - timedelta(days=365)
        start = then.strftime('%m/%d/%Y')
        end = now.strftime('%m/%d/%Y')
        search_options['tbs'] = time_range_custom_attr.format(start=start, end=end)

    if safesearch and params['safesearch']:
        search_options['safe'] = 'on'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      search_options=urlencode(search_options))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[contains(@class, "rg_meta")]/text()'):

        try:
            metadata = loads(result)

            img_format = metadata.get('ity', '')
            img_width = metadata.get('ow', '')
            img_height = metadata.get('oh', '')
            if img_width and img_height:
                img_format += " {0}x{1}".format(img_width, img_height)

            source = metadata.get('st', '')
            source_url = metadata.get('isu', '')
            if source_url:
                source += " ({0})".format(source_url)

            results.append({'url': metadata['ru'],
                            'title': metadata['pt'],
                            'content': metadata.get('s', ''),
                            'source': source,
                            'img_format': img_format,
                            'thumbnail_src': metadata['tu'],
                            'img_src': metadata['ou'],
                            'template': 'images.html'})

        except:
            continue

    return results

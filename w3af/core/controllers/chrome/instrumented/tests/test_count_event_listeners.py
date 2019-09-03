"""
test_count_event_listeners.py

Copyright 2019 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from __future__ import print_function

import os
import Queue
import unittest

from collections import OrderedDict
from nose.plugins.attrib import attr

from w3af.core.controllers.chrome.devtools.exceptions import ChromeInterfaceException
from w3af.core.controllers.chrome.instrumented.main import InstrumentedChrome
from w3af.core.controllers.chrome.tests.helpers import set_debugging_in_output_manager
from w3af.core.data.url.extended_urllib import ExtendedUrllib


@attr('internet')
class TestChromeCrawlerGetEventListeners(unittest.TestCase):
    """
    This test is the result of a small research I made to understand how many
    event listeners are present on "common" pages.

    Note that this test depends on external sites which we don't control in any
    way. The test might start failing after a change in those sites.

    Note that the test is tagged as 'internet' (see @attr) to be able to disable
    if necessary.
    """

    TESTS = OrderedDict([
        ('https://facebook.com/', 50),
    ])

    """
    There are some failing tests, Ctrl+F for "FAILS":    
    
        ('https://google.com/', 20),
        ('https://www.google.com/search?q=w3af', 7),

        ('https://www.bing.com/', 80),
        ('https://www.bing.com/search?q=w3af', 100),

        ('https://facebook.com/', 50),
        ('https://www.facebook.com/', 50),
        ('https://www.facebook.com/local/lists/350492278720904/', 5),

        ('https://cnn.com/', 55),
        ('https://edition.cnn.com/2019/03/27/uk/theresa-may-is-throwing-the-kitchen-sink-at-brexit-intl-gbr/index.html', 170),

        ('https://www.bbc.com/', 200),
        ('https://www.bbc.com/news/uk-politics-47729773', 300),

        ('https://www.wikipedia.org/', 10),
        ('https://en.wikipedia.org/wiki/Cross-site_scripting', 0),

        ('http://w3af.org/', 20),
        ('http://w3af.org/take-a-tour', 24),

        ('https://github.com/', 40),
        ('https://github.com/andresriancho/w3af', 46),

        ('https://web.whatsapp.com/', 0), # FAILS: websocket?
        
        ('https://andresriancho.com/', 400),
        ('https://andresriancho.com/internet-scale-analysis-of-aws-cognito-security/', 400),
        
        ('https://Youtube.com/', 400),
        ('https://www.youtube.com/watch?v=otvvUzFh5Do', 400),
                
        ('https://qq.com/', 400),
        ('https://new.qq.com/rain/a/20190902A0C87G00', 400),
        
        ('https://360.cn/', 400),
        ('http://ku.u.360.cn/online.php?s=gw_web', 400),
        
        ('https://netflix.com/', 400),
        ('https://www.netflix.com/ar-en/title/80057281', 400),
        
        ('https://instagram.com/', 400),
        ('https://www.instagram.com/leomessi/', 400),
        ('https://www.instagram.com/p/Bz3BsLSim4x/', 400),
        
        ('https://twitter.com/', 400),
        ('https://twitter.com/AndresRiancho', 400),
        ('https://twitter.com/AndresRiancho/status/1115224660600393728', 400),
        
        ('https://stackoverflow.com/', 400),
        ('https://stackoverflow.com/questions/20484920/terminate-a-hung-redis-pubsub-listen-thread', 400),
    """

    def setUp(self):
        uri_opener = ExtendedUrllib()
        http_traffic_queue = Queue.Queue()

        self.ic = InstrumentedChrome(uri_opener, http_traffic_queue)

    def tearDown(self):
        self.ic.terminate()

    def _load_url(self, url):
        self.ic.load_url(url)

        loaded = self.ic.wait_for_load()
        if not loaded:
            self.ic.stop()

    def _print_all_console_messages(self, ic):
        for console_message in ic.get_console_messages():
            print(console_message)

    def _print_summary(self, url, all_event_listeners):
        event_types = dict()

        for el in all_event_listeners:
            event_type = el['event_type']
            if event_type in event_types:
                event_types[event_type] += 1
            else:
                event_types[event_type] = 1

        # print(url)
        # pprint.pprint(event_types)
        # print()

    def _count_event_listeners(self, url, min_event_count):
        self._load_url(url)

        try:
            all_event_listeners = [el for el in self.ic.get_all_event_listeners()]
        except ChromeInterfaceException:
            all_event_listeners = []

        self._print_summary(url, all_event_listeners)

        all_el_str = '\n'.join(' - %s' % i for i in all_event_listeners)

        msg = ('%s has %s event listeners and should have at least %s.'
               ' The complete list of identified event listeners is:\n%s')
        args = (url, len(all_event_listeners), min_event_count, all_el_str)

        # self._print_all_console_messages(ic)

        self.assertGreaterEqual(len(all_event_listeners),
                                min_event_count,
                                msg % args)

        # self.assertEqual(ic.get_js_errors(), [])

    @unittest.skip('Manual testing')
    def test_count_event_listeners(self):
        if int(os.getenv('CHROME_DEBUG', 0)) == 1:
            set_debugging_in_output_manager()

        for url, min_event_count in self.TESTS.iteritems():
            self._count_event_listeners(url, min_event_count)
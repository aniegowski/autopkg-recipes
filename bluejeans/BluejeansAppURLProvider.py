#!/usr/bin/python

import json
import os
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["BluejeansAppURLProvider"]

FEED_URL = 'https://swdl.bluejeans.com/desktop-app/mac/ga.manifest.json'
FEED_URL_KEY = 'pkg_installer_url'

class BluejeansAppURLProvider(Processor):
    description = __doc__
    input_variables = {
        "feed_url": {
            "required": False,
            "description": "Default is '%s." % FEED_URL,
        },
        "feed_url_key": {
            "required": False,
            "description": "Default is '%s." % FEED_URL_KEY,
        },
    }
    output_variables = {
        "filename": {
            "description": "Filename portion of the URL.",
        },
        "url": {
            "description": "URL to the latest Bluejeans app package.",
        },
        "version": {
            "description": "version of the pkg, as claimed by the feed"
        },
    }

    def get_feed_from_url(self, feed_url):
        try:
            url_handle = urllib2.urlopen(feed_url)
            response = url_handle.read()
            url_handle.close()
        except BaseException as err:
            raise ProcessorError(
                'Can\'t read response from URL %s: %s' % (feed_url, err))
        try:
            response_dict = json.loads(response)
            return response_dict
        except ValueError as err:
            raise ProcessorError(
                'Could not parse json from URL %s: %s' % (feed_url, err))

    def main(self):
        feed_url = self.env.get('feed_url', FEED_URL)
        feed_url_key = self.env.get('feed_url_key', FEED_URL_KEY)
        feed = self.get_feed_from_url(feed_url)
        try:
            self.env['url'] = feed[feed_url_key]
            self.output('Found URL %s' % self.env['url'])
        except AttributeError:
            raise ProcessorError(
                'Missing installer_download_url from feed at URL %s' % feed_url)
        self.env['filename'] = os.path.split(self.env['url'])[-1]
        self.output('Filename: %s' % self.env['filename'])
        try:
            self.env['version'] = feed['version']
            self.output('Found version number %s' % self.env['version'])
        except AttributeError:
            raise ProcessorError(
                'Missing version from feed at URL %s' % feed_url)

if __name__ == "__main__":
    PROCESSOR = BluejeansAppURLProvider()
    PROCESSOR.execute_shell()

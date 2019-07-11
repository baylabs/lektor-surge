# -*- coding: utf-8 -*-
import os
import shutil

from lektor.pluginsystem import Plugin
from lektor.publisher import Command, Publisher, _temporary_folder


class SurgePublisher(Publisher):

    def link_artifacts(self, path):
        try:
            link = os.link
        except AttributeError:
            link = shutil.copy

        # Clean old
        for filename in os.listdir(path):
            if filename == '.git':
                continue
            filename = os.path.join(path, filename)
            try:
                os.remove(filename)
            except OSError:
                shutil.rmtree(filename)

        # Add new
        for dirpath, dirnames, filenames in os.walk(self.output_path):
            dirnames[:] = [x for x in dirnames if x != '.lektor']
            for filename in filenames:
                full_path = os.path.join(self.output_path, dirpath, filename)
                dst = os.path.join(path, full_path[len(self.output_path):]
                                   .lstrip(os.path.sep)
                                   .lstrip(os.path.altsep or ''))
                try:
                    os.makedirs(os.path.dirname(dst))
                except (OSError, IOError):
                    pass
                link(full_path, dst)

    def write_auth(self, path, target_url):
        params = target_url.decode_query()
        auth = params.get('auth')
        if auth is not None:
            with open(os.path.join(path, 'AUTH'), 'w') as f:
                f.write('%s\n' % auth.encode('utf-8'))

    def write_cname(self, path, target_url):
        with open(os.path.join(path, 'CNAME'), 'w') as f:
            f.write('%s\n' % target_url.host.encode('utf-8'))

    def publish(self, target_url, credentials=None, **extra):
        if target_url.scheme == 'surge+https':
            url = 'https://' + target_url.host
        else:
            url = target_url.host

        self.write_cname(self.output_path, target_url)
        self.write_auth(self.output_path, target_url)

        for line in Command(['surge', self.output_path, url]):
            yield line


class SurgePlugin(Plugin):
    name = u'Surge'
    description = u'Lektor plugin to publish your site to surge.sh'

    def on_setup_env(self, **extra):
        for scheme in ('surge', 'surge+https'):
            try:
                # Lektor 2.0+.
                self.env.add_publisher(scheme, SurgePublisher)
            except AttributeError:
                # Lektor 1.0.
                from lektor.publisher import publishers
                publishers[scheme] = SurgePublisher

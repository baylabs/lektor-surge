# -*- coding: utf-8 -*-
import subprocess

from lektor.pluginsystem import Plugin
from lektor.publisher import Publisher


class SurgePublisher(Publisher):
    def publish(self, target_url, credentials=None, **extra):
        url = target_url.path
        yield "Publishing to Surge..."
        subprocess.check_call(['surge', '-p', self.output_path, url])


class SurgePlugin(Plugin):
    name = u'surge'
    description = u'Publishes your lektor site with surge.sh.'

    def on_setup_env(self, **extra):
        self.env.add_publisher('surge', SurgePublisher)

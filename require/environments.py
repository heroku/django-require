from __future__ import unicode_literals

from distutils.spawn import find_executable

from django.utils.functional import cached_property

from require.conf import settings as require_settings
from require.helpers import import_module_attr


def load_environment():
    environment = require_settings.REQUIRE_ENVIRONMENT
    aliases = require_settings.REQUIRE_ENVIRONMENT_ALIASES
    environment = aliases.get(environment, environment)
    environment = import_module_attr(environment)
    return environment


class Environment(object):
    def __init__(self, environment):
        self.env = environment

    def args(self):
        raise NotImplementedError()


class NodeEnvironment(Environment):
    def args(self):
        # Start of the command to run the compiler in Node.
        return ["node"] if require_settings.REQUIRE_DEBUG else ["/app/vendor/node/bin/node"]


class RhinoEnvironment(Environment):
    def args(self):
        # Start of the command to run the compiler in Java.
        return [
            "java",
            "-classpath",
            ":".join((
                self.env.resource_path("js.jar"),
                self.env.resource_path("compiler.jar"),
            )),
            "org.mozilla.javascript.tools.shell.Main"
        ]


class AutoEnvironment(Environment):
    environments = [NodeEnvironment, RhinoEnvironment]

    @cached_property
    def environment(self):
        for environment in self.environments:
            environment = environment(self.env)
            executable = environment.args()[0]
            if find_executable(executable):
                print "Auto environment using {0} for require.js optimization".format(environment.__class__.__name__)
                return environment

        raise EnvironmentError("no environments detected: {envs}".format(
            envs=', '.join([ str(env) for env in self.environments ])))

    def args(self):
        return self.environment.args()

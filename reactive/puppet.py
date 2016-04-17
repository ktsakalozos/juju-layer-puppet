from charms.reactive import (
    set_state,
    remove_state,
    when_not,
    when,
)
from charmhelpers.core import hookenv, unitdata
from charms import apt
import platform
import subprocess


@when_not('apt.installed.puppet')
def install_puppet():
    """Install Puppet packages.

    If the user has configured repos, use them. If not (and we're on trusty),
    use the puppetlabs repo to avoid buggy archive packages. If neither of
    these, install packages using the default system repos.
    """
    config = hookenv.config()
    kv = unitdata.kv()
    distribution = platform.linux_distribution()  # looks like [ubuntu, 12.04, precise]

    if config.get('install_sources'):
        kv.set('puppet.url', config.get('install_sources'))
        kv.set('puppet.key', config.get('install_keys'))
        apt.update()
    elif distribution[2] == 'trusty':
        # BIGTOP-2003. A workaround to install newer hiera to get rid of hiera 1.3.0 bug.
        # TODO once Ubuntu trusty fixes version of hiera package, this could be replaced by
        # adding packages: ['puppet'] in layer.yaml options:basic
        wget = 'wget -O /tmp/puppetlabs-release-trusty.deb https://apt.puppetlabs.com/puppetlabs-release-trusty.deb'
        dpkg = 'dpkg -i /tmp/puppetlabs-release-trusty.deb'
        try:
            subprocess.check_call(wget.split())
            subprocess.check_call(dpkg.split())
        except subprocess.CalledProcessError as e:
            hookenv.status_set('blocked',
                               'failed to install puppetlabs repo: %s' % e.output)
            return False
        else:
            apt.update()

    apt.queue_install(['puppet'])
    apt.install_queued()


@when('apt.installed.puppet')
@when_not('puppet.available')
def puppet_ready():
    """
    Set status so users know puppet is ready. Set the 'puppet.available' state
    so other layers can gate puppet operations.
    """
    hookenv.status_set('active', 'puppet is installed')
    set_state('puppet.available')


@when('puppet.available', 'config.changed')
def version_check():
    """
    If config changed since the previous install, purge the package and remove
    'puppet.available'. The install_puppet() will run again with the new config.
    """
    config = hookenv.config()
    kv = unitdata.kv()

    # kv.get returns None for empty config; set empty config to None to match
    url = config.get('install_sources') or None
    key = config.get('install_keys') or None

    if url != kv.get('puppet.url') or key != kv.get('puppet.key'):
        apt.purge(['puppet'])
        remove_state('puppet.available')

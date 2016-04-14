from charms.reactive import (
    hook,
    set_state,
    remove_state,
    main,
    when_not,
    when,
)

from charmhelpers.core import (
    hookenv,
    unitdata,
)

from charms import apt
import subprocess
from subprocess import CalledProcessError


config = hookenv.config()
kv = unitdata.kv()


@when_not('puppet.available')
def install_puppet():
    """ Installs latest Puppet & hiera packages

    Emits:
    puppet.available: Emitted once the runtime has been installed
    """

    # install required puppet modules
    # BIGTOP-2003. A workaround to install newer hiera to get rid of hiera 1.3.0 bug.
    # TODO once Ubuntu trusty fixes version of hiera package, this could be replaced by
    # adding packages: ['puppet'] in layer.yaml options:basic
    try:
        # Ideally the sources should be taken from config.yaml but I can not make it work
        wget = 'wget -O /tmp/puppetlabs-release-trusty.deb https://apt.puppetlabs.com/puppetlabs-release-trusty.deb'
        dpkg = 'dpkg -i /tmp/puppetlabs-release-trusty.deb'
        apt_update = 'apt-get update'
        puppet_install = 'apt-get install --yes puppet'
        subprocess.call(wget.split())
        subprocess.call(dpkg.split())
    except CalledProcessError:
        pass  # All modules are set

    kv.set('puppet.url', config.get('install_sources'))
    kv.set('puppet.key', config.get('install_keys'))

    apt.queue_install(['puppet'])


@when('apt.installed.puppet')
@when_not('puppet.available')
def puppet_id_set():
    hookenv.status_set('active', 'Puppet is installed')
    set_state('puppet.available')


@hook('config-changed')
def version_check():
    url = config.get('install_sources')
    key = config.get('install_keys')

    if url != kv.get('puppet.url') or key != kv.get('puppet.key'):
        apt.purge(['puppet'])
        remove_state('puppet.available')


if __name__ == "__main__":
    main()

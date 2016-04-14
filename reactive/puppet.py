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


config = hookenv.config()
kv = unitdata.kv()


@when_not('puppet.available')
def install_puppet():
    """ Installs latest Puppet & hiera packages

    Emits:
    puppet.available: Emitted once the runtime has been installed
    """
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

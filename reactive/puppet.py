from charms.reactive import (
    set_state,
    remove_state,
    is_state,
    when_not,
    when,
    when_any,
)
from charms import apt
import platform


@when_not('apt.installed.puppet')
def install_puppet():
    """Install Puppet packages.

    If the user has configured repos, use them. If not (and we're on trusty),
    use the puppetlabs repo to avoid buggy archive packages. If neither of
    these, install packages using the default system repos.
    """
    distname, version, series = platform.linux_distribution()

    if series == 'trusty' and is_state('config.default.install_sources'):
        # BIGTOP-2003. A workaround to install newer hiera to get rid of
        # hiera 1.3.0 bug.
        apt.add_source('deb http://apt.puppetlabs.com trusty main dependencies',
                       '4BD6EC30')

        apt.update()

    apt.queue_install(['puppet'])
    apt.install_queued()


@when('apt.installed.puppet')
@when_not('puppet.available')
def puppet_ready():
    """
    Set the `puppet.available` state so other layers can gate
    puppet operations.
    """
    set_state('puppet.available')


@when('puppet.available')
@when_any('config.changed.install_sources', 'config.changed.install_keys')
def version_check():
    """
    If config changed since the previous install, purge the package and
    remove `puppet.available`.  Then `install_puppet()` will run again with
    the new config.
    """
    # NB: uncomment when this is fixed:
    # https://github.com/juju-solutions/layer-basic/pull/61
    # apt.purge(['puppet'])
    # remove_state('puppet.available')

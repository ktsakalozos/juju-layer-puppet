# layer-puppet
> Juju charms.reactive layer for Puppet.
  The idea is shamelessly taken from battlemidget/juju-layer-node


## states emitted

**puppet.available** - This state is emitted once Puppet packages
are installed. Rely on this state to gate a `puppet apply` operation.


## api

The puppet layer doesn't provide any special API, but it does include
[layer-apt](https://git.launchpad.net/layer-apt/tree/README.md). We
utilize the `apt` module to update repositories and install Puppet
packages.

If alternate repositories should be used to install Puppet packages,
set the `install_sources` and `install_keys` config options as described in the
layer-apt README linked above.


## notes

Puppet packages on Trusty are known to have YAML parsing issues. By default,
this layer will install updated packages from the Puppet Labs trusty repository
to avoid these issues. If this is not desired, use the `install_sources` config
option to override this behavior on Trusty.

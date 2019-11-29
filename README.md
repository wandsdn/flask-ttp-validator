A flask web application for validating [Table Type Patterns](https://www.opennetworking.org/wp-content/uploads/2013/04/OpenFlow%20Table%20Type%20Patterns%20v1.0.pdf), built on top of the [ttp-tools](https://github.com/wandsdn/ttp-tools) library.

You can try it online [here](https://wand.net.nz/ttp-validator/).

### Installation

Install the C library requirements for [gmpy2](https://gmpy2.readthedocs.io/en/latest/) as required by [ofequivalence](https://github.com/wandsdn/ofequivalence). For Debian based distributions run:
```
apt install libgmp-dev libmpfr-dev libmpc-dev
```
Then use pip to install the python requirements. In the root directory (containing this readme) run:
```
pip install -r requirements.txt
```
If you wish to install TTP validator to the system path use (use the --user option to install for only the local user):
```
pip install .
```

### Configuration

The TTP validator uses [Flask instance configuration](https://exploreflask.com/en/latest/configuration.html#instance-folder). When running out of a local repository place the ttp-validator.cfg file into a directory named instance:
```
mkdir instance
cp ttp-validator.cfg instance/
```
By default ttp-validator.cfg contains a single configuration option:
```
CACHE_DIR = '/tmp/ttp-validator'
```
If CACHE_DIR exists the TTP validator saves results to this directory, including errors for debugging. The cache also serves permanent links to results, without which permanent links will not work; for persistence across reboots, you should move the cache directory. If CACHE_DIR does not exist, the validator will silently disable the cache. To enable the default cache path run:
```
mkdir /tmp/ttp-validator
```

### Running (Quick Start)
Refer to the [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/quickstart/) for a full description of how to deploy and run Flask apps.

To run a local server, in the root directory (containing this readme) run.
```
export FLASK_APP=flask_ttp_validator
flask run
(or python -m flask run)
```

### License

The code is licensed under the Apache License Version 2.0, see the included LICENSE file.

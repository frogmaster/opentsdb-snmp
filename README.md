# opentsdb-snmp

Simple program to push metrics from snmp to [opentsdb](http://opentsdb.net/)

## configuration

Configuration is stored in JSON format, which is a pain to write, so you should probably generate it somohow.
Format is as follows:

    {
        "tsd": [
            {
                "hostname": "foo.bar",
                "port": 4242
            },
            {
                "hostname": "localhost",
            }
        ].
        "devices": [
            {
                "hostname": "foobar",
                "community": "public",
                "snmp_version": 2,
                "metrics": [
                    {
                        "metric": "interface.packets",
                        "oid": ".1.3.6.1.2.1.31.1.1.1.9",
                        "type": "walk",
                        "tags": {
                            "direction": "in",
                            "type": "broadcast"
                        },
                        "resolver": "default"
                    }
                ]
            }
        ]
    }

### tsd section

Entry contains hostname and port (not mandatory and defaults to 4242)


### devices section

Entry contains hostname, snmp community and version (1/2). 
Also a metrics array, which needs more detail.


### metrics section

* *metric* - name for the metric
* *oid* - snmp *numeric* oid, note that the . in the beginning is mandatory. Textual oids, are currently not supported
* *type* - walk/get wether we should use get or walk for this oid
* *tags* - extra tags to append. Note that metric+tags should be unique per device section (although no such check currenly exists). Also host=hostname tag is added automatically.
* *resolver* - resolver to use.

### resolvers

Resolver takes raw data and returns extra tags.
Currently there's an implementation for default resolver. More will be added as needed. Also to location and mechanism of resolver classes is subject to change.

#### default

Adds index tags based on oid index. For example when metrics oid is 1.2.3 and walk returns something like 1.2.3.4.5 then tags returned are index=4 and index2=5


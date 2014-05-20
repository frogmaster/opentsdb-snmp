# opentsdb-snmp

Simple program to push metrics from snmp to [opentsdb](http://opentsdb.net/)

## configuration

Configuration is stored in YAML format and has three values: tsd, hosts_file and metrics.
Example configuration:

    hosts_file: "misc/sample_hostlist.yml"
    tsd: #list of tsd-s
      -
        host: "localhost" #host
        port: 5431 #port
      -
        host: "localhost"
    metrics:
      ifHCOutUcastPkts: #unique metric name used in (device section in hostlist file)
        resolver: "ifname" #relevant only when walk is used
        oid: "1.3.6.1.2.1.31.1.1.1.11"
        metric: "interface.packets" #metric name on tsd side
        type: "walk" #either walk or get
        rate: true #wether rate should be calculated
        tags: #tags on tsd side
          direction: "out"
          type: "unicast"


####hosts_file example:

    - 
      hostname: "foo"
      community: "bar"
      snmp_version: 2
      metrics: 
        - "ifInHCOutUcastPkts"
    - 
      hostname: "bar"
      community: "foo"
      snmp_version: 2
      metrics: 
        - "ifInUcastPkts"
        - ""ifOutOctets"



## resolvers

Resolver takes raw data and returns extra tags.
Things passed to resolver resolve() method are: index, device object

### default

Adds index tags based on oid index. For example when metrics oid is 1.2.3 and walk returns something like 1.2.3.4.5 then tags returned are index=4 and index2=5


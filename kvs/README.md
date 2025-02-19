A simple key-value storage server

Bind to a port to expose a {string:string} map to the specified network interface.

Flexible HTTP support:\
Embedding everything in a GET request makes it really easy to poke at the contents with a browser, curl, wget, etc if the kvs client library isn't available. The return value is always JSON encoded.

Supported Operations:\
get: http://authority/oper=get&key=keyhere\
set: http://authority/oper=set&key=key&value=val\
delete: http://authority/oper=delete&key=keyhere

Future work:
- Back with RAFT or some other multinode HA protocol 
- C++ rewrite
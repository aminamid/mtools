# -*- coding: utf-8 -*-

from logging import getLogger

module_logger = getLogger(__name__)

def parsed_args():
    from mutil import mopts
    from mutil.schema import Schema, And, Use, Or, Optional, SchemaError
    import json

    myhelp = """
    Usage:
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  get (<query> | -f FILE)
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  put (<influxdb_point> | -f FILE)
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  getdb
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  getcq
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  dropcq <cqid>
      {progname} [options] [(--logfile | --logboth)] [(--debug | --nolog)]  dropcq_all

    Options:
      -h HOST, --host=HOST  hostname [default: localhost]
      -p PORT, --port=PORT  port number [default: 8086]
      -u USER, --user=USER  user for influxdb [default: root]
      -w PSWD, --pswd=PSWD  password for influxdb [default: root]
      -d DB, --dbname=DB    dbname [default: testdb]
      -t TIMEOUT, --timeout=TIMEOUT    dbname [default: 60]
      -f FILE, --file=FILE  filename
      --force               force create if db is not exists [default: False]
      --separate DELIMIT    delimit by [default: ,]
      --logfile             out put log to file  [default: False]
      --logboth             out put log to file and console  [default: False]
      --logdir DIR          out put log to file  [default: ./dir]
      --loglevel <level>    loglevel [default: 30]
      --debug               set loglevel to logging.DEBUG [default: False]
      --nolog               set loglevel to 0 [default: False]
      --help                show this message

    """
    myschema = Schema({
      'get':bool,
      'put':bool,
      'getdb':bool,
      'getcq':bool,
      'dropcq':bool,
      'dropcq_all':bool,
      '<query>': Or(None, str),
      '<influxdb_point>': Or(None, str),
      '<cqid>': Or(None, Use(int)),
      '--host': basestring,
      '--port': Use(int),
      '--user': basestring,
      '--pswd': basestring,
      '--dbname': basestring,
      '--timeout': Use(int),
      '--file': Or(None, Use(open, error="Files should be readable")),
      '--force': bool,
      '--separate': Or(None, basestring),
      '--logfile': bool,
      '--logboth': bool,
      '--logdir': basestring,
      '--loglevel': Or(None, Use(int)),
      '--debug': bool,
      '--nolog': bool,
      '--help': bool,
      })

    return mopts.parse(myhelp=myhelp, myschema=myschema, filepath=__file__)


def main(opts, handle_mgr  ):
    module_logger.debug('opts=[{0}]'.format(opts))
    import json
    from mutil.minf import PoorInfluxDBClient
    client = PoorInfluxDBClient(host=opts.host, port=opts.port, username=opts.user, password=opts.pswd, database=opts.dbname, timeout=opts.timeout, force=opts.force)
    if opts.get:
        if opts.query:
            print client.csv_get(opts.query,opts.separate)
        elif opts.file:
            print client.query(opts.file.read())
    elif opts.put:
        print client.write_points('list continuous queries')
    elif opts.getdb:
        print client.csv_dbget()
    elif opts.getcq:
        print client.csv_get('list continuous queries',opts,separate)
    elif opts.dropcq:
        client.query('drop continuous query {0}'.format(opts.cqid))
        print client.csv_get('list continuous queries',opts.separate)
    elif opts.dropcq_all:
        res = client.query('list continuous queries')
        for id in [ point[res[0]['columns'].index('id')] for point in res[0]['points']]:
            client.query('drop continuous query {0}'.format(id))
        print client.csv_get('list continuous queries')


if __name__ == '__main__':
    from mutil import mlog
    opts = parsed_args()

    logging_modules=[ __name__, 'mutil.minf' ]

    handle_mgr = mlog.HandleManager(
        names = logging_modules,
        logdir = opts.logdir,
        prefix = mlog.prefix(__file__),
        postfix = 'log',
        enable_stream = not opts.logfile ,
        enable_file = opts.logboth or opts.logfile,
        level = opts.loglevel )

    main(opts=opts, handle_mgr= handle_mgr)



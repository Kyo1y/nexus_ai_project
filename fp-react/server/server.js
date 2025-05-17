'use strict'

require('dotenv').config()
const config = require('./config')

require('pml-trace-logging')({ // this should be called in the main application start file, before any other references
  doPretty: config.logging.pretty,
  ignoreList: 'time,hostAddress,hostProcess,hostName,logType,elapsedTime,traceHeaders,request,response,module', // properties to not log
  excludePattern: config.session.exclusionPattern, // endpoints not to use request logging
})
const logger = require('pml-trace-logging').consoleLogger.child({module: require('path').basename(__filename)})
const cluster = require('cluster')
const prometheus = require('./middleware/prometheus')

if (cluster.isMaster) {
  logger.info('Master thread [pid:%d]', process.pid)
  logger.info('Launching [threadCount:%d] server threads listening on [port:%d] in [env:%s] mode', config.server.threadCount, config.server.port, process.env.ENVIRONMENT_NAME)

  cluster.on('exit', function(worker) {
    logger.warn('Worker [pid:%d] DIED      starting new process', worker.process.pid)
    prometheus.threadsActiveGauge.dec(1)
    startWorker()
  })

  cluster.on('online', function(worker) {
    logger.info('Worker [pid:%d] DETECTED  by master', worker.process.pid)
    prometheus.removeThreadFromWatchlist(worker.process.pid)
  })

  prometheus.initMaster()

  startWorker()

  for (let i = 1; i < config.server.threadCount; i++) {
    setTimeout(startWorker, i * 500)
  }
} else {
  require('./serverWorker.js')
}

function startWorker() {
  try {
    let worker = cluster.fork()

    if (worker.process) {
      logger.info('Worker [pid:%d] REQUESTED by master', worker.process.pid)
      prometheus.addThreadToWatchlist(worker.process.pid)
      prometheus.threadsStartedCounter.inc(1)
      prometheus.threadsActiveGauge.inc(1)
    } else {
      logger.error('Invalid worker object returned from cluster.fork():')
    }
  } catch (err) {
    logger.error('Error thrown on cluster.fork(): %j', err)
  }
}

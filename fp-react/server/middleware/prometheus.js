const express = require('express')
const metricsServer = express()
const promClient = require('prom-client')
const config = require('../config')
const logger = require('pml-trace-logging').consoleLogger.child({module: require('path').basename(__filename)})
const aggregatorRegistry = new promClient.AggregatorRegistry()
const globalRegistry = promClient.register
const prometheusPort = config.server.port + 1
const threadsHealthyCounter = new promClient.Counter({
  name: 'threads_healthy',
  help: 'Number of worker threads running and listening for connections',
  labelNames: ['threadsHealthy'],
})
const threadsStartedCounter = new promClient.Counter({
  name: 'threads_started',
  help: 'Number of worker threads that have been started by the master process',
  labelNames: ['threadsStarted'],
})
const threadsActiveGauge = new promClient.Gauge({
  name: 'threads_active',
  help: 'Current number of worker threads running',
  labelNames: ['threadsActive'],
})

let monitoredPidList = []

function removeThreadFromWatchlist(pid) {
  monitoredPidList = monitoredPidList.filter((item) => item !== pid)
}

function addThreadToWatchlist(pid) {
  monitoredPidList.push(pid)
  setTimeout(() => {
    if (monitoredPidList.includes(pid)) {
      logger.error('Worker [pid:%d] MISSING   did not start within 5 seconds, removing from watchlist', pid)
      removeThreadFromWatchlist(pid)
    }
  }, 5000)
}

function initWorker() {
// Enable collection of default metrics
  promClient.collectDefaultMetrics()
}

function initMaster() {
  metricsServer.get('/cluster_metrics', (req, res) => {
    aggregatorRegistry.clusterMetrics((err, metrics) => {
      let skip5Lines

      if (err) {
        logger.info(err)
      }

      skip5Lines = metrics.split(/\r?\n/).splice(5).join('\n') // required to skip dupe lines coming from aggregated workers

      res.set('Content-Type', aggregatorRegistry.contentType)
      res.send(globalRegistry.metrics() + skip5Lines) // concats master thread plus aggregated worker thread stats
    })
  })

  metricsServer.listen(prometheusPort)
  logger.info('Prometheus cluster metrics on [port:%d] at /cluster_metrics', prometheusPort)
}

module.exports = {
  initMaster,
  initWorker,
  removeThreadFromWatchlist,
  addThreadToWatchlist,
  threadsActiveGauge,
  threadsStartedCounter,
  threadsHealthyCounter,
}

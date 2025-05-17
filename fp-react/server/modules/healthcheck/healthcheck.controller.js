'use strict'

const https = require('https')
const logger = require('pml-trace-logging').consoleLogger.child({module: 'healthcheck'})
const config = require('../../config')
const Healthcheck = require('./healthcheck.model')
const axios = require('axios')

const personaURL = config.auth.personaURL.substr(0, config.auth.personaURL.indexOf('/persona-service/')) + '/persona-service/health'

const oAuthCheck = () => axios.get(config.auth.oAuthAboutURL)
  .then(() => true)
  .catch(() => {
    logger.error(`Failed to fetch ${config.auth.oAuthAboutURL}`)
    return false
  })

const agent = new https.Agent({
  rejectUnauthorized: false,
})

const personaCheck = () => axios.get(personaURL, {httpsAgent: agent})
  .then((response) => {
    if (response.data.status !== 'UP') {
      return false
    }

    return true
  })
  .catch((e) => {
    logger.error(`Failed to fetch ${personaURL}: ${e}`)
    return false
  })

const mongoCheck = () => Healthcheck.remove({}).exec()
  .then(() => Healthcheck.create({widget: 'xyzpdq'}))
  .then((results) => Healthcheck.findOne({widget: results.widget}).exec())
  .then(() => true)
  .catch(() => false)

exports.index = function(req, res) {
  const status = {}

  Promise.all([mongoCheck(), oAuthCheck(), personaCheck()])
    .then(function(values) {
      status.mongoUp = values[0]
      status.oAuthUp = values[1]
      status.personaUp = values[2]
      status.healthy = status.mongoUp && status.oAuthUp && status.personaUp

      return res.status(200).json(status) // always return 200; the payload gives the health status, not the HTTP status code
    })
}

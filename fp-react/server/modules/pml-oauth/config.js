const logger = require('pml-trace-logging').consoleLogger.child({module: 'pmlOAuth'})

let config = {
  app: null,
  express: null,
  appBaseURL: null,
  appCallbackPath: null,
  appLoggedOutPath: null,
  oAuthAuthorizationURL: null,
  oAuthClientID: null,
  oAuthClientSecret: null,
  oAuthLogoutURL: null,
  oAuthScopes: null,
  oAuthTokenURL: null,
  oAuthUserInfoURL: null,
  personaURL: null,
}

const configHandler = {
  get: function(target, prop) {
    let message

    if (target.hasOwnProperty(prop)) {
      if (target[prop]) {
        return target[prop]
      }

      logger.error(message = 'option not set: ' + prop)
      throw new Error(message)
    }

    logger.error(message = 'invalid option: ' + prop)
    throw new Error(message)
  },

  set: function(target, prop, value) {
    let message

    if (!target.hasOwnProperty(prop)) {
      logger.error(message = 'invalid option: ' + prop)
      throw new Error(message)
    }

    if (prop !== 'app' && prop !== 'express' && typeof value !== 'string') {
      console.error(message = 'string required for option: ' + prop)
      throw new Error(message)
    }

    switch (prop) {
      // ensure function is passed as value
      case 'app':
      case 'express':
        if (typeof value !== 'function') {
          console.error(message = 'function required for option: ' + prop)
          throw new Error(message)
        }
        break

      // ensure trailing slash
      case 'appBaseURL':
        if (value.charAt(value.length - 1) !== '/') {
          value = value + '/'
        }
        break

      // remove leading slash
      case 'appCallbackURL':
        if (value.charAt(0) === '/') {
          value = value.slice(1)
        }
        break

      // no validation for the other options
      default:
    }

    if (prop !== 'express' && prop !== 'app' && prop !== 'oAuthClientSecret') {
      logger.info(`Setting option ${prop} to '${value}'`)
    } else {
      logger.info(`Setting option ${prop}`)
    }
    target[prop] = value

    return true
  },
}

module.exports = new Proxy(config, configHandler)

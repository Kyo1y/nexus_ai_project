let config = require('./config')
const logger = require('pml-trace-logging').consoleLogger.child({module: 'pmlOAuth'})
const passport = require('passport')
const authController = require('./controller')
const authRoutes = require('./routes')

/**
 * @param {Object} options                        Object with needed properties defined
 * @param {String} options.appCallbackPath        Path to use for OAuth callback, with no leading slash
 * @param {String} options.appLoggedOutPath       Path in app to send user to after OAuth logs them out
 * @param {String} options.oAuthAuthorizationURL  External URL for user's browser
 * @param {String} options.oAuthClientID          App's user ID configured in OAuth
 * @param {String} options.oAuthClientSecret      App's password in OAuth
 * @param {String} options.oAuthLogoutURL         External logout URL for user's browser
 * @param {String} options.oAuthScopes            Scopes of OAuth access requested of user
 * @param {String} options.oAuthTokenURL          Internal URL for server to server token exchange
 * @param {String} options.oAuthUserInfoURL       Internal URL for server to server user info request
 * @param {String} options.personaURL             URL for persona info; {{USERID}} will be replaced user's ID
 **/

exports.initialize = (options) => {
  for (let prop in options) {
    config[prop] = options[prop]
  }

  config.app.use(passport.initialize())

  module.exports.router = authRoutes(authController())
}

module.exports.isAuthenticated = authController.isAuthenticated
module.exports.forceLoginIfUnauthenticated = authController.forceLoginIfUnauthenticated
module.exports.router = null

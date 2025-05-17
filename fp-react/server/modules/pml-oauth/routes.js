const config = require('./config')
const passport = require('passport')
const Strategy = require('pml-trace-passport-oauth2').Strategy
const logger = require('pml-trace-logging').consoleLogger.child({module: 'pmlOAuth'})

// Setup routes and handlers for Passport

module.exports = (AuthController) => {
  const express = config.express
  const router = express.Router()

  router.use('/pml/corp/logout', AuthController.routeLogout)

  router.use('/pml/corp', (req, res, next) => {
    if (req.query.startUrl) {
      res.cookie('startUrl', req.query.startUrl)
    }

    return passport.authenticate('corp', {failureRedirect: '/', scope: config.oAuthScopes.split(' '), session: false})(req, res, next)
  },
  )

  router.get('/pml/callback', passport.authenticate('corp', {
    failureRedirect: '/',
    session: false,
  }), AuthController.createSession)

  router.get('/pml/refresh', AuthController.routeRefresh)

  passport.use('corp',
    new Strategy({
      authorizationURL: config.oAuthAuthorizationURL,
      callbackURL: config.appBaseURL + config.appCallbackPath,
      clientID: config.oAuthClientID,
      clientSecret: config.oAuthClientSecret,
      tokenURL: config.oAuthTokenURL,
      state: false,
    }, AuthController.authenticationSuccessful),
  )

  return router
}

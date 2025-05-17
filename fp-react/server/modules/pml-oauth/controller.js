const request = require('request')
const async = require('async')
const jwt = require('jsonwebtoken')
const uuid = require('node-uuid')
const axios = require('axios')
const qs = require('querystring')
const moment = require('moment')
const logger = require('pml-trace-logging').consoleLogger.child({module: 'pmlOAuth'})
const config = require('./config')

module.exports = () => {
  let user

  // Middleware and route handler functions
  function routeLogout(req, res) {
    let logoutCallback = `?redirect_uri=${config.appBaseURL}${config.appLoggedOutPath}`
    let userId = req.session && req.session.user && req.session.user.username ? req.session.user.username : null
    let id

    if (req.cookies.session) {
      id = JSON.parse(req.cookies.session).sessionID
    }

    if (req.query.code) {
      logoutCallback = logoutCallback + `/${req.query.code}`
    }

    logger.info('Attempting logout for: %s', id)

    req.session.destroy((err) => {
      if (err) {
        logger.error('Failed to destroy user\'s session')
      } else {
        logger.info('Session destroyed for user %s', userId || id)
      }

      res.clearCookie('session')

      res.redirect(config.oAuthLogoutURL + logoutCallback)
    })
  }

  async function routeRefresh(req, res) {
    let data
    let success = true
    let response

    logger.info('Received refresh request')

    try {
      data = qs.stringify({
        refresh_token: req.session.user.refreshToken,
        client_id: config.oAuthClientID,
        client_secret: config.oAuthClientSecret,
        grant_type: 'refresh_token',
      })

      response = await axios.post(config.oAuthTokenURL, data, {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      if (response.data.error && response.data.error === 'invalid_grant') {
        logger.info('refreshToken failed, error: %j' + response.data.error)
        success = false
      }

      if (!response.data.access_token || !response.data.expires_in) {
        logger.info('No valid access token')
        success = false
      }

      if (success) {
        req.session.user.accessToken = response.data.access_token
        req.session.user.refreshToken = response.data.refresh_token
        req.session.user.accessTokenExpiration = moment().add(response.data.expires_in, 'seconds').toDate()

        req.session.save()

        logger.info('User ' + req.session.user.username + ' refreshed')

        return res.send({accessTokenExpiration: req.session.user.accessTokenExpiration})
      }
    } catch (error) {
      logger.error(error)
      res.status(500)
      return res.send('Failed to exchange refresh token')
    }
  }

  function authenticationSuccessful(accessToken, refreshToken, params, profile, done) {
    let data = jwt.decode(accessToken)

    if (data instanceof Object) {
      profile = data
    } else {
      profile = JSON.parse(data)
    }

    logger.info('User ' + profile.loggedInAs + ' authenticated successfully')

    user = {
      accessToken: accessToken,
      context: profile.context,
      refreshToken: refreshToken,
      role: 'user',
      sessionID: uuid.v1(),
      username: profile.loggedInAs,
    }

    user.accessTokenExpiration = moment().add(params.expires_in, 'seconds').toDate()

    return done(null, user)
  }

  // Called after Passport successfully exchanges Auth code (ie. the user is valid, and should be logged into the app)
  async function createSession(req, res) {
    let userInfo, json

    if (!req.user) {
      return res.json(404, {
        message: 'Something went wrong, please try again.',
      })
    }

    userInfo = await getAdditionalUserInfo(req.user.accessToken)

    if (!isAuthorized(userInfo)) {
      let url = '/auth/pml/corp/logout'

      logger.info(`User ${req.user.username} is not authorized.`)

      url = url + '?code=UNAUTHORIZED'

      return res.redirect(url)
    }

    json = {
      sessionID: req.user.sessionID,
      loggedInAs: req.user.username,
      email: userInfo.emailAddress,
      roles: userInfo.roles || [],
      name: userInfo.name || '',
      authorized: userInfo.authorized || false,
      permissions: userInfo.permissions || [],
      accessTokenExpiration: req.user.accessTokenExpiration,
    }

    json = addIsProperties(json, userInfo)

    req.session.user = req.user

    res.cookie('session', JSON.stringify(json))

    req.session.userInfo = json

    req.session.save()

    if (req.cookies.startUrl && req.cookies.startUrl !== '') {
      let destination = req.cookies.startUrl

      res.clearCookie('startUrl')
      logger.info(`Redirecting to ${destination}; clearing cookie`)

      return res.redirect(destination)
    }

    return res.redirect('/')
  }

  // End of Middleware functions

  // Private Functions

  /*
  Define which attributes are necessary for entry to the application here.
  Return false if the user does not meet those minimum requirements.
  You could require specific Security Roles or Persona service values.

  Any service calls required to get these values should be implemented in
  the getAdditionalUserInfo function.
  */

  function addIsProperties(data, source) {
    for (let p in source) {
      if (source.hasOwnProperty(p)) {
        if (p.startsWith('is')) { // if property starts with 'is'
          if (p[2].toUpperCase() === p[2]) { // and following letter is upper case (ie. isSomeProperty)
            data[p] = source[p] // then copy over to data
          }
        }
      }
    }

    return data
  }

  function isAuthorized(userInfo) {
    return userInfo.authorized
  }

  // Makes additional calls to OAuth, Persona, etc to get more user attributes and/or permissions
  function getAdditionalUserInfo(accessToken) {
    return new Promise((resolve) => {
      let userId = jwt.decode(accessToken).loggedInAs
      let url = config.personaURL.replace('{{USERID}}', userId)
      let userInfo

      async.parallel({
        persona: function(callback) {
          request({
            uri: url,
            method: 'GET',
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
            },
            rejectUnauthorized: false,
          },
          function(err, response, data) {
            if (err) {
              logger.error('Persona error: %j', err)
            }
            try {
              data = JSON.parse(data)
            } catch (SyntaxError) {
              logger.info('Error parsing the user information returned from the Persona server: %s', data)
              return callback(new Error('Error parsing returned data'))
            }
            return callback(null, data)
          })
        },
        clientInfo: function(callback) {
          logger.info('Requesting information about the current user from the OAuth2 server')
          request({
            uri: config.oAuthUserInfoURL,
            method: 'GET',
            headers: {
              'Content-Type': 'application/json; charset=utf-8',
              'Authorization': 'Bearer ' + accessToken,
            },
          },
          function(err, response, data) {
            if (err) {
              logger.error('OAuth clientinfo error: %j', err)
            }
            try {
              data = JSON.parse(data)
              callback(null, data)
            } catch (SyntaxError) {
              logger.info('Error parsing the user information returned from the OAuth2 server: %s', data)
              callback(null, null)
            }
          })
        },
      }, function(err, results) {
        if (err) logger.error(err)

        userInfo = {...sanitizePersona(results.persona), ...results.clientInfo} // results.clientInfo // @TODO: Add persona checks here

        return resolve(userInfo)
      })
    })
  }

  return {
    authenticationSuccessful: authenticationSuccessful,
    createSession: createSession,
    routeLogout: routeLogout,
    routeRefresh: routeRefresh,
  }
}

// eslint-disable-next-line no-unused-vars
function sanitizePersona({_request, backends, ...rest}) { // strips out '_request' and 'backends' properties
  return rest
}

function isAccessTokenExpired(accessTokenExpiration) {
  let tokenExpirationDate

  if (!accessTokenExpiration) return true

  tokenExpirationDate = new Date(accessTokenExpiration)

  return Date.now() > tokenExpirationDate.getTime()
}

module.exports.isAuthenticated = function isAuthenticated(req, res, next) {
  if (!req.session) {
    return res.status(401).send('No session found for user')
  } else if (!req.session.user) {
    return res.status(401).send('No user found in session')
  } else if (isAccessTokenExpired(req.session.user.accessTokenExpiration)) {
    return res.status(401).send('Access token expired')
  }

  return next()
}

module.exports.forceLoginIfUnauthenticated = function forceLoginIfUnauthenticated(req, res, next) {
  if (!req.session || !req.session.user || isAccessTokenExpired(req.session.user.accessTokenExpiration)) {
    return res.redirect(`/auth/pml/corp?startUrl=${encodeURIComponent(req.originalUrl)}`)
  }

  return next()
}

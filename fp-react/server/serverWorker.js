'use strict'

const config = require('./config')
const path = require('path')
const express = require('express')
const app = express()
const expressSession = require('express-session')
const MongoStore = require('connect-mongo')({'session': expressSession})
const errorHandler = require('errorhandler')
const cors = require('cors')
const mongoose = require('mongoose')
const cookieParser = require('cookie-parser')
const bodyParser = require('body-parser')
const about = require('./controllers/about.controller')
const cacheHeaders = require('./middleware/cache-headers')
const prometheus = require('./middleware/prometheus')
const initProxies = require('./middleware/proxies')
const logger = require('pml-trace-logging').consoleLogger.child({module: require('path').basename(__filename)})
const pmlTrace = require('pml-trace')
const requestLoggerMiddleware = require('pml-trace-logging').requestLoggerMiddleware
const pmlOAuth = require('./modules/pml-oauth')
const mongoChats = require('./modules/mongo-chats')
const mongoPrompts = require('./modules/mongo-prompts')
const swaggerUi = require('swagger-ui-express')
const swaggerDocument = require('./swagger.json')
const fileUploadMiddleware = require('express-fileupload')

// use the Webpack Dev Server and its proxy when in localhost mode, otherwise serve React from configured folder (ie. ./build)
const useWebpackDevServer = config.common.env === 'localhost'

let sessionMiddleware, sessionStorage

sessionStorage = new MongoStore({
  'mongooseConnection': mongoose.connection,
  'clear_interval': 3600,
  'autoReconnect': true,
})

sessionMiddleware = expressSession({
  saveUninitialized: true,
  resave: true,
  secret: config.session.secret,
  key: 'authorization.sid',
  cookie: {maxAge: config.session.maxAge},
  store: sessionStorage,
})

function conditionalSessionMiddleware(req, res, next) {
  if (!new RegExp(config.session.exclusionPattern).test(req.originalUrl)) {
    return sessionMiddleware(req, res, next)
  }
  return next()
}

function conditionalRequestLoggingMiddleware(req, res, next) {
  if (config.logging.accessLogs.disable || (config.logging.accessLogs.disableProxy && (new RegExp(/\/proxy/).test(req.originalUrl)))) {
    return next()
  }
  return requestLoggerMiddleware(req, res, next)
}

app.use(conditionalSessionMiddleware)
app.use(pmlTrace.generateMiddleware(config.session.exclusionPattern))
app.use(conditionalRequestLoggingMiddleware)
app.use(cors())
app.use(cacheHeaders)

mongoose.Promise = global.Promise
mongoose.connect(config.mongo.uri, config.mongo.options)

initProxies(app)

app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())
app.use(cookieParser())
app.use(fileUploadMiddleware({debug: false, safeFileName: true, abortOnLimit: true, useTempFiles: false}))

pmlOAuth.initialize({
  app,
  express,
  appBaseURL: config.auth.appBaseURL, // URL to the app, with trailing slash
  appCallbackPath: config.auth.appCallbackPath, // path to use for OAuth callback, with no leading slash
  appLoggedOutPath: config.auth.appLoggedOutPath, // path in app to send user to after OAuth logs them out
  oAuthAuthorizationURL: config.auth.oAuthAuthorizationURL, // external URL for user's browser
  oAuthClientID: config.auth.oAuthClientID, // app's user ID configured in OAuth
  oAuthClientSecret: config.auth.oAuthClientSecret, // app's password in OAuth
  oAuthLogoutURL: config.auth.oAuthLogoutURL, // external URL for user's browser
  oAuthScopes: config.auth.oAuthScopes, // scopes of OAuth access requested of user
  oAuthTokenURL: config.auth.oAuthTokenURL, // internal URL for server to server
  oAuthUserInfoURL: config.auth.oAuthUserInfoURL, // internal URL for server to server
  personaURL: config.auth.personaURL, // {{USERID}} will be replaced user's ID
})

prometheus.initWorker()

app.get('/ping', function(req, res) {
  res.send('Service is Active')
})

app.get('/heartbeat', function(req, res) {
  res.send('Service is Active')
})

app.get('/about', about)

!config.common.isProd && app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument)) // swagger only if not prod

app.use('/auth', pmlOAuth.router)
app.use('/healthcheck', require('./modules/healthcheck'))
app.use('/chats', mongoChats.router)
app.use('/prompts', mongoPrompts.router)
app.use(errorHandler()) // Must be last

// Quick fix for webpack-dev-server
if (useWebpackDevServer) {
  app.get('*', function(req, res) {
    res.redirect('http://localhost:3000/')
  })
} else {
  app.set('appPath', path.join(config.common.root, 'build'))
  logger.info(`Service website from: ${app.get('appPath')}`)
  app.use(express.static(app.get('appPath')))
}

let server = require('http').createServer(app)

server.listen(config.server.port, err => {
  if (err) {
    throw err
  }
  logger.info('Worker [pid:%d] LISTENING for requests', process.pid)
  prometheus.threadsHealthyCounter.inc(1)
})

const path = require('path')
const getEnv = require('getenv')

/*
  These vars are provided by Docker images, do not set manually except for testing

 */
const DOCKER_RUNNING = process.env.DOCKER_RUNNING || false // docker images will set this to true

/*
 Required Env Vars

 These include credentials and must come from the environment
 They can not be stored in code

 */
const OAUTH_CLIENT_SECRET = getEnv.secret('OAUTH_CLIENT_SECRET') // secret used to auth the app against OAuth
const SESSION_SECRET = getEnv.secret('SESSION_SECRET') // environment specific session secret
const MONGO_PASSWORD_SECRET = getEnv.secret('MONGO_PASSWORD_SECRET') // Base64 encoded client cert key

/*
 Optional Env Vars

 These don't include credentials, or don't during local dev, at least
 Mongo will include credentials when not running locally, for example

 */
const BUILD_TAG = getEnv('BUILD_TAG', 'localhost')
const ENVIRONMENT_NAME = getEnv('ENVIRONMENT_NAME', 'localhost') // specify dev, model, or prod here instead of with NODE_ENV
const HOSTNAME = DOCKER_RUNNING || getEnv.string('HOSTNAME', 'unsetHostname.pennmutual.com') // used for headers and /about endpoint
const LOG_PRETTY = getEnv.boolean('LOG_PRETTY', true) // false, 0, or unset to use default JSON logging
const AI_URL = getEnv('AI_URL', 'http://mpamuw101.pennmutual.com:6005/chat') // http://testmlearn01.pennmutual.com:6005/chat  http://mpamuw101.pennmutual.com:6005/chat
const MONGO_URI = getEnv('MONGO_URI', 'mongodb://localhost:27017/chatquote').replace('{{MONGO_PASSWORD_SECRET}}', MONGO_PASSWORD_SECRET)
const OAUTH_ABOUT_URL = getEnv('OAUTH_ABOUT_URL', 'http://oauth2orize-mo.pennmutual.com/about')
const OAUTH_AUTHORIZATION_URL = getEnv('OAUTH_AUTHORIZATION_URL', 'https://test.pennmutual.com/oauth2/dialog/authorize')
const OAUTH_CLIENT_ID = getEnv('OAUTH_CLIENT_ID', 'chatquote') // the name OAuth uses to refer to this application
const OAUTH_LOGOUT_URL = getEnv('OAUTH_LOGOUT_URL', 'https://test.pennmutual.com/oauth2/logout')
const OAUTH_TOKEN_URL = getEnv('OAUTH_TOKEN_URL', 'http://oauth2orize-mo.pennmutual.com/oauth/token')
const OAUTH_USERINFO_URL = getEnv('OAUTH_USERINFO_URL', 'http://oauth2orize-mo.pennmutual.com/api/userinfo')
const PERSONA_URL = getEnv('PERSONA_URL', 'https://iam-persona-mo.pennmutual.com/persona-service/user/userid/{{USERID}}?ctx=chatquote')
const PML_BASE_URL = getEnv('PML_BASE_URL', 'http://localhost:3000/') // the URL for the load balancer VIP when deployed
const SERVER_PORT = getEnv.int('SERVER_PORT', 3000) // the port this server runs on
const THREAD_COUNT = getEnv.int('THREAD_COUNT', 1) // use 1 for local development, 3+ for deployed environments

module.exports = {
  client: {
    sourceDirectory: process.env.PML_APP_SOURCE || 'build',
  },
  common: {
    buildTag: BUILD_TAG,
    inContainer: DOCKER_RUNNING === 'true',
    isProd: ENVIRONMENT_NAME === 'production',
    env: ENVIRONMENT_NAME,
    root: path.normalize(path.resolve(__dirname, '../..')),
  },
  logging: {
    accessLogs: {
      disable: false,
      disableProxy: false,
    },
    pretty: LOG_PRETTY,
  },
  session: {
    exclusionPattern: /\/keepalive|\/heartbeat|\/about|\/healthcheck|\.(?:html|css|png|gif|jpg|jpeg|woff|ico|svg|ttf)/,
    secret: SESSION_SECRET,
    expirationInSeconds: 30 * 60, // In seconds
    timeToCheckExpiredSessions: 600,
  },
  server: {
    baseURL: PML_BASE_URL,
    hostname: DOCKER_RUNNING === 'true' ? 'ECS Container' : HOSTNAME,
    port: SERVER_PORT,
    errorLog: './nodejs.error.log',
    proxies: [
      {
        localPath: '/proxy/ai',
        options: {
          target: AI_URL,
          pathRewrite: {'^/proxy/ai': ''}, // AI_URL.pathname
          changeOrigin: true,
          logLevel: 'info',
        },
      },
    ],
    threadCount: THREAD_COUNT,
    cacheExpiration: 10 * 60, // In seconds
    timeToRefreshBeforeExpiration: 5, // In minutes
    cronTaskTimeInterval: 4 * 60 * 1000, // In miliseconds
  },
  auth: {
    appBaseURL: PML_BASE_URL,
    appCallbackPath: 'auth/pml/callback',
    appLoggedOutPath: '#/loggedout',
    oAuthAboutURL: OAUTH_ABOUT_URL,
    oAuthAuthorizationURL: OAUTH_AUTHORIZATION_URL,
    oAuthClientID: OAUTH_CLIENT_ID,
    oAuthClientSecret: OAUTH_CLIENT_SECRET,
    oAuthLogoutURL: OAUTH_LOGOUT_URL,
    oAuthScopes: 'offline_access basic_access pml_data_access',
    oAuthTokenURL: OAUTH_TOKEN_URL,
    oAuthUserInfoURL: OAUTH_USERINFO_URL,
    personaURL: PERSONA_URL,
  },
  mongo: {
    uri: MONGO_URI,
    options: {
      writeConcern: {w: 1},
      useNewUrlParser: true,
      useUnifiedTopology: true,
      useCreateIndex: true,
    },
  },
}

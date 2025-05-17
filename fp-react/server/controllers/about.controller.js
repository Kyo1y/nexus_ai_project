const config = require('../config')
const pjson = require('../../package.json')

module.exports = function about(req, res) {
  let data = {
    version: pjson.version || config.common.buildTag,
    env: config.common.env,
    baseURL: config.server.baseURL,
    hostname: config.server.hostname,
    listeningPort: config.server.port,
    threadCount: config.server.threadCount,
    rootDirectory: config.common.root,
    nodeVersion: process.version,
    uptime: process.uptime(),
  }

  return res.json(req.headers['x-forwarded-for'] ? scrubbedAbout(data) : data)
}

function scrubbedAbout(source) {
  // eslint-disable-next-line no-unused-vars
  const {nodeVersion, hostname, rootDirectory, certificates, listeningPort, ...sourceRest} = source

  return sourceRest
}

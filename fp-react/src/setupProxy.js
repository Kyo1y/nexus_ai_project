/*

If the Webpack dev server is running inside a Docker image, we need to proxy
to the 'nodeserver' container host defined in docker-compose.yml

Otherwise, we assume the developer is running locally and point to localhost

 */

const proxy = require('http-proxy-middleware')

let target

if (process.env.DOCKER_RUNNING) {
  target = 'http://nodeserver:5000/'
} else {
  target = 'http://localhost:5000/'
}

module.exports = function(app) {
  app.use(proxy('/about', {target: target}))
  app.use(proxy('/healthcheck', {target: target}))
  app.use(proxy('/api', {target: target}))
  app.use(proxy('/api-docs', {target: target}))
  app.use(proxy('/auth', {target: target}))
  app.use(proxy('/chats', {target: target}))
  app.use(proxy('/prompts', {target: target}))
  app.use(proxy('/proxy', {target: target}))
}

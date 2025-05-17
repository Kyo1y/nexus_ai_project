// Setup routes for chats

const {isAuthenticated, forceLoginIfUnauthenticated} = require('../pml-oauth')

module.exports = (express, controller) => {
  const router = express.Router()

  router.post('/', [isAuthenticated, controller.saveChat])

  router.get('/', [isAuthenticated, controller.getChats])

  router.put('/:id', [isAuthenticated, controller.updateChat])

  router.get('/:id', [forceLoginIfUnauthenticated, controller.getChat])

  router.delete('/:id', [isAuthenticated, controller.deleteChat])

  return router
}

// Setup routes for submissions

const {isAuthenticated} = require('../pml-oauth')

module.exports = (express, controller) => {
  const router = express.Router()

  router.get('/', [isAuthenticated, controller.getPrompts])

  return router
}

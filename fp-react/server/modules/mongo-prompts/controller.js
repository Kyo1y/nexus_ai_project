const logger = require('pml-trace-logging').consoleLogger.child({module: 'mongo-form-store'})
const mongoose = require('mongoose')

let PromptSchema = new mongoose.Schema({
  promptName: {type: String, required: true},
  query: {type: String, required: true},
}, {
  collection: 'prompts',
  versionKey: false,
})

let Prompt = mongoose.model('Prompt', PromptSchema)

module.exports = {
  getPrompts: async function getPrompts(req, res) {
    let prompts = await Prompt.find()

    if (!prompts.length) {
      return res.sendStatus(404)
    }

    return res.send(prompts)
  },
  getPrompt: async function getPrompt(req, res) {
    let prompt = await Prompt.findById(req.params.id)

    if (!prompt) {
      return res.sendStatus(404)
    }

    return res.send(prompt)
  },
  updatePrompt: async function updatePrompt(req, res) {
    // @TODO: should also check that user is admin or owner of prompt
    let prompt = await Prompt.findById(req.params.id)

    if (!prompt) {
      return res.sendStatus(404)
    }

    prompt.promptName = req.body.promptName
    prompt.query = req.body.query

    prompt.save()
      .then(item => {
        res.send(item)
      })
      .catch(err => {
        res.status(400).send(err)
      })
  },
  deletePrompt: async function deletePrompt(req, res) {
    // @TODO: should also check that user is admin or owner of prompt
    let prompt = await Prompt.findById(req.params.id)

    if (!prompt) {
      return res.sendStatus(404)
    }

    prompt.remove()
      .then(() => {
        res.sendStatus(200)
      })
      .catch(err => {
        res.status(400).send(err)
      })
  },
  addPrompt: async function addPrompt(req, res) {
    let prompt = new Prompt({promptName: req.body.promptName, query: req.body.query})

    prompt.save()
      .then(item => {
        res.send(item)
      })
      .catch(err => {
        res.status(400).send(err)
      })
  },
}

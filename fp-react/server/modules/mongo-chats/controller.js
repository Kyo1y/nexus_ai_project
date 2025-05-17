const logger = require('pml-trace-logging').consoleLogger.child({module: 'mongo-form-store'})
const mongoose = require('mongoose')

const ConversationSchema = new mongoose.Schema({
  isQuery: {type: Boolean, required: true},
  content: {type: String, required: true},
  timestamp: {type: Date, default: Date.now},
})

let ChatSchema = new mongoose.Schema({
  userId: {type: String, required: true},
  sessionName: {type: String, required: true},
  conversation: {
    type: [ConversationSchema],
    default: undefined,
  },
  modificationTimestamp: {type: Date, default: Date.now},
  timestamp: {type: Date, default: Date.now},
}, {
  collection: 'chats',
  versionKey: false,
})

let Chat = mongoose.model('Chat', ChatSchema)

module.exports = {
  saveChat: async function saveChat(req, res) {
    let chat

    if (req.body._id) {
      return res.status(400).send('Illegal field: _id')
    }

    // create new chat

    for (let prop in req.body) { // fix incorrect property types so they get saved to Mongo as such. * See note below.
      if (req.body.hasOwnProperty(prop)) {
        if (req.body[prop] === 'false') { // make it false if it is "false"
          req.body[prop] = false
        }

        if (req.body[prop] === 'true') { // make it true if it is "true"
          req.body[prop] = true
        }

        if (Number(req.body[prop]).toString() === req.body[prop]) { // If it is a number, save it as a number.
          req.body[prop] = Number(req.body[prop])
        }
      }
    }

    chat = new Chat({userId: req.session.user.username, sessionName: req.body.sessionName, conversation: req.body.conversation})

    // save chat
    chat.save()
      .then(item => {
        res.send(item)
      })
      .catch(err => {
        res.status(400).send(err)
      })
  },
  updateChat: async function updateChat(req, res) {
    let chat, updatedChat

    req.body.lastEditedByUserId = req.session.user.username
    req.body.modificationTimestamp = new Date()

    try {
      // can only update your own chats
      chat = await Chat.findOne({_id: req.params.id, userId: req.session.user.username}, null, {new: true})
    } catch (e) {
      logger.error(`Chat ${req.params.id} update error: ${e}`)
      return res.status(500).send(e)
    }

    if (!chat) {
      logger.warn(`Chat ${req.params.id} Not found`)
      return res.status(404).send(`${req.params.id} Not found`)
    }

    if (chat.userId !== req.session.user.username) {
      return res.sendStatus(403)
    }

    try {
      updatedChat = {...chat.toObject(), ...req.body}
      await Chat.updateOne({_id: req.params.id, userId: req.session.user.username}, updatedChat, {upsert: false})
    } catch (e) {
      logger.error(`Chat ${req.params.id} update error: ${e}`)
      return res.status(500).send(e)
    }

    return res.send(updatedChat)
  },
  getChat: async function getChat(req, res) {
    let chat = await Chat.findById(req.params.id)

    if (!chat) {
      return res.sendStatus(404)
    }

    return res.send(chat)
  },
  getChats: async function getChats(req, res) {
    let chats = await Chat.find()

    if (!chats.length) {
      return res.sendStatus(404)
    }

    return res.send(chats)
  },
  deleteChat: async function deleteChat(req, res) {
    let chat = await Chat.findById(req.params.id)

    if (chat.userId !== req.session.user.username) {
      return res.sendStatus(403)
    }

    if (!chat) {
      return res.sendStatus(404)
    }

    await Chat.deleteOne({_id: req.params.id})

    return res.sendStatus(200)
  },
}

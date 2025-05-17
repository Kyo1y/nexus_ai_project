'use strict'

const mongoose = require('mongoose')
const Schema = mongoose.Schema

const HealthcheckSchema = new Schema({
  widget: {
    type: String,
    required: true,
    unique: false,
  },
  createdAt: Date,
})

/**
 * Pre-save hook
 */
HealthcheckSchema
  .pre('save', function(next) {
    let currentDate

    if (!this.isNew) return next()

    currentDate = new Date()

    if (!this.createdAt) {
      this.createdAt = currentDate
    }

    next()
  })

module.exports = mongoose.model('Healthcheck', HealthcheckSchema, 'healthcheck')

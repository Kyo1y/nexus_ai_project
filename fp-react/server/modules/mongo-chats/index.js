const express = require('express')
const controller = require('./controller')
const routes = require('./routes')

module.exports.router = routes(express, controller)

exports.renderNotFound = function(req, res) {
  res.status(404).format({
    'text/html': function() {
      res.render('server/views/404')
    },
    'application/json': function() {
      res.json({
        error: 'Path not found',
      })
    },
    'default': function() {
      res.send('Path not found')
    },
  })
}

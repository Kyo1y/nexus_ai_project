exports.index = function(req, res) {
  return res.sendStatus(200)
}

exports.log = function(req, res) {
  if (!req.body) {
    return res.json(400, {
      message: 'You did not provide a required parameter.',
    })
  }

  return res.sendStatus(200)
}

import axios from 'axios'
import {getSession} from 'utils/session'
import CONSTANTS from 'Constants'

const client = axios.create({baseURL: CONSTANTS.baseProxyUrl})

client.interceptors.request.use(
  ({params, ...config}) => {
    let session = getSession()

    config.params = {app: CONSTANTS.appName, ...params}

    config.headers.accept = 'application/json'
    config.headers.authorization = 'Bearer ' + (session ? session.sessionID : 'NOTOKEN')

    return config
  },
  error => {
    Promise.reject(error)
  },
)

client.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      window.location = '/auth/pml/corp'
    } else {
      return Promise.reject(error.response)
    }
  },
)

export default client

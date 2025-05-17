import React, {useEffect, useState} from 'react' // eslint-disable-line no-unused-vars
import {getSession, hasSession} from 'utils/session' // eslint-disable-line no-unused-vars
import {Navigate, Route, Routes} from 'react-router-dom'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome' // eslint-disable-line no-unused-vars
// import moment from 'moment'
import * as api from 'api/api'

import HomePage from 'views/HomePage/HomePage'
import Unauthorized from 'views/Unauthorized/Unauthorized'
import LoggedOutPage from 'views/LoggedOutPage/LoggedOutPage'
import NotFoundPage from 'views/NotFoundPage/NotFoundPage'

const Loading = () => { // eslint-disable-line no-unused-vars
  return (
    <div className="loading-message">
      <FontAwesomeIcon size="lg" icon="spinner"/>
      <span>Loading</span>
    </div>
  )
}

const requestRefresh = () => {
  console.info('Requesting refresh')
  api.refreshSession()
    .then(response => {
      // startRefreshCycle(response.data.accessTokenExpiration)
    })
    .catch(() => {
      window.location.href = '/auth/pml/corp'
    })
}

const PrivateRoute = ({component: RequestedComponent, path, componentProps}) => { // eslint-disable-line no-unused-vars
  const [isLoading, setLoading] = useState(true)
  const [isAuthenticated, setAuthenticated] = useState(false)
  const [isAuthorized, setAuthorized] = useState(false)

  useEffect(() => {
    let startUrl = ''

    if (path !== '/') {
      startUrl = '?startUrl=' + window.encodeURIComponent('/#' + path)
    }

    setAuthenticated(true)
    let session = getSession()
    // startRefreshCycle(session.accessTokenExpiration, startUrl)
    
    setAuthorized(true)
    setLoading(false)
  }, [path])

  if (isLoading) {
    return (<Loading/>)
  } else if (isAuthenticated && isAuthorized) {
    return (<RequestedComponent {...componentProps} />)
  }

  return (<Navigate to="/unauthorized" replace />)
}

const Router = () => (
  <>
    <Routes>
      <Route path="/loggedout/:code?" exact element={<LoggedOutPage />} />
      <Route path="/unauthorized" exact element={<Unauthorized />} />
      <Route exact path="/" element={<Navigate to="/home" replace />} />
      <Route exact path="/home" element={
        <PrivateRoute path="/home" exact component={HomePage} />
      }/>
      <Route path="/user/:userID" element={<HomePage />} />
      <Route element={<NotFoundPage />} />
    </Routes>
  </>
)

export default Router

import React from 'react'
import {HashRouter} from 'react-router-dom'
import Router from 'Router'
import AuthProvider from 'context/auth.provider'
import {AppProvider} from './context/app.context'
import {ChatProvider} from './context/chat.context'
import {PromptProvider} from './context/prompt.context'
import {hasSession, getSession} from 'utils/session'
import {ToastContainer} from 'react-toastify'
import Header from 'components/Header/Header'
import Footer from 'components/Footer/Footer'
import 'react-toastify/dist/ReactToastify.min.css'
import 'utils/icons'
import 'react-perfect-scrollbar/dist/css/styles.css'

const App = () => {
  let session
  let fullName, id, email, roles

  if (hasSession()) {
    session = getSession()
    fullName = session && session.name
    id = session && session.loggedInAs
    email = session && session.email
    roles = session && session.roles
  }

  return (
    <AppProvider>
      <PromptProvider>
        <ChatProvider>
          <AuthProvider
            value={{
              id,
              fullName,
              email,
              roles,
            }}
          >
            <HashRouter>
              <Header/>
              <Router/>
              <Footer/>
              <ToastContainer/>
            </HashRouter>
          </AuthProvider>
        </ChatProvider>
      </PromptProvider>
    </AppProvider>
  )
}

export default App

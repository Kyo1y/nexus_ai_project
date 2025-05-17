import React, {useState} from 'react'
import AuthContext from './auth.context'

export const AuthProvider = (props) => {
  const [user] = useState(props.value)

  return (
    <AuthContext.Provider
      value={
        {user}
      }
    >
      {props.children}
    </AuthContext.Provider>
  )
}

export default AuthProvider

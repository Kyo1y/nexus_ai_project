import React, {createContext, useState} from 'react'

const AppContext = createContext()

export const AppProvider = (props) => {
  const [showPrompts, setShowPrompts] = useState(true) // eslint-disable-line no-unused-vars

  return (
    <AppContext.Provider
      value={
        {
          showPrompts,
          setShowPrompts,
        }
      }
    >
      {props.children}
    </AppContext.Provider>
  )
}

export default AppContext

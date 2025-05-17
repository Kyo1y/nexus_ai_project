import React, {useContext} from 'react'
import AppContext from 'context/app.context'
import ChatContext from 'context/chat.context'

const LeftNav = () => {
  const {showPrompts, setShowPrompts} = useContext(AppContext)
  const {newChat} = useContext(ChatContext)
  let chatsClasses = 'btn btn-middle' + (showPrompts ? '' : ' selected')
  let promptsClasses = 'btn btn-start' + (showPrompts ? ' selected' : '')

  return (
    <>
      <nav className="btn-group">
        <a className={promptsClasses} onClick={() => setShowPrompts(true)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17" fill="none">
            <path d="M2.66667 1V4.33333M1 2.66667H4.33333M3.5 12.6667V16M1.83333 14.3333H5.16667M9.33333 1L11.2381 6.71429L16 8.5L11.2381 10.2857L9.33333 16L7.42857 10.2857L2.66667 8.5L7.42857 6.71429L9.33333 1Z" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Prompts</span>
        </a>
        <a className={chatsClasses} onClick={() => setShowPrompts(false)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="18" viewBox="0 0 17 18" fill="none">
            <path d="M12.6667 5.16667H14.3333C15.2538 5.16667 16 5.91286 16 6.83334V11.8333C16 12.7538 15.2538 13.5 14.3333 13.5H12.6667V16.8333L9.33333 13.5H6C5.53976 13.5 5.1231 13.3135 4.82149 13.0118M4.82149 13.0118L7.66667 10.1667H11C11.9205 10.1667 12.6667 9.42048 12.6667 8.5V3.5C12.6667 2.57953 11.9205 1.83334 11 1.83334H2.66667C1.74619 1.83334 1 2.57953 1 3.5V8.5C1 9.42048 1.74619 10.1667 2.66667 10.1667H4.33333V13.5L4.82149 13.0118Z" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Chats</span>
        </a>
        <a className="btn btn-end" onClick={() => newChat()}>
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 13 13" fill="none">
            <path d="M6.5 1.5V11.5M11.5 6.5L1.5 6.5" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>New chat</span>
        </a>
      </nav>
    </>
  )
}

export default LeftNav

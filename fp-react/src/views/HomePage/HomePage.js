import React, {useCallback, useEffect, useContext} from 'react'
import LeftNav from 'components/LeftNav/LeftNav'
import ActiveConversation from 'components/ActiveConversation/ActiveConversation'
import PromptContext from 'context/prompt.context'
import ChatContext from 'context/chat.context'
import PromptInput from 'components/PromptInput/PromptInput'
import AppContext from 'context/app.context'
import { useParams } from 'react-router-dom'

const HomePage = () => {
  const {requestItems: requestPrompts, items: prompts} = useContext(PromptContext)
  const {requestItems: requestChats, items: chats, setQuery, loadChat, setIdentity} = useContext(ChatContext)
  const {showPrompts} = useContext(AppContext)
  const requestPromptsCallback = useCallback(requestPrompts, []) // eslint-disable-line
  const requestChatsCallback = useCallback(requestChats, []) // eslint-disable-line
  const identityCallback = useCallback(setIdentity, [])
  const { userID } = useParams();

  function formatIdentity(input) {
    // Replace dashes with spaces
    let formattedString = input.replace(/-/g, ' ');
    
    // Capitalize each word
    formattedString = formattedString.replace(/\b\w/g, function(char) {
        return char.toUpperCase();
    });

    return formattedString;
}

let formattedIdentity = null;
if (typeof userID !== 'undefined') {
  formattedIdentity = formatIdentity(userID);
} 

  useEffect(() => {
    requestPromptsCallback('')
    requestChatsCallback('')

    identityCallback(formattedIdentity)
  }, []) // eslint-disable-line

  return (
    <>
      <LeftNav />
      <main>
        <menu className="samples">
          {showPrompts
            ? prompts.map(prompt => (
              <li key={prompt._id}>
                <a onClick={() => setQuery(prompt.query)}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 25 25" fill="none">
                    <path d="M2.66667 1V4.33333M1 2.66667H4.33333M3.5 12.6667V16M1.83333 14.3333H5.16667M9.33333 1L11.2381 6.71429L16 8.5L11.2381 10.2857L9.33333 16L7.42857 10.2857L2.66667 8.5L7.42857 6.71429L9.33333 1Z" stroke="#00AA44" strokeWidth="1.67" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span style={{whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", width: "100%"}}>
                    {prompt.promptName}
                  </span>
                </a>
              </li>
            ))
            : chats.map(chat => (
              <li key={chat._id}>
                <a onClick={() => loadChat(chat._id)}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 25 25" fill="none">
                    <path d="M12.3889 4.61111H13.9444C14.8036 4.61111 15.5 5.30756 15.5 6.16667V10.8333C15.5 11.6924 14.8036 12.3889 13.9444 12.3889H12.3889V15.5L9.27778 12.3889H6.16667C5.73711 12.3889 5.34822 12.2148 5.06672 11.9333M5.06672 11.9333L7.72222 9.27778H10.8333C11.6924 9.27778 12.3889 8.58133 12.3889 7.72222V3.05556C12.3889 2.19645 11.6924 1.5 10.8333 1.5H3.05556C2.19645 1.5 1.5 2.19645 1.5 3.05556V7.72222C1.5 8.58133 2.19645 9.27778 3.05556 9.27778H4.61111V12.3889L5.06672 11.9333Z" stroke="#00AA44" strokeWidth="1.67" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span style={{whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", width: "100%"}}>
                    {chat.sessionName}
                  </span>
                </a>
              </li>
            ))
          }
        </menu>
        <article className="active-chat">
          <ActiveConversation/>
          <PromptInput/>
        </article>
      </main>
    </>
  )
}

export default HomePage

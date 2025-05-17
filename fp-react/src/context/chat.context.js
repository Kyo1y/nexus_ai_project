import React, {createContext, useState} from 'react'
import * as API from 'api/api'
import * as contextUtils from './context-utils'

const ChatContext = createContext()



export const ChatProvider = (props) => {
  const [error, setError] = useState()
  const [isLoading, setIsLoading] = useState(false)
  const [item, setItem] = useState(null)
  const [items, setItems] = useState([])
  const [itemSuccess, setItemSuccess] = useState(false)
  const [, setItemLoading] = useState(false) // eslint-disable-line no-unused-vars
  const [totalItems, setTotalItems] = useState(0)
  const [query, setQuery] = useState('')
  const [conversation, setConversation] = useState([])
  const [chat, setChat] = useState(null)
  const [cannedResponsesPosition, setCannedResponsesPosition] = useState(0)
  const [conversationId, setConversationId] = useState(null)
  const [isReplay, setIsReplay] = useState(false)

  const cannedIdentities = ['Michael Kane', 'Other Leader', '<unset>'];
  const [identity, setIdentity] = useState(cannedIdentities[0])

  /*
  const cannedResponses = [
    'DEMO: This is a static demo response, but the real bot could respond with a rate that could be expected for the described client.',
    'DEMO: The response could also ask for follow-up details that are required for a quote.',
    'DEMO: Eventually we\'ll tie this into the real back end for live data.',
    'DEMO: This is a static demo response that can be used to show what things might look like with a live response.',
    'DEMO: This response is very long to show you that the typing speed will get faster when the amount of text gets very long.  This is to ensure that the user doesn\'t have to wait for 15 seconds for a long response to render.',
  ]
*/

  const newChat = () => {
    setConversation([])
    setConversationId(null)
    setIsReplay(false)
  }

  const loadChat = (id) => {
    setIsLoading(false)
    setIsReplay(true)

    if (items.length) {
      let matchingChats = {}

      matchingChats = items.filter(c => {
        return c._id === id
      })

      if (matchingChats.length) {
        setChat(matchingChats[0])
        setConversation(matchingChats[0].conversation)
      } else {
        console.error('No matching chat found for ID: ', id)
      }
    }
  }

  const saveChat = async() => {
    setChat({...chat, conversation: chat.conversation})
    updateItem(chat)
  }

  const addConversationPrompt = async(content) => {
    let response, id

    setIsLoading(true)

    setConversation([...conversation, {isQuery: true, content}])

    resetQuery()

    if (!conversationId) {
      response = await API.initiateConversation()

      if (response.data.chat_id) {
        id = response.data.chat_id
        setConversationId(id)
      }
    }

    response = await API.updateConversation(id || conversationId, content, identity)

    if (response.data) {
      let text = response.data.chat.replaceAll('\n', '\r\n')
      let tableData = null
      let rowData = null
      let dataHeader = null

      if (response.data.html_table) {
        tableData = response.data.html_table
      }
      if (response.data.data_table) {
        rowData = response.data.data_table
      }
      if (response.data.data_header) {
        dataHeader = response.data.data_header
      }
      setConversation([...conversation, {isQuery: true, content}, {isQuery: false, content: text, tableData: tableData, rowData: rowData, dataHeader: dataHeader}])
    }

    if (cannedResponsesPosition === 4) {
      setCannedResponsesPosition(0)
    } else {
      setCannedResponsesPosition(cannedResponsesPosition + 1)
    }

    setIsLoading(false)
  }

  const addConversationResponse = (content) => {
    setConversation([...conversation, {isQuery: false, content}])
  }

  const resetQuery = () => setQuery('')

  const requestItems = async() => {
    return null
    // return contextUtils.requestItems(API.getChats, {}, setItems, setTotalItems)
  }

  const requestItem = async(id) => {
    try {
      const items = await contextUtils.requestItem(API.getCannedPrompts)
      return items['examples']
    } catch (e) {
      return e instanceof Error ? e : new Error(e)
    }
  }

  const updateItem = async(c) => {
    let response

    setItemLoading(true)

    try {
      response = await API.updateChat(c)
      setItemLoading(false)
      setItemSuccess(response)
      setTimeout(() => { setItemSuccess(false) }, 200)
      return response
    } catch (e) {
      console.error('error ==='.toUpperCase(), e)
      setError(e)
      setItemLoading(false)
      throw new Error(e)
    }
  }

  return (
    <ChatContext.Provider
      value={
        {
          addConversationPrompt,
          addConversationResponse,
          chat,
          conversation,
          error,
          isLoading,
          isReplay,
          item,
          itemSuccess,
          items,
          loadChat,
          newChat,
          query,
          requestItem,
          requestItems,
          resetQuery,
          saveChat,
          setChat,
          setConversation,
          setError,
          setIsLoading,
          setIsReplay,
          setItem,
          setItemLoading,
          setItemSuccess,
          setQuery,
          totalItems,
          updateItem,
          setIdentity,
          identity,
          cannedIdentities,
        }
      }
    >
      {props.children}
    </ChatContext.Provider>
  )
}

export default ChatContext

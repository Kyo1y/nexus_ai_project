import React, {createContext, useState} from 'react'
import * as API from 'api/api'
import * as contextUtils from './context-utils'

const PromptContext = createContext()

export const PromptProvider = ({children}) => {
  const [error, setError] = useState()
  const [item, setItem] = useState(null)
  const [items, setItems] = useState([])
  const [itemSuccess, setItemSuccess] = useState(false)
  const [itemLoading, setItemLoading] = useState(false) // eslint-disable-line no-unused-vars
  const [totalItems, setTotalItems] = useState(0)

  const requestItems = async() => {
    try {
      const items = await API.getCannedPrompts()
      const cannedExamples = items.data.examples;
      setItems(cannedExamples)
      return cannedExamples
    } catch (e) {
      console.log('Failed to make request')
      return e instanceof Error ? e : new Error(e)
    }
    // return contextUtils.requestItems(API.getPrompts, {}, setItems, setTotalItems)
  }

  const requestItem = async(id) => {
    return null
    // try {
    //   const i = await contextUtils.requestItem(API.getPrompt, id)

    //   for (const prop in i) {
    //     if (prop.endsWith('_dt')) {
    //       i[prop] = contextUtils.stripTime(i[prop])
    //     }
    //   }

    //   return i
    // } catch (e) {
    //   return e instanceof Error ? e : new Error(e)
    // }
  }

  return (
    <PromptContext.Provider
      value={
        {
          error,
          item,
          itemLoading,
          itemSuccess,
          items,
          requestItem,
          requestItems,
          setError,
          setItem,
          setItemLoading,
          setItemSuccess,
          setItems,
          totalItems,
        }
      }
    >
      {children}
    </PromptContext.Provider>
  )
}

export default PromptContext

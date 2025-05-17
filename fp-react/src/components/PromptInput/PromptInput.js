import React, {useContext, useRef, useEffect} from 'react'
import ChatContext from 'context/chat.context'

const useFocus = () => {
  const htmlElRef = useRef(null)
  const setFocus = () => { htmlElRef.current && htmlElRef.current.focus() }

  return [ htmlElRef, setFocus ]
}

const PromptInput = () => {
  const {query, setQuery, addConversationPrompt, isLoading, isReplay} = useContext(ChatContext)
  const [inputRef, setInputFocus] = useFocus()

  let btnClasses = 'btn btn-send'

  if (isLoading || isReplay) {
    btnClasses = btnClasses + ' btn-disabled'
  }

  // useEffect when isLoading changes, set focus to inputRef
  useEffect(() => { setInputFocus() }, [isLoading, setInputFocus])

  const onEnterPress = (e) => {
    if (e.keyCode === 13 && e.shiftKey === false) {
      e.preventDefault()
      addConversationPrompt(query)
    }
  }

  // make textarea have cursor focus
  // https://stackoverflow.com/questions/28889826/how-to-set-focus-on-an-input-field-after-rendering

  return (
    <form className="chatbox" action="">
      <div className="form-field">
        <label htmlFor="askMe">Ask me</label>
        <textarea name="promptInput" id="askMe" cols="30" rows="3" value={query}
          ref={inputRef}
          disabled={isLoading || isReplay}
          onKeyDown={onEnterPress}
          onChange={e => setQuery(e.target.value)}
          placeholder={'Type or copy/paste your question to ChatInsight here.'}></textarea>
      </div>
      <a className={btnClasses} onClick={() => !isLoading && addConversationPrompt(query) && setInputFocus()}>
        <span >Send</span>
      </a>
    </form>
  )
}

export default PromptInput

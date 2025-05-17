import React, {useCallback, useState, useEffect} from 'react'
import Typewriter from 'typewriter-effect'
import BotIcon from 'components/BotIcon/BotIcon'
const LoadingResponse = ({text, latest = false, isReplay = false, loading = false, delay = 5, tableData = null}) => {
    const outputMessages = ['Thinking...']

  return (
    <div className="query-response">
      <BotIcon />
      <div className="query-response-text">
      <Typewriter
          options={{
            strings: ['Thinking...', text],  // Set the multiText prop to strings in the new API
            autoStart: true,  // Auto-start the typing effect
            loop: false,  // Keep looping the text
            delay: delay,  // Type speed (same as typeSpeed)
            deleteSpeed: 50,  // You can adjust this if you want the text to delete (optional)
            cursor: '|',  // Cursor style
            pauseFor: 12000,  // Pause between the typing cycles (mapped from multiTextDelay)
          }}
        />        
      </div>
    </div>
  )
}

export default LoadingResponse

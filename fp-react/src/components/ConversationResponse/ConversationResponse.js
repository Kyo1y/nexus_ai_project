import React from 'react'
import Typewriter from 'typewriter-effect'
import DataTable from 'components/DataTable/DataTable'
import BotIcon from 'components/BotIcon/BotIcon'
const ConversationResponse = ({text, latest = false, isReplay = false, loading = false, delay = 5, tableData = null, rowData = null, dataHeader = null}) => {
  return (
    <div className="query-response">
      <BotIcon />
      <div className="query-response-text">
        {!isReplay && !loading && latest ? (
          <React.Fragment>
          <Typewriter
            options={{
              strings: [text],  // Convert `text` into an array for `strings` prop
              autoStart: true,  // Start typing automatically
              loop: false,      // Set loop to false (since `text` is a single string)
              delay: delay,     // Type speed (same as typeSpeed)
              deleteSpeed: 50,  // Optional: You can set deleteSpeed if you want to delete the text (not required here)
              cursor: '|',      // Cursor style
              pauseFor: 1000,   // Optional: Add pause after text is typed (default 1000ms)
            }}
          />
            {rowData && dataHeader && (
              <DataTable data={rowData} headers={dataHeader}/>
            )}
          </React.Fragment>)
          : (<React.Fragment>
            <p>{text}</p>
            {rowData && dataHeader && (
              <DataTable data={rowData} headers={dataHeader}/>
            )}
            </React.Fragment>)
        }
      </div>
    </div>
  )
}

export default ConversationResponse

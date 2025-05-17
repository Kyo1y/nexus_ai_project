import React, {useContext} from 'react'
import ConversationQuery from 'components/ConversationQuery/ConversationQuery'
import ConversationResponse from 'components/ConversationResponse/ConversationResponse' // eslint-disable-line no-unused-vars
import LoadingResponse from 'components/ConversationResponse/LoadingResponse' // eslint-disable-line no-unused-vars
import ChatContext from 'context/chat.context'
import IdentityManager from 'components/IdentityManager/IdentityManager'
import SuggestionCard from 'components/SuggestionCard/SuggestionCard'
const HelloLine = (props) => {
  const { fullName } = props;
  if (fullName !== null) {
    var firstName = fullName.replace(/ .*/,'');
    return <p>Hello {firstName},</p>
  }
  return null;
}

const ActiveConversation = () => {
  const {conversation, isLoading, isReplay, identity} = useContext(ChatContext)


  if (!conversation.length) {
    
    return (
      <section className="landing">
        <h1>Chat Insight - Technology Demo</h1>
        <HelloLine fullName={identity} />

        <p>This technology demo shows what is possible using a GPT based large language model to find insight on financial professionals. This is for <strong>demonstration purposes only</strong>, and all information should be verified.</p>
        <p>Currently supported queries:</p>
        <ul>
          <li>Abnormal business volume</li>
          <li>Not written a policy</li>
          <li>Wrote policy over face amount</li>
        </ul>
        {/* <p>Currently supported rating factors include:</p>
        <small className="legal">
          <div className="capabilities">
            <ul>
              <li>Type II Diabetes (A1C, duration)</li>
              <li>Generalized Anxiety Disorder</li>
              <li>Asthma</li>
            </ul>
          </div>
          <div className="warnings">
            <ul>
              <li>Obesity (height/weight, BMI)</li>
              <li>Hypertension (blood pressure)</li>
              <li>Hyperlipidemia (cholesterol)</li>
            </ul>
          </div>
        </small> */}
      </section>
    )
  }

  return (
    <section className="query">
      {
        conversation.map((item, index) => item.isQuery ? (<ConversationQuery key={index} text={item.content}/>) : (
          <ConversationResponse 
            isReplay={isReplay} 
            loading={isLoading} 
            latest={index === (conversation.length - 1)} 
            key={index} text={item.content} 
            tableData={item.tableData} 
            rowData={item.rowData}
            dataHeader={item.dataHeader}
          />))
      }
      { isLoading
        ? (<LoadingResponse delay={50} loading={false} latest={true} text={'Thinking...'}/>) : null
      }
    </section>
  )
}

export default ActiveConversation

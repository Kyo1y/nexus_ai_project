import React, {useContext} from 'react'
import ChatContext from 'context/chat.context'

const SuggestionCard = ({title, text}) => {
    
    const {setQuery} = useContext(ChatContext);
    return (
        <div className="suggestion-card">
            <button className="btn" onClick={() => setQuery(text)}>
                {title}
            </button>
        </div>
    )
}

export default SuggestionCard;
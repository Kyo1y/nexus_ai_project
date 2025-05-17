import React from 'react'

const ConversationQuery = ({text}) => {
  return (
    <div className="query-title">
      <div className="query-icon-user">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <g clipPath="url(#clip0_59_35599)">
            <rect x="2" y="2" width="32" height="32" rx="16" fill="#F7F8F8"/>
            <path d="M18 18.4C20.8719 18.4 23.2 16.0719 23.2 13.2C23.2 10.3281 20.8719 8 18 8C15.1282 8 12.8 10.3281 12.8 13.2C12.8 16.0719 15.1282 18.4 18 18.4Z" fill="#37474F"/>
            <path d="M5.8667 34C5.8667 27.2989 11.299 21.8667 18 21.8667C24.7011 21.8667 30.1334 27.2989 30.1334 34H5.8667Z" fill="#37474F"/>
          </g>
          <rect x="1.25" y="1.25" width="33.5" height="33.5" rx="16.75" stroke="#94D500" strokeWidth="1.5"/>
          <defs>
            <clipPath id="clip0_59_35599">
              <rect x="2" y="2" width="32" height="32" rx="16" fill="white"/>
            </clipPath>
          </defs>
        </svg>
      </div>
      <div className="query-title-text">
        <h2>{text}</h2>
      </div>
    </div>
  )
}

export default ConversationQuery

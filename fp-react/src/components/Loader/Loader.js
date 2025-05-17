import React from 'react'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'

const Loader = ({size}) => {
  return (
    <div className="loader">
      <FontAwesomeIcon size={size} icon="spinner" />
    </div>
  )
}

export default Loader

import React from 'react'
import {shallowToJson} from 'enzyme-to-json'
import {shallow} from 'enzyme'
import App from './App'

it('renders without crashing', () => {
  shallow(<App />)
})

it('matches the snapshot', () => {
  const component = shallow(<App />)

  expect(shallowToJson(component)).toMatchSnapshot()
})

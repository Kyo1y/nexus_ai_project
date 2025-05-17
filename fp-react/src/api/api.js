import request from 'utils/request'
import axios from 'axios'

/*
Initiate conversation with AI
 */
export const initiateConversation = () => {
  return axios.get(`http://localhost:5000/chat/`, {headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}})
  // return request.get(`http://localhost:5000/chat`, {headers: {'Content-Type': 'application/json'}})
}

/*
Send text to the AI
 */
export const updateConversation = (conversationId, text, identity = null) => {
  const obj = {
    chat: text,
    identity: identity
  }

  return axios.post(`http://localhost:5000/chat/` + conversationId, obj, {headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST, GET, PUT'}})
  // return request.post(`http://localhost:5000/chat` + conversationId, obj, {headers: {'Content-Type': 'application/json'}})
}

export const getCannedPrompts = () => {
  return axios.get(`http://localhost:5000/chat/canned`, {headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}})
}

/*
GETs a chat
 */
export const getChat = (chatId) => {
  return request.get(`/chats/${chatId}`, {headers: {'Content-Type': 'application/json'}})
}

/*
GETs chats
 */
export const getChats = (params) => {
  return request.get(`/chats`, {params: params}, {headers: {'Content-Type': 'application/json'}})
}

/*
POSTs a new chat
 */
export const createChat = (obj) => {
  return request.post(`/chats`, obj, {headers: {'Content-Type': 'application/json'}})
}

/*
DELs a chat
 */
export const deleteChat = (id) => {
  return request.delete(`/chats/${id}`, {headers: {'Content-Type': 'application/json'}})
}

/*
PUTs an updated chat
 */
export const updateChat = (obj) => {
  return request.put(`/chats/${obj._id}`, obj, {headers: {'Content-Type': 'application/json'}})
}

/*
GETs a prompt
 */
export const getPrompt = (promptId) => {
  return request.get(`/prompts/${promptId}`, {headers: {'Content-Type': 'application/json'}})
}

/*
GETs prompts
 */
export const getPrompts = (params) => {
  return request.get(`/prompts`, {params: params}, {headers: {'Content-Type': 'application/json'}})
}

/*
Causes server to refresh the user's OAuth token
 */
export const refreshSession = () => {
  // return axios.get(`/auth/pml/refresh`)
}

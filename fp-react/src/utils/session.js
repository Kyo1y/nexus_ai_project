import Cookies from 'js-cookie'

export const hasSession = () => {
  return Boolean(Cookies.getJSON('session'))
}

export const getSession = () => {
  if (!hasSession) return {}
  return Cookies.getJSON('session')
}

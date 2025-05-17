import {FTAR_ALLOWED_ROLES} from './constants'

export const canAccessFtars = (user) => {
  let acceptedRoles

  if (user) {
    acceptedRoles = FTAR_ALLOWED_ROLES.filter(value => user.roles.includes(value))

    return acceptedRoles.length > 0
  }

  return false
}

export const nameValidator = {
  maxLength: 65,
  minLength: 2,
  pattern: {
    value: /^[ A-Za-z'-]*$/,
    message: 'letters, spaces, apostrophes, and hyphens only',
  },
}

export const serviceHoursValidator = {
  setValueAs: (value) => Number(value),
  pattern: {
    value: /^[0-9]*\.?[0-9]*$/,
    message: 'positive numbers only',
  },
}

export const noBlanksValidator = {
  validate: (value) => {
    if (value && value.trim() === '') {
      return 'blank entries are not allowed'
    }

    return true
  },
}

export const imageFileValidator = {
  validate: (files) => {
    console.info('File size: ', files.length && files[0].size)

    if (!files.length) {
      return true // if there are no files, don't validate anything here
    }

    if (files[0].size > 8000000) {
      return 'file must be no larger than 8MB'
    }

    if (!['application/pdf', 'image/png', 'image/jpeg'].includes(files[0].type)) {
      return 'only PNG, JPG/JPEG, and PDF files are allowed'
    }

    return true
  },
}

export const futureDateValidator = {
  validate: (value) => {
    if (new Date(value) < Date.now()) {
      return 'dates in the past are not allowed'
    }

    if (new Date(value) > new Date('2032-01-01')) {
      return 'date is too far into the future'
    }

    return true
  },
}

export const pastDateValidator = {
  validate: (value) => {
    if (new Date(value) > Date.now()) {
      return 'dates in the future are not allowed'
    }

    if (new Date(value) < new Date('2022-01-01')) {
      return 'date is too far in the past'
    }

    return true
  },
}

export const imagesDocsSpreadsheetsFileValidator = {
  validate: (files) => {
    console.info('File size: ', files.length && files[0].size)

    if (!files.length) {
      return true // if there are no files, don't validate anything here
    }

    if (files[0].size > 8000000) {
      return 'file must be no larger than 8MB'
    }

    if (!['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf', 'image/png', 'image/jpeg'].includes(files[0].type)) {
      return 'only DOC/DOCX, XLS/XLSX, PNG, JPG/JPEG, and PDF files are allowed'
    }

    return true
  },
}

export const statusValidator = {
  pattern: {
    value: /^(DEFEATED|MEETING|SMILING)$/,
    message: 'Must be "DEFEATED", "MEETING", or "SMILING"',
  },
}

export const userIDValidator = {
  maxLength: 30,
  minLength: 3,
  pattern: {
    value: /^[0-9A-Za-z._]*$/,
    message: 'letters, numbers, _ and . only',
  },
}

export const agentCodeValidator = {
  pattern: {
    value: /^[0-9A-Za-z]{5}$/,
    message: 'must be 5 alphanumeric characters',
  },
}

export const officeCodeValidator = {
  pattern: {
    value: /^[0-9A-Za-z]{3}$/,
    message: 'must be 3 alphanumeric characters',
  },
}

export const lastFourValidator = {
  pattern: {
    value: /^[0-9]{4}$/,
    message: 'must be 4 numeric digits',
  },
}

export const phoneValidator = {
  pattern: {
    value: /^[0-9]{10}$/,
    message: 'must be 10 digits, no punctuation',
  },
}

export const property2Validator = {
  required: true,
  maxLength: 256,
  minLength: 5,
  pattern: {
    value: /^[A-Z]*$/,
    message: 'Must be upper case letters only',
  },
}

export const
  makeRequired = (validator) => {
    if (validator) {
      return {...validator, required: true}
    }

    return {...noBlanksValidator, required: true}
  }

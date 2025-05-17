import * as API from 'api/api'

const generateFormDataClass = (data) => {
  let formData = new FormData()

  for (let prop in data) {
    if (data.hasOwnProperty(prop)) {
      if (data[prop] instanceof FileList) { // file select field
        if (data[prop][0]) { // actually has a file chosen
          formData.append(prop, data[prop][0], data[prop][0].name)
        } // skip field entirely if it is a file selector with no files
      } else {
        formData.append(prop, data[prop]) // regular field
      }
    }
  }

  return formData
}

/***
 *
 * @param {Object} formData A JavaScript FormData object
 * @param {string} formName Name of the form being saved
 * @param {function} setFormError A function to pass an error to (for failures)
 * @param {function} setFormSuccess A function to set form success with (for failures)
 * @returns {Promise<FormData>}
 */
export const saveSubmissionToMongo = async(formData, formName, setFormError, setFormSuccess) => {
  let submissionDocument

  let newFormData = generateFormDataClass(formData)

  try {
    submissionDocument = await API.saveToMongo(formName, newFormData)

    newFormData = submissionDocument.data.formData

    submissionDocument.data.files.forEach(file => {
      newFormData[file.fieldName] = file.url
    })
  } catch (error) {
    console.error('Failed to persist to MongoDB:', error)
    setFormError(error)
    setFormSuccess(false)
  }

  return newFormData
}

/***
 * @param {Object}      params
 * @param {Object}      params.user                     Security Context user object (name, user ID, etc)
 * @param {Function}    params.setFormDisabled          Function for setting form state to disabled
 * @param {Function}    params.setFormError             Function for setting form error
 * @param {Function}    params.setFormSuccess           Function for setting form success state
 * @param {String}      [params.domain]                 The security domain for the form, will be matched against Persona property "HumanResources" maps to "isHumanResources" in Persona.
 * @param {String}      params.formName                 Name of the form
 * @param {String}      params.templateID               Mailer service template ID
 * @param {String}      [params.confirmationTemplateID] Mailer service template ID for confirmation email, if any
 * @param {String}      [params.fromAddress]            Email address to use for return addresses
 * @param {Boolean}     [params.saveToMongo]            Save to mongo as well as mailer service
 * @returns {(function(*=): Promise<void>)|*}
 */
export const generateSubmitFormHandler = ({domain, user, setFormDisabled, setFormError, setFormSuccess, formName, templateID, confirmationTemplateID = null, saveToMongo = false}, customFommDataProcessor) => {
  if (!user || !setFormDisabled || !setFormError || !setFormSuccess || !formName || !templateID || !domain) {
    throw (new Error('Missing parameter when calling generateSubmitFormHandler()'))
  }

  if (domain[0] !== domain[0].toUpperCase() || domain[1] !== domain[1].toLowerCase()) {
    throw (new Error('Domain must be in upper camel case style (ie. MyDomain or MailRoom).'))
  }

  return async(formData) => {
    let errorState = false

    setFormDisabled(true)

    formData = {'_formName': formName, domain, ...formData}

    if (customFommDataProcessor) {
      formData = customFommDataProcessor(formData)
    }

    formData.submitterEmail = user.email
    formData.submitterFullName = user.fullName
    formData.submitterUserID = user.id // Hah! Thought you could just edit the DOM directly, did you?

    // test
    if (saveToMongo) {
      try {
        formData = await saveSubmissionToMongo(formData, formName, setFormError, setFormSuccess) // this returns a new FormData with image URLs replacing any images
      } catch (error) {
        errorState = true
        setFormError(error)
        setFormSuccess(false)
        console.error('Failed to save data to database: ', error)
      }
    }

    if (!errorState) {
      try {
        await API.postFormData(formData, templateID)
        setFormError(null)
        setFormSuccess(true)
      } catch (error) {
        errorState = true
        setFormError(error)
        setFormSuccess(false)
        console.error('Failed to email form data: ', error)
      }
    }

    if (!errorState && confirmationTemplateID) {
      try {
        API.postFormData(formData, confirmationTemplateID, formData.submitterEmail)
      } catch (error) {
        console.error('Failed to send confirmation email: ', error)
      }
    }

    setFormDisabled(false)
  }
}

export const requestItems = async(apiCall, query, setItems, setTotalItems) => {
  let response = {}

  try {
    response = await apiCall(query)

    setItems(response.data)

    if (response.data) {
      setTotalItems(response.data.length)
    }
  } catch (error) {
    console.error(`Failed to retrieve items: ${error}`)
  }
}

export const requestItem = async(apiCall, query, setItem = () => {}, resetForm = () => {}) => {
  let response = {}

  try {
    response = await apiCall(query)
    setItem(response.data)
    resetForm(response.data)

    return response.data
  } catch (error) {
    console.error(`Failed to retrieve item ${query}: ${error}`)
    throw new Error(error)
  }
}

export const updateItem = async(apiCall, formData, setLoading, setError, setItem, setItemSuccess, setDisabled) => {
  let response = {}

  setLoading(true)

  try {
    response = await apiCall(formData)
    setItem(response.data)
    setItemSuccess(response.data)
    setTimeout(() => { setItemSuccess(false) }, 200)
    setDisabled(true)
    setError(null)
  } catch (error) {
    console.error('Failed to update item:', error)
    setError(error)
  }

  setLoading(false)
}

export const saveNewItem = async(apiCall, formData, setLoading, setError, setItemSuccess) => {
  let response

  setLoading(true)
  setError(null)

  try {
    response = await apiCall(formData)
    setItemSuccess(response.data)
    setTimeout(() => { setItemSuccess(false) }, 200)
  } catch (error) {
    console.error('Failed to save item:', error)
    setError(error)
    throw new Error(error)
  }

  setLoading(false)

  return response
}

export const stripTime = (dateTime) => {
  return dateTime.substr(0, 10)
}

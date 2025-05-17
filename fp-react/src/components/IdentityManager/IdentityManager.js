import React, {useContext} from 'react'

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import ChatContext from 'context/chat.context'

const IdentityManager = (props) => {
    const {identity, setIdentity, cannedIdentities} = useContext(ChatContext)
    return (
        <Box sx={{
            '& .MuiTextField-root': { m: 1, width: '25ch' },
          }}>
             <Autocomplete
                value={identity}
                onChange={(event, newValue) => {
                    setIdentity(newValue);
                  }}
                disablePortal
                id="combo-box-demo"
                options={cannedIdentities}
                
                renderInput={(params) => <TextField {...params} label="Identity" />}
            />
        </Box>
    )
}
export default IdentityManager;
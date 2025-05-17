import Box from '@mui/material/Box';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';


/**
 * Header component. Used example https://mui.com/material-ui/react-table/#system-EnhancedTable.js 
 * as basis.
 */
const TableHeader = (props) => {
    const {headers, order, orderBy, onRequestSort} = props;

    const createSortHandler = (property) => (event) => {
        onRequestSort(event, property);
      };
    
    const headerStyle = {
        color: "#fff",  
        backgroundColor: "#37474f", 
        textAlign: "center",
        '&:hover': {
            backgroundColor: "#37474f", // Keep the same background color on hover
            color: "#fff",  
        }
    }

    return (
        <TableHead>
            <TableRow key="header">
                {headers.map((headCell) => (
                    <TableCell 
                        key={headCell.id} 
                        sortDirection={orderBy === headCell.id ? order :  false}
                        sx={{textAlign: "center"}}
                        className='TableHeader'
                    >
                        <TableSortLabel
                            
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order : 'asc'}
                            onClick={createSortHandler(headCell.id)}
                            sx={{color: '#fff', '&:hover': {
                                color: '#fff'
                            }}}
                            classes={{color:'#ff'}}
                            className='CustSortLabel'
                        >
                            {headCell.label}
                            {orderBy === headCell.id ? (
                                <Box component="span" sx={visuallyHidden}>
                                {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                                </Box>
                            ) : null}
                        </TableSortLabel>

                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    )
}

export default TableHeader;
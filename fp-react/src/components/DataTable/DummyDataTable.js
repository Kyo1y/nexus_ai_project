import DataTable from 'components/DataTable/DataTable'
import TableHeader from 'components/DataTable/TableHeader'

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Paper from '@mui/material/Paper';

const DummyDataTable = () => {
    const data = [
        {"AgentCode": "1018E", "name": "Corey House", "count_pid": 1, key: 1},
        {"AgentCode": "1788C", "name": "Max Leopold", "count_pid": 2, key: 2},
        {"AgentCode": "1828E", "name": "Anthony Vincent", "count_pid": 1, key: 3},
        {"AgentCode": "1836E", "name": "Mark Herschlag", "count_pid": 4, key: 4},
        {"AgentCode": "1858E", "name": "Nicolas Rodriguez", "count_pid": 3, key: 5},
        {"AgentCode": "1965D", "name": "Richard Vazquez", "count_pid": 2, key: 6},
        {"AgentCode": "2122E", "name": "David Waters", "count_pid": 4, key: 7}
    ]
    const headers = [
        {
            id: 'AgentCode',
            label: 'Agent Code'
        },
        {
            id: 'name',
            label: 'Name'
        },
        {
            id: 'count_pid',
            label: 'Total Policy Count'
        }
    ]

    return (
        <DataTable 
            data={data}
            headers={headers}
        />
        
     );
}

export default DummyDataTable
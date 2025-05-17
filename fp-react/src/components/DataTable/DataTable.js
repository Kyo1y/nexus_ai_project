import React, { useState } from 'react';

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Paper from '@mui/material/Paper';

import TableHeader from 'components/DataTable/TableHeader'

const DataTable = (props) => {
    const {data, headers} = props;

    const [order, setOrder] = React.useState('asc');
    const [orderBy, setOrderBy] = React.useState('calories');

    function lastWord(word) {
      // Remove content within parentheses
      let stringWithoutParentheses = word.replace(/\([^()]*\)/g, '');

      // Remove any trailing spaces
      stringWithoutParentheses = stringWithoutParentheses.trim();
      
      // Split the input string by spaces
      let words = stringWithoutParentheses.split(" ");

      // Return the last word
      return words[words.length - 1];
    }

    function descendingComparator(a, b, orderBy) {
      let aValue;
      let bValue;
      if (orderBy === 'Name') {
        aValue = lastWord(a[orderBy]);
        bValue = lastWord(b[orderBy]);
      }
      else {
        aValue = a[orderBy];
        bValue = b[orderBy]
      }
        if (bValue < aValue) {
          return -1;
        }
        if (bValue > aValue) {
          return 1;
        }
        return 0;
      }
      
      function getComparator(order, orderBy) {
        return order === 'desc'
          ? (a, b) => descendingComparator(a, b, orderBy)
          : (a, b) => -descendingComparator(a, b, orderBy);
      }
      
      // Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
      // stableSort() brings sort stability to non-modern browsers (notably IE11). If you
      // only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
      // with exampleArray.slice().sort(exampleComparator)
      function stableSort(array, comparator) {
        const stabilizedThis = array.map((el, index) => [el, index]);
        stabilizedThis.sort((a, b) => {
          const order = comparator(a[0], b[0]);
          if (order !== 0) {
            return order;
          }
          return a[1] - b[1];
        });
        return stabilizedThis.map((el) => el[0]);
      }

    const handleRequestSort = (event, property) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    // const columns = Object.keys(data[0]);
    const columns = headers.map((item) => item.id)

    const sortedData = React.useMemo(
        () => stableSort(data, getComparator(order, orderBy)),
        [order, orderBy]
    )

  return (
    <TableContainer>
            <Table>
                <TableHeader
                    headers={headers}
                    order={order}
                    orderBy={orderBy}
                    onRequestSort={handleRequestSort}
                >
                </TableHeader>
                <TableBody>
                    {sortedData.map((row) => (
                        <TableRow key={row['key']}>
                            {columns.map((colName) => (
                                <TableCell key={colName}>{row[colName]}</TableCell>
                            ))}

                        </TableRow>
                        
                    )) }
                </TableBody>
            </Table>
        </TableContainer>
  );
};

export default DataTable;

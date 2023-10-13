import React from "react";
import styled, { css } from "styled-components";
import { useTable, usePagination, useSortBy, useGlobalFilter } from "react-table";
import AppColors from "../styles/colors";
import { FaSortAmountUp, FaSortAmountDown } from "react-icons/fa";
import { BiFirstPage, BiLastPage } from "react-icons/bi";
import { MdKeyboardArrowLeft, MdKeyboardArrowRight } from "react-icons/md";
import { sharedButtonStyle, sharedFlexCenter, sharedFlexSpaceBetween } from "../styles/global";
import Input from "./Input";

interface TableProps {
  title: string;
  data: any[];
  columns: any[];
  id?: string;
}

const Table: React.FC<TableProps> = ({ title, data, columns, id }) => {

  const tableInstance = useTable(
    {
      columns: columns,
      data: data,
      initialState: { pageIndex: 0, pageSize: 5 }
    },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const {
    getTableProps, // table props from react-table
    headerGroups, // headerGroups, if your table has groupings
    getTableBodyProps, // table body props from react-table
    prepareRow, // Prepare the row (this function needs to be called for each row before getting the row props)
    footerGroups,
    state,
    setGlobalFilter,
    page, // use, page or rows
    nextPage,
    previousPage,
    canNextPage,
    canPreviousPage,
    pageOptions,
    gotoPage,
    pageCount,
    setPageSize
  } = tableInstance;

  const { globalFilter, pageIndex, pageSize } = state;

  return (
    <>
      <HeaderContainer>
      <Search>
      Search:{" "}
      <Input value={globalFilter || ""} onChangeHandler={(value : any) => setGlobalFilter(value)} inputStyle={searchInputStyle}/>
      </Search>
      <SelectContainer
          value={pageSize}
          onChange={(e) => setPageSize(Number(e.target.value))}
          // size={2}
        >
          {[5, 10, 15].map((pageSize) => (
            <OptionTag key={pageSize} value={pageSize}>
              {pageSize !== 15 ? `Show ${pageSize}` : `Show all`}
            </OptionTag>
          ))}
        </SelectContainer>
        </HeaderContainer>
      <Container>
      <TableView {...getTableProps()} id={id}>
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <ColumnHeader {...column.getHeaderProps(column.getSortByToggleProps())}>
                  {column.render("Header")}
                  <span>
                    {column.isSorted
                      ? column.isSortedDesc
                        ? <FaSortAmountDown size={16} />
                        : <FaSortAmountUp size={16} />
                      : ""}
                  </span>
                </ColumnHeader>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map((row) => {
            prepareRow(row);
            return (
              <TableRow {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <TableCell {...cell.getCellProps()}>{cell.render("Cell")}</TableCell>
                  );
                })}
              </TableRow>
            );
          })}
        </tbody>
      </TableView>
      </Container>
      <Pagination>
        <span>
          Page&nbsp;
          <strong>
            {pageIndex + 1} of {pageOptions.length}
          </strong>{" "}
        </span>
        <BtnContainer>
          <PaginationBtn onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
            <BiFirstPage  size={20} />
          </PaginationBtn>{" "}
          <PaginationBtn onClick={() => previousPage()} disabled={!canPreviousPage}>
            <MdKeyboardArrowLeft  size={20} />
          </PaginationBtn>{" "}
          <PaginationBtn onClick={() => nextPage()} disabled={!canNextPage}>
            <MdKeyboardArrowRight  size={20} />
          </PaginationBtn>{" "}
          <PaginationBtn
            onClick={() => gotoPage(pageCount - 1)}
            disabled={!canNextPage}
          >
            <BiLastPage  size={20} />
          </PaginationBtn>{" "}
        </BtnContainer>
      </Pagination>
    </>
  );
};

export default React.memo(Table);

const TableView = styled.table`
  width: 100%;
  border-spacing: 0;
`;
const ColumnHeader = styled.th`
  background: ${AppColors.ThemeLightestPurple};
  padding: 1rem;
  border-bottom: 1px solid #1a1a1a;
  font-weight: bold;
  text-align: center;
`;
const TableCell = styled.td`
  padding: 1rem;
  text-align: center;
`;
const TableRow = styled.tr`
  &:nth-child(2n) {
    background: ${AppColors.ThemeBlueShadow};
  }
`;

const Container = styled.div`
  height: 25rem;
  overflow: scroll;
  `

const Pagination = styled.div`
margin: 2rem;
${sharedFlexCenter}
justify-content: flex-end;
`

const PaginationBtn = styled.button`
    font-weight: 700;
    padding: 0.5rem;
`

const Search = styled.div`
  display:flex;
  align-items: center;
  margin: 2rem 1rem;
  font-weight: 600;
  width:100%;
`
const searchInputStyle = css`
  width: 30%;
  margin-left: 1rem;
`

const HeaderContainer = styled.div`
${sharedFlexSpaceBetween}
`

const SelectContainer = styled.select`
  padding: 0.5rem;
  font-size: 1rem;
`

const OptionTag = styled.option`
  background: ${AppColors.ThemeBlue};
  padding:  0.5rem;
  font-size: 1rem;
`

const BtnContainer = styled.div`
  margin-left: 1rem;
`

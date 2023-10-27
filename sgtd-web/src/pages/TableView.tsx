import React, { useRef } from "react";
import Layout from "../components/Layout";
import Table from "../components/Table";
import styled, { css } from "styled-components";
import Button from "../components/Button";
import { sharedButtonStyle, sharedFlexCenter } from "../styles/global";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { CSVLink } from "react-csv";
import AppColors from "../styles/colors";
import { Slide, ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { PDFColumns, columns, tableData } from "../lib/dummyData";

function TableView() {
  const tableRef = useRef(null);

  const exportToPDF = () => {
    const unit = "pt";
    const size = "A4";
    const orientation = "portrait";

    const marginLeft = 40;
    const doc = new jsPDF(orientation, unit, size);

    doc.setFontSize(15);

    const title = "Table Title";
    doc.text(title, marginLeft, 25);
    autoTable(doc, {
      body: [...tableData],
      columns: PDFColumns,
    });
    doc.save("report.pdf");
  };

  const csvData = [
    ["INDEX", "Due To Arrive Time", "locationFrom", "Vessel Name", "Call Sign", "IMO number","Flag", "Due To Depart Time"],
    ...tableData.map(({ index, duetoArriveTime, locationFrom, vesselName, callSign, IMOnumber, flag,dueToDepartTime }) => [
      index + 1,
      duetoArriveTime,
      locationFrom,
      vesselName,
      callSign,
      IMOnumber,
      flag,
      dueToDepartTime
    ]),
  ];

  const copyTable = () => {
    const elTable = document.querySelector("table");
    let range, sel;
    if (document.createRange && window.getSelection) {
      range = document.createRange();
      sel = window.getSelection();
      sel && sel.removeAllRanges();
      if (elTable && sel) {
        try {
          range.selectNodeContents(elTable);
          sel.addRange(range);
        } catch (e) {
          range.selectNode(elTable);
          sel.addRange(range);
        }
      }
      document.execCommand("copy");
    }

    sel && sel.removeAllRanges();

    toast.success("Copied to clipboard!!");
  };

  return (
    <Layout>
      <Section>
        <ToastContainer
          position="bottom-right"
          autoClose={2000}
          transition={Slide}
        />
        <BtnContainer>
          <Button
            title={"PDF"}
            clickHandler={exportToPDF}
            buttonStyle={btnStyle}
          />

          <StyledCSVLink filename="my-file.csv" data={csvData}>
            CSV
          </StyledCSVLink>
          <Button
            title={"COPY"}
            clickHandler={copyTable}
            buttonStyle={btnStyle}
          />
        </BtnContainer>
        <TableContainer ref={tableRef}>
          <Table
            title={"Table view"}
            data={tableData}
            columns={columns}
            id={"my-table"}
          />
        </TableContainer>
      </Section>
    </Layout>
  );
}

export default TableView;

const TableContainer = styled.div`
  width: 90%;
`;

const Section = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 90%;
  align-items: center;
`;

const BtnContainer = styled.div`
  margin: 1rem;
  align-self: flex-end;
  ${sharedFlexCenter};
  justify-content: flex-end;
`;

const btnStyle = css`
  ${sharedButtonStyle}
  width: 5rem;
  margin: 0 0.5rem;
`;

const StyledCSVLink = styled(CSVLink)`
  display: block;
  font-weight: 600;
  border-radius: 0.25rem;
  ${btnStyle}
  text-decoration: none;
  font-size: 0.8rem;
  color: ${AppColors.White};
  cursor: pointer;
  text-align: center;
`;

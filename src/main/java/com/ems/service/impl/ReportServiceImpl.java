package com.ems.service.impl;

import com.ems.dto.ReportFilterDTO;
import com.ems.entity.Attendance;
import com.ems.entity.Employee;
import com.ems.entity.Salary;
import com.ems.repository.AttendanceRepository;
import com.ems.repository.DepartmentRepository;
import com.ems.repository.EmployeeRepository;
import com.ems.repository.SalaryRepository;
import com.ems.service.ReportService;
import com.lowagie.text.Document;
import com.lowagie.text.Element;
import com.lowagie.text.Font;
import com.lowagie.text.PageSize;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfWriter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Service;

import java.awt.Color;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class ReportServiceImpl implements ReportService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;
    private final AttendanceRepository attendanceRepository;
    private final SalaryRepository salaryRepository;

    @Override
    public ByteArrayInputStream generateExcelReport(ReportFilterDTO filter) {
        String reportType = filter.getReportType() != null ? filter.getReportType().toUpperCase() : "EMPLOYEE";

        try (Workbook workbook = new XSSFWorkbook(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            Sheet sheet = workbook.createSheet(reportType + " Report");

            // Header Style
            CellStyle headerStyle = workbook.createCellStyle();
            headerStyle.setFillForegroundColor(IndexedColors.ROYAL_BLUE.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            org.apache.poi.ss.usermodel.Font font = workbook.createFont();
            font.setColor(IndexedColors.WHITE.getIndex());
            font.setBold(true);
            headerStyle.setFont(font);

            int rowIdx = 0;
            Row headerRow = sheet.createRow(rowIdx++);

            switch (reportType) {
                case "ATTENDANCE":
                    String[] attHeaders = {"ID", "Employee Code", "Name", "Department", "Date", "Check-In", "Check-Out", "Hours", "Status"};
                    for (int col = 0; col < attHeaders.length; col++) {
                        Cell cell = headerRow.createCell(col);
                        cell.setCellValue(attHeaders[col]);
                        cell.setCellStyle(headerStyle);
                    }
                    List<Attendance> attendances = attendanceRepository.findAll();
                    for (Attendance att : attendances) {
                        Row row = sheet.createRow(rowIdx++);
                        row.createCell(0).setCellValue(att.getId());
                        row.createCell(1).setCellValue(att.getEmployee().getEmployeeCode());
                        row.createCell(2).setCellValue(att.getEmployee().getFullName());
                        row.createCell(3).setCellValue(att.getEmployee().getDepartment() != null ? att.getEmployee().getDepartment().getName() : "N/A");
                        row.createCell(4).setCellValue(att.getAttendanceDate().toString());
                        row.createCell(5).setCellValue(att.getCheckInTime() != null ? att.getCheckInTime().toString() : "-");
                        row.createCell(6).setCellValue(att.getCheckOutTime() != null ? att.getCheckOutTime().toString() : "-");
                        row.createCell(7).setCellValue(att.getWorkHours() != null ? att.getWorkHours() : 0.0);
                        row.createCell(8).setCellValue(att.getStatus().name());
                    }
                    break;

                case "SALARY":
                    String[] salHeaders = {"ID", "Code", "Name", "Pay Month", "Basic", "HRA", "DA", "Bonus", "Incentives", "Deductions", "Tax", "Net Salary", "Status"};
                    for (int col = 0; col < salHeaders.length; col++) {
                        Cell cell = headerRow.createCell(col);
                        cell.setCellValue(salHeaders[col]);
                        cell.setCellStyle(headerStyle);
                    }
                    List<Salary> salaries = salaryRepository.findAll();
                    for (Salary sal : salaries) {
                        Row row = sheet.createRow(rowIdx++);
                        row.createCell(0).setCellValue(sal.getId());
                        row.createCell(1).setCellValue(sal.getEmployee().getEmployeeCode());
                        row.createCell(2).setCellValue(sal.getEmployee().getFullName());
                        row.createCell(3).setCellValue(sal.getPayMonth());
                        row.createCell(4).setCellValue(sal.getBasicSalary().doubleValue());
                        row.createCell(5).setCellValue(sal.getHra() != null ? sal.getHra().doubleValue() : 0);
                        row.createCell(6).setCellValue(sal.getDa() != null ? sal.getDa().doubleValue() : 0);
                        row.createCell(7).setCellValue(sal.getBonus() != null ? sal.getBonus().doubleValue() : 0);
                        row.createCell(8).setCellValue(sal.getIncentives() != null ? sal.getIncentives().doubleValue() : 0);
                        row.createCell(9).setCellValue(sal.getDeductions() != null ? sal.getDeductions().doubleValue() : 0);
                        row.createCell(10).setCellValue(sal.getTax() != null ? sal.getTax().doubleValue() : 0);
                        row.createCell(11).setCellValue(sal.getNetSalary().doubleValue());
                        row.createCell(12).setCellValue(sal.getPaymentStatus().name());
                    }
                    break;

                case "EMPLOYEE":
                default:
                    String[] empHeaders = {"ID", "Employee Code", "Full Name", "Email", "Mobile", "Gender", "Department", "Role", "Joining Date", "Status"};
                    for (int col = 0; col < empHeaders.length; col++) {
                        Cell cell = headerRow.createCell(col);
                        cell.setCellValue(empHeaders[col]);
                        cell.setCellStyle(headerStyle);
                    }
                    List<Employee> employees = employeeRepository.findAll();
                    for (Employee emp : employees) {
                        Row row = sheet.createRow(rowIdx++);
                        row.createCell(0).setCellValue(emp.getId());
                        row.createCell(1).setCellValue(emp.getEmployeeCode());
                        row.createCell(2).setCellValue(emp.getFullName());
                        row.createCell(3).setCellValue(emp.getEmail());
                        row.createCell(4).setCellValue(emp.getMobileNumber());
                        row.createCell(5).setCellValue(emp.getGender());
                        row.createCell(6).setCellValue(emp.getDepartment() != null ? emp.getDepartment().getName() : "N/A");
                        row.createCell(7).setCellValue(emp.getRole() != null ? emp.getRole().getName() : "N/A");
                        row.createCell(8).setCellValue(emp.getJoiningDate().toString());
                        row.createCell(9).setCellValue(emp.getEmploymentStatus().name());
                    }
                    break;
            }

            for (int i = 0; i < 12; i++) {
                sheet.autoSizeColumn(i);
            }

            workbook.write(out);
            return new ByteArrayInputStream(out.toByteArray());
        } catch (Exception e) {
            log.error("Error generating Excel report", e);
            throw new RuntimeException("Failed to export Excel report: " + e.getMessage());
        }
    }

    @Override
    public ByteArrayInputStream generatePdfReport(ReportFilterDTO filter) {
        String reportType = filter.getReportType() != null ? filter.getReportType().toUpperCase() : "EMPLOYEE";
        Document document = new Document(PageSize.A4.rotate());
        ByteArrayOutputStream out = new ByteArrayOutputStream();

        try {
            PdfWriter.getInstance(document, out);
            document.open();

            // Title
            Font titleFont = new Font(Font.HELVETICA, 18, Font.BOLD, new Color(37, 99, 235));
            Paragraph title = new Paragraph("Employee Management System - " + reportType + " REPORT", titleFont);
            title.setAlignment(Element.ALIGN_CENTER);
            title.setSpacingAfter(15);
            document.add(title);

            Font subFont = new Font(Font.HELVETICA, 10, Font.ITALIC, Color.GRAY);
            Paragraph sub = new Paragraph("Generated on: " + LocalDate.now(), subFont);
            sub.setAlignment(Element.ALIGN_RIGHT);
            sub.setSpacingAfter(15);
            document.add(sub);

            Font headFont = new Font(Font.HELVETICA, 10, Font.BOLD, Color.WHITE);

            switch (reportType) {
                case "ATTENDANCE":
                    PdfPTable attTable = new PdfPTable(8);
                    attTable.setWidthPercentage(100);
                    String[] attHeaders = {"Code", "Name", "Department", "Date", "Check-In", "Check-Out", "Hours", "Status"};
                    for (String h : attHeaders) {
                        PdfPCell cell = new PdfPCell(new Phrase(h, headFont));
                        cell.setBackgroundColor(new Color(37, 99, 235));
                        cell.setPadding(6);
                        attTable.addCell(cell);
                    }
                    for (Attendance att : attendanceRepository.findAll()) {
                        attTable.addCell(att.getEmployee().getEmployeeCode());
                        attTable.addCell(att.getEmployee().getFullName());
                        attTable.addCell(att.getEmployee().getDepartment() != null ? att.getEmployee().getDepartment().getName() : "N/A");
                        attTable.addCell(att.getAttendanceDate().toString());
                        attTable.addCell(att.getCheckInTime() != null ? att.getCheckInTime().toString() : "-");
                        attTable.addCell(att.getCheckOutTime() != null ? att.getCheckOutTime().toString() : "-");
                        attTable.addCell(String.valueOf(att.getWorkHours()));
                        attTable.addCell(att.getStatus().name());
                    }
                    document.add(attTable);
                    break;

                case "SALARY":
                    PdfPTable salTable = new PdfPTable(8);
                    salTable.setWidthPercentage(100);
                    String[] salHeaders = {"Code", "Name", "Month", "Basic", "Bonus", "Tax", "Net Salary", "Status"};
                    for (String h : salHeaders) {
                        PdfPCell cell = new PdfPCell(new Phrase(h, headFont));
                        cell.setBackgroundColor(new Color(37, 99, 235));
                        cell.setPadding(6);
                        salTable.addCell(cell);
                    }
                    for (Salary sal : salaryRepository.findAll()) {
                        salTable.addCell(sal.getEmployee().getEmployeeCode());
                        salTable.addCell(sal.getEmployee().getFullName());
                        salTable.addCell(sal.getPayMonth());
                        salTable.addCell("$" + sal.getBasicSalary().toString());
                        salTable.addCell("$" + (sal.getBonus() != null ? sal.getBonus().toString() : "0.00"));
                        salTable.addCell("$" + (sal.getTax() != null ? sal.getTax().toString() : "0.00"));
                        salTable.addCell("$" + sal.getNetSalary().toString());
                        salTable.addCell(sal.getPaymentStatus().name());
                    }
                    document.add(salTable);
                    break;

                case "EMPLOYEE":
                default:
                    PdfPTable empTable = new PdfPTable(8);
                    empTable.setWidthPercentage(100);
                    String[] empHeaders = {"Code", "Full Name", "Email", "Mobile", "Department", "Role", "Joined", "Status"};
                    for (String h : empHeaders) {
                        PdfPCell cell = new PdfPCell(new Phrase(h, headFont));
                        cell.setBackgroundColor(new Color(37, 99, 235));
                        cell.setPadding(6);
                        empTable.addCell(cell);
                    }
                    for (Employee emp : employeeRepository.findAll()) {
                        empTable.addCell(emp.getEmployeeCode());
                        empTable.addCell(emp.getFullName());
                        empTable.addCell(emp.getEmail());
                        empTable.addCell(emp.getMobileNumber());
                        empTable.addCell(emp.getDepartment() != null ? emp.getDepartment().getName() : "N/A");
                        empTable.addCell(emp.getRole() != null ? emp.getRole().getName() : "N/A");
                        empTable.addCell(emp.getJoiningDate().toString());
                        empTable.addCell(emp.getEmploymentStatus().name());
                    }
                    document.add(empTable);
                    break;
            }

            document.close();
            return new ByteArrayInputStream(out.toByteArray());
        } catch (Exception e) {
            log.error("Error generating PDF report", e);
            throw new RuntimeException("Failed to export PDF report: " + e.getMessage());
        }
    }
}

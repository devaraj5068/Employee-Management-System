package com.ems.controller;

import com.ems.dto.ReportFilterDTO;
import com.ems.service.DepartmentService;
import com.ems.service.ReportService;
import com.ems.service.RoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;

import java.io.ByteArrayInputStream;

@Controller
@RequestMapping("/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;
    private final DepartmentService departmentService;
    private final RoleService roleService;

    @GetMapping
    public String reportsIndex(Model model) {
        model.addAttribute("filter", new ReportFilterDTO());
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("roles", roleService.getAllRoles());
        return "reports/index";
    }

    @GetMapping("/export/excel")
    public ResponseEntity<InputStreamResource> exportExcel(@ModelAttribute ReportFilterDTO filter) {
        ByteArrayInputStream stream = reportService.generateExcelReport(filter);
        String filename = (filter.getReportType() != null ? filter.getReportType() : "Employee") + "_Report.xlsx";

        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Disposition", "attachment; filename=" + filename);

        return ResponseEntity.ok()
                .headers(headers)
                .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(new InputStreamResource(stream));
    }

    @GetMapping("/export/pdf")
    public ResponseEntity<InputStreamResource> exportPdf(@ModelAttribute ReportFilterDTO filter) {
        ByteArrayInputStream stream = reportService.generatePdfReport(filter);
        String filename = (filter.getReportType() != null ? filter.getReportType() : "Employee") + "_Report.pdf";

        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Disposition", "attachment; filename=" + filename);

        return ResponseEntity.ok()
                .headers(headers)
                .contentType(MediaType.APPLICATION_PDF)
                .body(new InputStreamResource(stream));
    }
}

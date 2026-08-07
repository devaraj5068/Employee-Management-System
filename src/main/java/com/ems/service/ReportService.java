package com.ems.service;

import com.ems.dto.ReportFilterDTO;

import java.io.ByteArrayInputStream;

public interface ReportService {
    ByteArrayInputStream generateExcelReport(ReportFilterDTO filter);
    ByteArrayInputStream generatePdfReport(ReportFilterDTO filter);
}

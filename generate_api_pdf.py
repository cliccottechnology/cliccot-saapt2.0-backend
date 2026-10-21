import os
import subprocess
from pathlib import Path

BASE_DIR = Path(r"D:\SAAPT 2.0")
HTML_FILE = BASE_DIR / "api_collection.html"
PDF_FILE = BASE_DIR / "SAAPT_2.0_API_Collection.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SAAPT 2.0 - Action-Based REST API Collection</title>
<style>
  @page {
    size: A4;
    margin: 15mm 15mm 15mm 15mm;
    @bottom-right {
      content: counter(page);
    }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 11pt;
    line-height: 1.5;
  }
  .page-break {
    page-break-before: always;
  }
  
  /* Cover Page */
  .cover {
    height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 40px 30px;
    border: 2px solid #2563eb;
    border-radius: 16px;
    background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
  }
  .cover-header {
    border-bottom: 3px solid #2563eb;
    padding-bottom: 24px;
  }
  .cover-badge {
    display: inline-block;
    padding: 6px 14px;
    background: #2563eb;
    color: #ffffff;
    font-size: 11pt;
    font-weight: 700;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
  }
  .cover-title {
    font-size: 32pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin-bottom: 12px;
  }
  .cover-subtitle {
    font-size: 15pt;
    color: #475569;
    font-weight: 400;
  }
  .cover-info {
    margin: 40px 0;
  }
  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    background: #ffffff;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
  }
  .info-item {
    font-size: 10.5pt;
  }
  .info-label {
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    font-size: 9pt;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .info-val {
    color: #0f172a;
    font-weight: 600;
  }
  .cover-footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 16px;
    display: flex;
    justify-content: space-between;
    font-size: 9.5pt;
    color: #64748b;
  }

  /* Section Headers */
  .section-header {
    background: #0f172a;
    color: #ffffff;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .section-title {
    font-size: 16pt;
    font-weight: 700;
  }
  .section-badge {
    background: #3b82f6;
    color: #fff;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 9pt;
    font-weight: 600;
  }

  /* API Card */
  .api-card {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-bottom: 24px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    page-break-inside: avoid;
    overflow: hidden;
  }
  .api-card-header {
    padding: 12px 18px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }
  .api-endpoint {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
  }
  .method {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 9pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #ffffff;
  }
  .method-post { background: #16a34a; }
  .method-get { background: #2563eb; }
  .method-put { background: #d97706; }
  .method-patch { background: #ea580c; }
  .method-delete { background: #dc2626; }

  .api-meta {
    display: flex;
    gap: 8px;
  }
  .meta-tag {
    font-size: 8.5pt;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
  }
  .meta-auth-yes { background: #fee2e2; color: #991b1b; }
  .meta-auth-no { background: #dcfce7; color: #166534; }
  .meta-format { background: #f1f5f9; color: #475569; }

  .api-card-body {
    padding: 16px 18px;
  }
  .api-desc {
    color: #475569;
    font-size: 10.5pt;
    margin-bottom: 14px;
  }
  
  .block-title {
    font-size: 9.5pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 14px;
    font-size: 9.5pt;
  }
  th {
    background: #f1f5f9;
    color: #334155;
    text-align: left;
    padding: 6px 10px;
    border: 1px solid #cbd5e1;
    font-weight: 600;
  }
  td {
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
    color: #1e293b;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }
  .field-name {
    font-family: 'Consolas', monospace;
    font-weight: 600;
    color: #2563eb;
  }
  .field-type {
    font-family: 'Consolas', monospace;
    font-size: 8.5pt;
    color: #64748b;
  }
  .field-req {
    color: #dc2626;
    font-weight: 700;
  }
  .field-opt {
    color: #64748b;
  }

  /* Code Block */
  pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 12px 14px;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    line-height: 1.4;
    overflow-x: auto;
    margin-bottom: 14px;
    border-left: 4px solid #3b82f6;
  }
  
  .json-key { color: #93c5fd; }
  .json-str { color: #86efac; }
  .json-num { color: #fde047; }
  .json-bool { color: #f472b6; }
</style>
</head>
<body>

<!-- Cover Page -->
<div class="cover">
  <div class="cover-header">
    <span class="cover-badge">Developer API Reference</span>
    <h1 class="cover-title">SAAPT 2.0 Backend<br>Action-Based API Collection</h1>
    <p class="cover-subtitle">Clear, Explicit Action Endpoints (add-student, delete-student, list-students, etc.)</p>
  </div>

  <div class="cover-info">
    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">Base URL (Local)</div>
        <div class="info-val">http://127.0.0.1:8000 / http://127.0.0.1:8001</div>
      </div>
      <div class="info-item">
        <div class="info-label">API Style</div>
        <div class="info-val">Action-Oriented (add-student, edit-student, delete-student)</div>
      </div>
      <div class="info-item">
        <div class="info-label">Authentication</div>
        <div class="info-val">JSON Web Token (JWT Bearer Token)</div>
      </div>
      <div class="info-item">
        <div class="info-label">Database</div>
        <div class="info-val">PostgreSQL (Supabase) / SQLite</div>
      </div>
      <div class="info-item">
        <div class="info-label">Content Types</div>
        <div class="info-val">application/json & multipart/form-data</div>
      </div>
      <div class="info-item">
        <div class="info-label">Release Version</div>
        <div class="info-val">Version 2.0 • Updated October 2026</div>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <span>Cliccot Technology — SAAPT 2.0 School ERP</span>
    <span>Intuitive Developer Integration Reference</span>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 1: STUDENT MANAGEMENT -->
<div class="section-header">
  <div class="section-title">1. Student Management (Action-Based APIs)</div>
  <div class="section-badge">Base: /api/</div>
</div>

<!-- API: Add Student -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/add-student/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">multipart/form-data</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Add Student API:</strong> Creates a new student admission record with personal details, parent information, and uploaded certificates.</div>
    <div class="block-title">Form Data Request Parameters</div>
    <table>
      <thead>
        <tr><th>Field</th><th>Type</th><th>Required</th><th>Description</th></tr>
      </thead>
      <tbody>
        <tr><td><span class="field-name">full_name</span></td><td><span class="field-type">string</span></td><td><span class="field-req">Required</span></td><td>Full legal name of the student.</td></tr>
        <tr><td><span class="field-name">date_of_birth</span></td><td><span class="field-type">date (YYYY-MM-DD)</span></td><td><span class="field-req">Required</span></td><td>Student date of birth.</td></tr>
        <tr><td><span class="field-name">gender</span></td><td><span class="field-type">string</span></td><td><span class="field-req">Required</span></td><td><code>Male</code>, <code>Female</code>, or <code>Other</code>.</td></tr>
        <tr><td><span class="field-name">academic_year</span></td><td><span class="field-type">integer (ID)</span></td><td><span class="field-req">Required</span></td><td>Academic year ID (e.g. 1).</td></tr>
        <tr><td><span class="field-name">class_section</span></td><td><span class="field-type">integer (ID)</span></td><td><span class="field-opt">Optional</span></td><td>Assigned class section ID.</td></tr>
        <tr><td><span class="field-name">roll_number</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Class roll number.</td></tr>
        <tr><td><span class="field-name">blood_group</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>e.g. <code>O+</code>, <code>A+</code>, <code>B+</code>.</td></tr>
        <tr><td><span class="field-name">father_name</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Parent / Father name.</td></tr>
        <tr><td><span class="field-name">mother_name</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Mother name.</td></tr>
        <tr><td><span class="field-name">mobile_number</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Primary contact phone number.</td></tr>
        <tr><td><span class="field-name">parent_email</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Parent email address.</td></tr>
        <tr><td><span class="field-name">address</span></td><td><span class="field-type">string</span></td><td><span class="field-opt">Optional</span></td><td>Full residential address.</td></tr>
        <tr><td><span class="field-name">student_photo</span></td><td><span class="field-type">file</span></td><td><span class="field-opt">Optional</span></td><td>Passport size photograph.</td></tr>
      </tbody>
    </table>
    <div class="block-title">Response (201 Created)</div>
    <pre>{
  <span class="json-key">"id"</span>: <span class="json-num">102</span>,
  <span class="json-key">"admission_number"</span>: <span class="json-str">"SAAPT-2026-042"</span>,
  <span class="json-key">"full_name"</span>: <span class="json-str">"Ananya Patel"</span>,
  <span class="json-key">"status"</span>: <span class="json-str">"active"</span>,
  <span class="json-key">"date_of_birth"</span>: <span class="json-str">"2015-09-20"</span>,
  <span class="json-key">"gender"</span>: <span class="json-str">"Female"</span>,
  <span class="json-key">"blood_group"</span>: <span class="json-str">"B+"</span>,
  <span class="json-key">"academic_year"</span>: <span class="json-num">1</span>,
  <span class="json-key">"class_section"</span>: <span class="json-num">2</span>,
  <span class="json-key">"roll_number"</span>: <span class="json-str">"08"</span>
}</pre>
  </div>
</div>

<!-- API: List Students -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/list-students/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>List Students API:</strong> Retrieves the student directory table with pagination, name/admission search, and class/section filters.</div>
    <div class="block-title">Query Parameters</div>
    <table>
      <thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td><span class="field-name">search</span></td><td><span class="field-type">string</span></td><td>Search student name or admission number.</td></tr>
        <tr><td><span class="field-name">class</span></td><td><span class="field-type">string/int</span></td><td>Filter by class name or class ID (e.g. <code>Class 6</code> or <code>1</code>).</td></tr>
        <tr><td><span class="field-name">section</span></td><td><span class="field-type">string/int</span></td><td>Filter by section letter or section ID (e.g. <code>A</code>).</td></tr>
        <tr><td><span class="field-name">status</span></td><td><span class="field-type">string</span></td><td><code>active</code>, <code>transferred</code>, <code>graduated</code>, <code>inactive</code>.</td></tr>
        <tr><td><span class="field-name">academic_year</span></td><td><span class="field-type">string/int</span></td><td>Filter by academic year (e.g. <code>2025-2026</code>).</td></tr>
        <tr><td><span class="field-name">page</span></td><td><span class="field-type">integer</span></td><td>Page number (default 10 items per page).</td></tr>
      </tbody>
    </table>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"count"</span>: <span class="json-num">245</span>,
  <span class="json-key">"next"</span>: <span class="json-str">"http://127.0.0.1:8000/api/list-students/?page=2"</span>,
  <span class="json-key">"previous"</span>: <span class="json-bool">null</span>,
  <span class="json-key">"results"</span>: [
    {
      <span class="json-key">"id"</span>: <span class="json-num">101</span>,
      <span class="json-key">"admission_number"</span>: <span class="json-str">"SAAPT-2025-001"</span>,
      <span class="json-key">"full_name"</span>: <span class="json-str">"Aarav Sharma"</span>,
      <span class="json-key">"class_display"</span>: <span class="json-str">"Class 6 - A"</span>,
      <span class="json-key">"roll_number"</span>: <span class="json-str">"12"</span>,
      <span class="json-key">"parent_name"</span>: <span class="json-str">"Rajesh Sharma"</span>,
      <span class="json-key">"parent_mobile"</span>: <span class="json-str">"+919876500001"</span>,
      <span class="json-key">"status"</span>: <span class="json-str">"active"</span>,
      <span class="json-key">"admission_date"</span>: <span class="json-str">"2025-06-01"</span>
    }
  ]
}</pre>
  </div>
</div>

<!-- API: View Student Profile -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/view-student/&lt;id&gt;/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>View Student Profile API:</strong> Returns complete student profile with parent info, documents, KPIs, and marksheet records.</div>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"id"</span>: <span class="json-num">101</span>,
  <span class="json-key">"admission_number"</span>: <span class="json-str">"SAAPT-2025-001"</span>,
  <span class="json-key">"full_name"</span>: <span class="json-str">"Aarav Sharma"</span>,
  <span class="json-key">"date_of_birth"</span>: <span class="json-str">"2014-05-12"</span>,
  <span class="json-key">"gender"</span>: <span class="json-str">"Male"</span>,
  <span class="json-key">"blood_group"</span>: <span class="json-str">"O+"</span>,
  <span class="json-key">"class_display"</span>: <span class="json-str">"Class 6 - A"</span>,
  <span class="json-key">"roll_number"</span>: <span class="json-str">"12"</span>,
  <span class="json-key">"status"</span>: <span class="json-str">"active"</span>,
  <span class="json-key">"overall_grade"</span>: <span class="json-str">"A+"</span>,
  <span class="json-key">"attendance_percentage"</span>: <span class="json-num">94.50</span>,
  <span class="json-key">"parent_guardian"</span>: {
    <span class="json-key">"father_name"</span>: <span class="json-str">"Rajesh Sharma"</span>,
    <span class="json-key">"mother_name"</span>: <span class="json-str">"Priya Sharma"</span>,
    <span class="json-key">"mobile_number"</span>: <span class="json-str">"+919876500001"</span>,
    <span class="json-key">"email"</span>: <span class="json-str">"rajesh.sharma@example.com"</span>
  }
}</pre>
  </div>
</div>

<!-- API: Edit Student -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-put">PUT</span> <span class="method method-patch">PATCH</span>
      <span>/api/edit-student/&lt;id&gt;/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">multipart/form-data</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Edit Student API:</strong> Updates an existing student's record and parent information.</div>
    <div class="block-title">Request Body Example (PATCH)</div>
    <pre>{
  <span class="json-key">"roll_number"</span>: <span class="json-str">"15"</span>,
  <span class="json-key">"status"</span>: <span class="json-str">"active"</span>,
  <span class="json-key">"mobile_number"</span>: <span class="json-str">"+919876599999"</span>
}</pre>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"id"</span>: <span class="json-num">101</span>,
  <span class="json-key">"full_name"</span>: <span class="json-str">"Aarav Sharma"</span>,
  <span class="json-key">"roll_number"</span>: <span class="json-str">"15"</span>,
  <span class="json-key">"status"</span>: <span class="json-str">"active"</span>
}</pre>
  </div>
</div>

<!-- API: Delete Student -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-delete">DELETE</span>
      <span>/api/delete-student/&lt;id&gt;/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Delete Student API:</strong> Permanently removes a student's profile and associated academic records from the database.</div>
    <div class="block-title">Response</div>
    <pre><span class="json-num">204</span> No Content (Empty Response Body)</pre>
  </div>
</div>

<!-- API: Student Stats -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/student-stats/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Student Stats API:</strong> Returns dashboard KPI metrics including total student counts, active/transferred counts, and per-class enrollment breakdowns.</div>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"total_students"</span>: <span class="json-num">450</span>,
  <span class="json-key">"active_students"</span>: <span class="json-num">420</span>,
  <span class="json-key">"transferred_students"</span>: <span class="json-num">12</span>,
  <span class="json-key">"graduated_students"</span>: <span class="json-num">15</span>,
  <span class="json-key">"new_admissions_this_month"</span>: <span class="json-num">28</span>,
  <span class="json-key">"class_breakdown"</span>: [
    {
      <span class="json-key">"id"</span>: <span class="json-num">1</span>,
      <span class="json-key">"school_class__name"</span>: <span class="json-str">"Class 6"</span>,
      <span class="json-key">"section__name"</span>: <span class="json-str">"A"</span>,
      <span class="json-key">"max_strength"</span>: <span class="json-num">40</span>,
      <span class="json-key">"active_count"</span>: <span class="json-num">38</span>
    }
  ]
}</pre>
  </div>
</div>

<!-- API: Bulk Allocate Students -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/bulk-allocate-students/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Bulk Allocate Students API:</strong> Atomically reallocates selected students to a new section, ensuring classroom capacity is not exceeded.</div>
    <div class="block-title">Request Body</div>
    <pre>{
  <span class="json-key">"student_ids"</span>: [<span class="json-num">101</span>, <span class="json-num">102</span>, <span class="json-num">105</span>],
  <span class="json-key">"target_class_section_id"</span>: <span class="json-num">3</span>
}</pre>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"message"</span>: <span class="json-str">"Successfully moved 3 students to Class 7 - B."</span>,
  <span class="json-key">"target_class_section"</span>: {
    <span class="json-key">"id"</span>: <span class="json-num">3</span>,
    <span class="json-key">"display_name"</span>: <span class="json-str">"Class 7 - B"</span>,
    <span class="json-key">"current_strength"</span>: <span class="json-num">35</span>,
    <span class="json-key">"max_strength"</span>: <span class="json-num">40</span>
  }
}</pre>
  </div>
</div>

<!-- API: Export Students & ID Card -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/export-students/ & /api/student-id-card/&lt;id&gt;/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Export Students:</strong> Generates CSV spreadsheet download.<br><strong>Student ID Card:</strong> Returns printable student badge information.</div>
    <div class="block-title">Student ID Card Response (200 OK)</div>
    <pre>{
  <span class="json-key">"school_name"</span>: <span class="json-str">"SAAPT International Public School"</span>,
  <span class="json-key">"student_name"</span>: <span class="json-str">"Aarav Sharma"</span>,
  <span class="json-key">"admission_number"</span>: <span class="json-str">"SAAPT-2025-001"</span>,
  <span class="json-key">"class_section"</span>: <span class="json-str">"Class 6 - A"</span>,
  <span class="json-key">"roll_number"</span>: <span class="json-str">"12"</span>,
  <span class="json-key">"blood_group"</span>: <span class="json-str">"O+"</span>,
  <span class="json-key">"emergency_contact"</span>: <span class="json-str">"+919876500001"</span>,
  <span class="json-key">"photo_url"</span>: <span class="json-str">"http://127.0.0.1:8000/media/students/photos/aarav.jpg"</span>
}</pre>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 2: CLASS & SECTION ALLOCATION -->
<div class="section-header">
  <div class="section-title">2. Class & Section Allocation (Action-Based APIs)</div>
  <div class="section-badge">Base: /api/</div>
</div>

<!-- API: List Class Sections -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/list-class-sections/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>List Class Sections API:</strong> Lists all allocated sections, assigned teachers, room numbers, and current vs. max student capacity.</div>
    <div class="block-title">Response (200 OK)</div>
    <pre>[
  {
    <span class="json-key">"id"</span>: <span class="json-num">1</span>,
    <span class="json-key">"academic_year"</span>: <span class="json-num">1</span>,
    <span class="json-key">"academic_year_name"</span>: <span class="json-str">"2025-2026"</span>,
    <span class="json-key">"school_class"</span>: <span class="json-num">1</span>,
    <span class="json-key">"class_name"</span>: <span class="json-str">"Class 6"</span>,
    <span class="json-key">"section"</span>: <span class="json-num">1</span>,
    <span class="json-key">"section_name"</span>: <span class="json-str">"A"</span>,
    <span class="json-key">"room_number"</span>: <span class="json-str">"Room 101"</span>,
    <span class="json-key">"class_teacher_name"</span>: <span class="json-str">"Mrs. Anjali Rao"</span>,
    <span class="json-key">"max_strength"</span>: <span class="json-num">40</span>,
    <span class="json-key">"current_strength"</span>: <span class="json-num">38</span>,
    <span class="json-key">"display_name"</span>: <span class="json-str">"Class 6 - A"</span>
  }
]</pre>
  </div>
</div>

<!-- API: Add Class Section -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/add-class-section/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Add Class Section API:</strong> Configures a new class and section allocation record.</div>
    <div class="block-title">Request Body</div>
    <pre>{
  <span class="json-key">"academic_year"</span>: <span class="json-num">1</span>,
  <span class="json-key">"school_class"</span>: <span class="json-num">2</span>,
  <span class="json-key">"section"</span>: <span class="json-num">1</span>,
  <span class="json-key">"room_number"</span>: <span class="json-str">"Room 204"</span>,
  <span class="json-key">"class_teacher_name"</span>: <span class="json-str">"Mr. Vikram Sen"</span>,
  <span class="json-key">"max_strength"</span>: <span class="json-num">45</span>
}</pre>
    <div class="block-title">Response (201 Created)</div>
    <pre>{
  <span class="json-key">"id"</span>: <span class="json-num">5</span>,
  <span class="json-key">"class_name"</span>: <span class="json-str">"Class 7"</span>,
  <span class="json-key">"section_name"</span>: <span class="json-str">"A"</span>,
  <span class="json-key">"display_name"</span>: <span class="json-str">"Class 7 - A"</span>,
  <span class="json-key">"current_strength"</span>: <span class="json-num">0</span>,
  <span class="json-key">"max_strength"</span>: <span class="json-num">45</span>
}</pre>
  </div>
</div>

<!-- API: Edit & Delete Class Section -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-put">PUT</span> <span class="method method-delete">DELETE</span>
      <span>/api/edit-class-section/&lt;id&gt;/ & /api/delete-class-section/&lt;id&gt;/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Edit Class Section:</strong> Modifies room number, teacher, or capacity.<br><strong>Delete Class Section:</strong> Removes an empty class section allocation.</div>
    <div class="block-title">Students in Section (GET /api/class-section-students/&lt;id&gt;/)</div>
    <pre>[
  {
    <span class="json-key">"id"</span>: <span class="json-num">101</span>,
    <span class="json-key">"admission_number"</span>: <span class="json-str">"SAAPT-2025-001"</span>,
    <span class="json-key">"full_name"</span>: <span class="json-str">"Aarav Sharma"</span>,
    <span class="json-key">"roll_number"</span>: <span class="json-str">"12"</span>,
    <span class="json-key">"status"</span>: <span class="json-str">"active"</span>
  }
]</pre>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 3: AUTHENTICATION -->
<div class="section-header">
  <div class="section-title">3. Authentication & Password Security</div>
  <div class="section-badge">Base: /api/auth/</div>
</div>

<!-- API: Forgot Password Flow -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/auth/forgot-password/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-no">No Auth Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Forgot Password API (Step 1 - Ask Mail ID & Send OTP):</strong> Asks user for their registered email address and sends a secure 6-digit OTP code (valid for 10 minutes).</div>
    <div class="block-title">Request Body</div>
    <pre>{
  <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>
}</pre>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"message"</span>: <span class="json-str">"OTP has been sent to your registered email address."</span>,
  <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>
}</pre>
  </div>
</div>

<!-- API: Verify OTP -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/auth/verify-otp/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-no">No Auth Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Verify OTP API (Step 2 - Verify Code):</strong> Validates the 6-digit code entered by the user. If correct, returns verification confirmation and reset token for step 3.</div>
    <div class="block-title">Request Body</div>
    <pre>{
  <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>,
  <span class="json-key">"otp"</span>: <span class="json-str">"582914"</span>
}</pre>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"message"</span>: <span class="json-str">"OTP verified successfully. You can now enter your new password."</span>,
  <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>,
  <span class="json-key">"reset_token"</span>: <span class="json-str">"u9mP0q-vA7Xz1bKr_8xL92aBcD4eFgHiJkLmNoPqRs"</span>
}</pre>
  </div>
</div>

<!-- API: Reset Password -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/auth/reset-password/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-no">No Auth Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Reset Password API (Step 3 - Set New Password & Confirm):</strong> Takes the new password and confirmation along with the verified OTP or reset token to update the password.</div>
    <div class="block-title">Request Body</div>
    <pre>{
  <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>,
  <span class="json-key">"reset_token"</span>: <span class="json-str">"u9mP0q-vA7Xz1bKr_8xL92aBcD4eFgHiJkLmNoPqRs"</span>,
  <span class="json-key">"new_password"</span>: <span class="json-str">"NewSecurePass@2026"</span>,
  <span class="json-key">"confirm_password"</span>: <span class="json-str">"NewSecurePass@2026"</span>
}</pre>
    <div class="block-title">Response (200 OK)</div>
    <pre>{
  <span class="json-key">"message"</span>: <span class="json-str">"Password changed successfully. You can now log in with your new password."</span>
}</pre>
  </div>
</div>

<!-- API: Login & Register & Profile -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-post">POST</span>
      <span>/api/auth/login/ & /api/auth/register/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-no">No Auth Required</span>
      <span class="meta-tag meta-format">application/json</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc"><strong>Login API:</strong> Log in via username or email.<br><strong>Register API:</strong> Staff user registration.</div>
    <div class="block-title">Login Request Body</div>
    <pre>{
  <span class="json-key">"username_or_email"</span>: <span class="json-str">"user@saapt.com"</span>,
  <span class="json-key">"password"</span>: <span class="json-str">"NewSecurePass@2026"</span>
}</pre>
    <div class="block-title">Login Response (200 OK)</div>
    <pre>{
  <span class="json-key">"message"</span>: <span class="json-str">"Login successful."</span>,
  <span class="json-key">"user"</span>: {
    <span class="json-key">"id"</span>: <span class="json-num">14</span>,
    <span class="json-key">"username"</span>: <span class="json-str">"sarah_admin"</span>,
    <span class="json-key">"email"</span>: <span class="json-str">"user@saapt.com"</span>
  },
  <span class="json-key">"tokens"</span>: {
    <span class="json-key">"access"</span>: <span class="json-str">"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."</span>,
    <span class="json-key">"refresh"</span>: <span class="json-str">"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."</span>
  }
}</pre>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 4: MASTER LOOKUPS -->
<div class="section-header">
  <div class="section-title">4. Master Lookups & Dropdowns (Action-Based APIs)</div>
  <div class="section-badge">Base: /api/</div>
</div>

<!-- API: Dropdowns -->
<div class="api-card">
  <div class="api-card-header">
    <div class="api-endpoint">
      <span class="method method-get">GET</span>
      <span>/api/get-classes/ & /api/get-sections/ & /api/get-academic-years/</span>
    </div>
    <div class="api-meta">
      <span class="meta-tag meta-auth-yes">Bearer Token Required</span>
    </div>
  </div>
  <div class="api-card-body">
    <div class="api-desc">Dropdown master data endpoints used for populating dropdown selections in forms and filter controls.</div>
    <div class="block-title">Example: GET /api/get-classes/ Response (200 OK)</div>
    <pre>[
  { <span class="json-key">"id"</span>: <span class="json-num">1</span>, <span class="json-key">"name"</span>: <span class="json-str">"Class 6"</span>, <span class="json-key">"code"</span>: <span class="json-str">"CLS-6"</span>, <span class="json-key">"numeric_order"</span>: <span class="json-num">6</span> },
  { <span class="json-key">"id"</span>: <span class="json-num">2</span>, <span class="json-key">"name"</span>: <span class="json-str">"Class 7"</span>, <span class="json-key">"code"</span>: <span class="json-str">"CLS-7"</span>, <span class="json-key">"numeric_order"</span>: <span class="json-num">7</span> }
]</pre>
    <div class="block-title">Example: GET /api/get-sections/ Response (200 OK)</div>
    <pre>[
  { <span class="json-key">"id"</span>: <span class="json-num">1</span>, <span class="json-key">"name"</span>: <span class="json-str">"A"</span> },
  { <span class="json-key">"id"</span>: <span class="json-num">2</span>, <span class="json-key">"name"</span>: <span class="json-str">"B"</span> }
]</pre>
    <div class="block-title">Example: GET /api/get-academic-years/ Response (200 OK)</div>
    <pre>[
  {
    <span class="json-key">"id"</span>: <span class="json-num">1</span>,
    <span class="json-key">"year_name"</span>: <span class="json-str">"2025-2026"</span>,
    <span class="json-key">"start_date"</span>: <span class="json-str">"2025-06-01"</span>,
    <span class="json-key">"end_date"</span>: <span class="json-str">"2026-04-30"</span>,
    <span class="json-key">"is_current"</span>: <span class="json-bool">true</span>
  }
]</pre>
  </div>
</div>

</body>
</html>
"""

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML at {HTML_FILE}")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

file_url = f"file:///{str(HTML_FILE).replace(os.sep, '/')}"

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={PDF_FILE}",
    file_url
]

subprocess.run(cmd, check=True)
print(f"Successfully compiled PDF to {PDF_FILE}")

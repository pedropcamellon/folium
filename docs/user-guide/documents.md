# Clinical Documents Guide

**Last Updated**: January 5, 2026

## Overview

The document management system allows you to upload, view, and organize clinical documents for each patient. Supported formats include PDFs, images (JPEG, PNG), and text files.

## Supported Document Types

- **Lab Results** - Blood tests, urinalysis, pathology reports
- **Imaging Reports** - X-rays, MRIs, CT scans
- **Prescriptions** - Medication orders and pharmacy records
- **Insurance Documents** - Insurance cards, authorization forms
- **Consent Forms** - Treatment consent, HIPAA forms
- **Clinical Notes** - SOAP notes, progress notes
- **Visit Summaries** - Discharge summaries, after-visit summaries
- **Referral Letters** - Specialist referrals, consultation notes
- **Administrative Forms** - Intake forms, patient questionnaires

## Uploading Documents

### Quick Upload

1. Open the patient's record
2. Navigate to the **Clinical Documents** section
3. Click **Upload Document** button
4. Drag and drop a file or click to browse
5. Select the document type from the dropdown
6. Edit the title (auto-filled from filename)
7. Optionally add a summary
8. Click **Upload**

### File Requirements

- **Maximum file size**: 10 MB
- **Allowed formats**:
  - PDF (`.pdf`)
  - Images (`.jpg`, `.jpeg`, `.png`)
  - Text (`.txt`)
  - Word documents (`.doc`, `.docx`)

### Upload Progress

A progress bar shows upload status. Once complete, the document appears in the patient's document list immediately.

## Viewing Documents

### Open Document Viewer

1. Locate the document in the patient's document list
2. Click the **eye icon** (👁️) to view
3. The document opens in a modal viewer

### Viewer Features

**For PDFs:**

- Page navigation (Previous/Next buttons)
- Page counter (e.g., "Page 3 of 15")
- Zoom controls (50% - 300%)
- Reset zoom button

**For Images:**

- Zoom in/out controls
- Responsive sizing (fits screen automatically)
- High-resolution viewing

**For Text Files:**

- Full-text display in readable format

**For All Documents:**

- Download button (saves to your device)
- Close button or click outside modal to dismiss

## Filtering Documents

### Filter by Document Type

1. Click the **Sort & Filter** button above the document list
2. Select one or more document types from the checkboxes:
   - Clinical Note
   - Lab Result
   - Imaging Report
   - Prescription
   - Admin Form
   - Visit Summary
   - Patient Upload
   - Billing/Coding
   - Communication
3. Selected types show with a checkmark
4. The document list updates automatically to show only selected types
5. Click **Clear** button in the filter menu to remove all filters

### Multiple Selection

You can select multiple document types simultaneously. For example:

- Select **Lab Result** + **Imaging Report** to see all diagnostic documents
- Select **Prescription** + **Clinical Note** to review treatment plans
- A badge indicator shows the number of active filters

### Sorting Documents

1. Click the **Sort & Filter** button
2. Choose from sort options:
   - **Date Created (Newest)** - Default, shows most recent first
   - **Date Created (Oldest)** - Shows oldest documents first
   - **Last Modified** - Shows recently updated documents
   - **Title (A-Z)** - Alphabetical by document title
3. The list updates automatically

### Tips

✅ Use filters to focus on specific document categories during patient visits  
✅ Combine filters to create custom views (e.g., all test results)  
✅ Sort by "Last Modified" to see recently updated documents  
✅ Badge indicator shows when filters or non-default sort are active  

## Searching Documents

### Quick Search

1. Type in the **Search documents...** input field above the document list
2. Search works across:
   - Document titles
   - Summaries
   - File names
3. Results update automatically as you type (debounced)
4. Search is case-insensitive

### Combining Search with Filters

Search and filters work together:

- **Search only**: Enter search term, all types included
- **Filter + Search**: Select document types, then search within those types
- **Example**: Filter to "Lab Result" + search "CBC" to find specific blood tests

### Clear Search

1. Click the **X** icon in the search input to clear
2. Or delete all text manually
3. Full document list returns immediately

### Search Tips

✅ Use partial words (e.g., "pres" finds "Prescription")  
✅ Search by patient symptoms in summaries  
✅ Search by file name if you remember the upload name  
✅ Combine with filters to narrow results (e.g., filter "Imaging" + search "chest")  
✅ Search updates in real-time (300ms delay to prevent lag)  

## Downloading Documents

1. Locate the document in the list
2. Click the **download icon** (⬇️)
3. The file opens in a new browser tab or downloads automatically

## Deleting Documents

1. Locate the document in the list
2. Click the **trash icon** (🗑️)
3. A confirmation dialog appears showing document details
4. Click **Delete Document** to confirm
5. The document is permanently removed

⚠️ **Warning**: Deletion cannot be undone.

## Common Workflows

### Workflow 1: Attaching Lab Results

**Scenario**: Lab results arrived via fax during patient visit

1. Click **Upload Document** in Clinical Documents section
2. Drag PDF file from desktop
3. System auto-selects type as "Lab Result"
4. Edit title: "Complete Blood Count Panel"
5. Click **Upload**
6. Click **eye icon** to review results during visit
7. Use zoom to examine specific values

**Duration**: < 1 minute

### Workflow 2: Viewing Previous Imaging

**Scenario**: Patient mentions previous X-ray from outside facility

1. Locate the X-ray in document list
2. Click **eye icon** to open viewer
3. Use zoom controls to examine details
4. Click download if you need to send to specialist
5. Close viewer to continue visit

**Duration**: < 30 seconds

### Workflow 3: Searching for Specific Documents

**Scenario**: Provider needs to find a specific prescription from 2 weeks ago

1. Navigate to Clinical Documents section
2. Type "prescription" in search box (or filter to Prescription type)
3. Search narrows results to prescriptions only
4. Scan titles and dates to find the specific one
5. Click **eye icon** to view details

**Duration**: < 10 seconds

### Workflow 4: Filtering to Review Lab Work

**Scenario**: Provider wants to review all recent lab results

1. Navigate to Clinical Documents section
2. Click **Lab Result** filter button
3. All lab documents are displayed, others hidden
4. Review results chronologically
5. Click **eye icon** on any lab to view details
6. Click **Clear All** to restore full document list

**Duration**: < 15 seconds

### Workflow 5: Uploading Insurance Cards

**Scenario**: New patient needs to upload insurance information

1. Take photo of insurance card (front)
2. Click **Upload Document**
3. Select photo from device
4. Choose type: "AdministrativeForm"
5. Title: "Insurance Card Front"
6. Repeat for back of card
7. Admin staff receives notification to review

**Duration**: < 2 minutes

## Tips & Best Practices

✅ **Use descriptive titles** - "CBC Panel 2026-01-04" instead of "lab.pdf"  
✅ **Add summaries** - Brief note helps others understand document purpose  
✅ **Choose correct type** - Proper categorization improves organization and filtering  
✅ **Delete obsolete documents** - Keep records clean and relevant  
✅ **Use zoom for details** - Especially helpful for imaging and lab results  
✅ **Use filters during visits** - Quickly focus on relevant document types  
✅ **Use search for quick lookup** - Faster than scrolling through long lists  
✅ **Combine search + filters** - Narrow results to exactly what you need  

## Troubleshooting

**Upload fails:**

- Check file size is under 10 MB
- Verify file type is supported
- Ensure stable internet connection

**Document won't open:**

- Try downloading instead
- Check browser allows pop-ups
- Refresh the page and try again

**Can't see uploaded document:**

- Wait a few seconds and refresh
- Check you're viewing the correct patient
- Verify upload completed successfully

**Search returns no results:**

- Check spelling of search term
- Try searching with fewer characters (e.g., "pres" instead of "prescription")
- Clear filters to search across all document types
- Verify documents exist with that term in title/summary/filename

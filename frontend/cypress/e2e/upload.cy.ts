describe('File Upload', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5174/upload')
  })

  it('should display upload interface', () => {
    cy.get('h4').should('contain', 'Upload Data')
    cy.contains('Upload your CSV files').should('exist')
    cy.contains('Only CSV files are accepted').should('exist')
  })

  it('should handle file upload', () => {
    // Create a sample CSV file
    cy.fixture('sample.csv', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        // Get the file input and attach the file
        cy.get('input[type="file"]').attachFile({
          fileContent,
          fileName: 'sample.csv',
          mimeType: 'text/csv'
        })
      })

    // Verify upload status appears
    cy.get('[role="alert"]').should('exist')
    cy.contains('Upload Status').should('exist')
  })

  it('should reject non-CSV files', () => {
    // Create a sample text file
    cy.fixture('sample.txt', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        // Get the file input and attach the file
        cy.get('input[type="file"]').attachFile({
          fileContent,
          fileName: 'sample.txt',
          mimeType: 'text/plain'
        })
      })

    // Verify error message
    cy.contains('Only CSV files are allowed').should('exist')
  })

  it('should handle drag and drop', () => {
    // Test drag and drop functionality
    cy.get('[role="button"]').trigger('dragenter')
    cy.contains('Drop the files here').should('exist')
    
    cy.get('[role="button"]').trigger('dragleave')
    cy.contains('Drag and drop files here').should('exist')
  })
}) 
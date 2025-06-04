describe('Navigation', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5174')
  })

  it('should display the dashboard by default', () => {
    cy.get('h4').should('contain', 'Welcome to PARLogic')
    cy.get('[data-testid="dashboard-summary"]').should('exist')
  })

  it('should navigate to Upload Data page', () => {
    cy.contains('Upload Data').click()
    cy.url().should('include', '/upload')
    cy.get('h4').should('contain', 'Upload Data')
  })

  it('should navigate to Analysis page', () => {
    cy.contains('Analysis').click()
    cy.url().should('include', '/analysis')
    cy.get('h4').should('contain', 'Usage Analysis')
  })

  it('should navigate to PAR Levels page', () => {
    cy.contains('PAR Levels').click()
    cy.url().should('include', '/par-levels')
    cy.get('h4').should('contain', 'PAR Level Calculator')
  })

  it('should show correct menu item as selected', () => {
    // Check dashboard is selected by default
    cy.get('.Mui-selected').should('contain', 'Dashboard')

    // Navigate to Upload and verify selection
    cy.contains('Upload Data').click()
    cy.get('.Mui-selected').should('contain', 'Upload Data')

    // Navigate to Analysis and verify selection
    cy.contains('Analysis').click()
    cy.get('.Mui-selected').should('contain', 'Analysis')

    // Navigate to PAR Levels and verify selection
    cy.contains('PAR Levels').click()
    cy.get('.Mui-selected').should('contain', 'PAR Levels')
  })
}) 
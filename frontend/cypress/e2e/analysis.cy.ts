describe('Analysis Page', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5174/analysis')
    // Intercept API calls
    cy.intercept('GET', '/analyze/usage/*', {
      statusCode: 200,
      body: {
        item_id: 'ITEM001',
        average_daily_usage: 25.5,
        peak_usage: 45,
        seasonality_factor: 1.2,
        trend: 'increasing',
        confidence_level: 0.95
      }
    }).as('analyzeUsage')
  })

  it('should display analysis interface', () => {
    cy.get('h4').should('contain', 'Usage Analysis')
    cy.contains('Analyze inventory usage patterns').should('exist')
  })

  it('should handle date selection and item ID input', () => {
    // Test date pickers
    cy.get('input[type="text"]').first().click()
    cy.get('.MuiPickersCalendar-root').should('exist')
    cy.contains('15').click()
    cy.get('.MuiPickersCalendar-root').should('not.exist')

    // Test item ID input
    cy.get('input[placeholder*="Item ID"]').type('ITEM001')
    cy.get('input[placeholder*="Item ID"]').should('have.value', 'ITEM001')
  })

  it('should perform analysis and display results', () => {
    // Fill in form
    cy.get('input[placeholder*="Item ID"]').type('ITEM001')
    
    // Click analyze button
    cy.contains('button', 'Analyze Usage').click()

    // Wait for API call
    cy.wait('@analyzeUsage')

    // Verify results are displayed
    cy.contains('Analysis Results').should('exist')
    cy.contains('Average Daily Usage').should('exist')
    cy.contains('25.5 units').should('exist')
    cy.contains('Peak Usage').should('exist')
    cy.contains('45 units').should('exist')
    cy.contains('Trend').should('exist')
    cy.contains('Increasing').should('exist')

    // Verify chart is displayed
    cy.get('canvas').should('exist')
  })

  it('should handle API errors gracefully', () => {
    // Mock API error
    cy.intercept('GET', '/analyze/usage/*', {
      statusCode: 500,
      body: { message: 'Internal server error' }
    }).as('analyzeUsageError')

    cy.get('input[placeholder*="Item ID"]').type('ITEM001')
    cy.contains('button', 'Analyze Usage').click()

    // Verify error message
    cy.get('[role="alert"]').should('exist')
    cy.contains('Failed to analyze usage').should('exist')
  })
}) 
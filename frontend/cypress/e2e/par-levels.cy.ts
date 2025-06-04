describe('PAR Levels Calculator', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5174/par-levels')
    // Intercept API calls
    cy.intercept('GET', '/calculate/par/*', {
      statusCode: 200,
      body: {
        item_id: 'ITEM001',
        min_par: 50,
        max_par: 150,
        reorder_point: 75,
        safety_stock: 25,
        service_level: 0.95,
        lead_time_days: 3
      }
    }).as('calculatePAR')

    cy.intercept('GET', '/recommendations/*', {
      statusCode: 200,
      body: {
        recommendations: [{
          item_id: 'ITEM001',
          current_stock: 60,
          recommended_action: 'Order soon',
          urgency: 'medium',
          details: 'Stock level approaching reorder point'
        }],
        timestamp: new Date().toISOString()
      }
    }).as('getRecommendations')
  })

  it('should display calculator interface', () => {
    cy.get('h4').should('contain', 'PAR Level Calculator')
    cy.contains('Calculate optimal PAR levels').should('exist')
  })

  it('should handle service level and lead time adjustments', () => {
    // Test service level slider
    cy.contains('Service Level').parent().find('input[type="range"]')
      .invoke('val', 0.99)
      .trigger('change')
    cy.contains('99%').should('exist')

    // Test lead time slider
    cy.contains('Lead Time').parent().find('input[type="range"]')
      .invoke('val', 7)
      .trigger('change')
    cy.contains('7').should('exist')
  })

  it('should calculate PAR levels and display results', () => {
    // Fill in item ID
    cy.get('input[placeholder*="Item ID"]').type('ITEM001')
    
    // Adjust service level and lead time
    cy.contains('Service Level').parent().find('input[type="range"]')
      .invoke('val', 0.95)
      .trigger('change')
    cy.contains('Lead Time').parent().find('input[type="range"]')
      .invoke('val', 3)
      .trigger('change')

    // Click calculate button
    cy.contains('button', 'Calculate PAR Levels').click()

    // Wait for API calls
    cy.wait(['@calculatePAR', '@getRecommendations'])

    // Verify results are displayed
    cy.contains('Calculated Levels').should('exist')
    cy.contains('Minimum PAR').should('exist')
    cy.contains('50 units').should('exist')
    cy.contains('Maximum PAR').should('exist')
    cy.contains('150 units').should('exist')
    cy.contains('Reorder Point').should('exist')
    cy.contains('75 units').should('exist')

    // Verify recommendations are displayed
    cy.contains('Recommendations').should('exist')
    cy.contains('Order soon').should('exist')
    cy.contains('Stock level approaching reorder point').should('exist')

    // Verify chart is displayed
    cy.get('canvas').should('exist')
  })

  it('should handle API errors gracefully', () => {
    // Mock API error
    cy.intercept('GET', '/calculate/par/*', {
      statusCode: 500,
      body: { message: 'Internal server error' }
    }).as('calculatePARError')

    cy.get('input[placeholder*="Item ID"]').type('ITEM001')
    cy.contains('button', 'Calculate PAR Levels').click()

    // Verify error message
    cy.get('[role="alert"]').should('exist')
    cy.contains('Failed to calculate PAR levels').should('exist')
  })
}) 
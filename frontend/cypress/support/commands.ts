// Extend Cypress namespace to include custom commands
declare namespace Cypress {
  interface Chainable {
    mockAnalyzeUsage(options?: Partial<UsagePattern>): void;
    mockCalculatePAR(options?: Partial<PARLevels>): void;
    mockRecommendations(options?: Partial<RecommendationResponse>): void;
  }
}

interface UsagePattern {
  item_id: string;
  average_daily_usage: number;
  peak_usage: number;
  seasonality_factor?: number;
  trend: string;
  confidence_level: number;
}

interface PARLevels {
  item_id: string;
  min_par: number;
  max_par: number;
  reorder_point: number;
  safety_stock: number;
  service_level: number;
  lead_time_days: number;
}

interface StockRecommendation {
  item_id: string;
  current_stock: number;
  recommended_action: string;
  urgency: string;
  details: string;
}

interface RecommendationResponse {
  recommendations: StockRecommendation[];
  timestamp: string;
}

// Mock analyze usage API
Cypress.Commands.add('mockAnalyzeUsage', (options = {}) => {
  const defaultResponse = {
    item_id: 'ITEM001',
    average_daily_usage: 25.5,
    peak_usage: 45,
    seasonality_factor: 1.2,
    trend: 'increasing',
    confidence_level: 0.95,
    ...options
  };

  cy.intercept('GET', '/analyze/usage/*', {
    statusCode: 200,
    body: defaultResponse
  }).as('analyzeUsage');
});

// Mock calculate PAR API
Cypress.Commands.add('mockCalculatePAR', (options = {}) => {
  const defaultResponse = {
    item_id: 'ITEM001',
    min_par: 50,
    max_par: 150,
    reorder_point: 75,
    safety_stock: 25,
    service_level: 0.95,
    lead_time_days: 3,
    ...options
  };

  cy.intercept('GET', '/calculate/par/*', {
    statusCode: 200,
    body: defaultResponse
  }).as('calculatePAR');
});

// Mock recommendations API
Cypress.Commands.add('mockRecommendations', (options = {}) => {
  const defaultResponse = {
    recommendations: [{
      item_id: 'ITEM001',
      current_stock: 60,
      recommended_action: 'Order soon',
      urgency: 'medium',
      details: 'Stock level approaching reorder point'
    }],
    timestamp: new Date().toISOString(),
    ...options
  };

  cy.intercept('GET', '/recommendations/*', {
    statusCode: 200,
    body: defaultResponse
  }).as('getRecommendations');
}); 
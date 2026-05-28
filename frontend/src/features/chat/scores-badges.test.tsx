import { render, screen } from '@testing-library/react'
import { ScoresBadges } from './scores-badges'

describe('ScoresBadges', () => {
  it('renders "Evaluating…" when status is pending', () => {
    render(<ScoresBadges status="pending" scores={null} onRetry={() => {}} />)
    expect(screen.getByText(/evaluating/i)).toBeInTheDocument()
  })

  it('renders three R/F/U badges with scores when status is resolved', () => {
    render(
      <ScoresBadges
        status="resolved"
        scores={{ relevancy: 0.9, faithfulness: 0.6, utilization: 0.3 }}
        onRetry={() => {}}
      />
    )
    expect(screen.getByLabelText(/relevancy/i)).toHaveTextContent('R')
    expect(screen.getByLabelText(/faithfulness/i)).toHaveTextContent('F')
    expect(screen.getByLabelText(/utilization/i)).toHaveTextContent('U')
  })

  it('colour-codes badges by threshold (green >= 0.8, amber 0.5-0.8, red < 0.5)', () => {
    render(
      <ScoresBadges
        status="resolved"
        scores={{ relevancy: 0.9, faithfulness: 0.6, utilization: 0.3 }}
        onRetry={() => {}}
      />
    )
    expect(screen.getByLabelText(/relevancy/i)).toHaveAttribute('data-tier', 'green')
    expect(screen.getByLabelText(/faithfulness/i)).toHaveAttribute('data-tier', 'amber')
    expect(screen.getByLabelText(/utilization/i)).toHaveAttribute('data-tier', 'red')
  })

  it('renders "Scoring failed — retry" when status is failed', () => {
    render(<ScoresBadges status="failed" scores={null} onRetry={() => {}} />)
    expect(screen.getByText(/scoring failed/i)).toBeInTheDocument()
  })

  it('renders nothing when status is idle', () => {
    const { container } = render(
      <ScoresBadges status="idle" scores={null} onRetry={() => {}} />
    )
    expect(container.firstChild).toBeNull()
  })
})

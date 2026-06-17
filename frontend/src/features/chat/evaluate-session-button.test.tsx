import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthContextProvider } from '@/lib/auth/context'
import { EvaluateSessionButton } from './evaluate-session-button'

function renderAs(
  role: 'admin' | 'user' | null,
  props: Partial<React.ComponentProps<typeof EvaluateSessionButton>> = {},
) {
  if (role) {
    localStorage.setItem('dos68k:role', role)
    localStorage.setItem('dos68k:token', `local-token-${role}`)
  } else {
    localStorage.clear()
  }
  const onClick = props.onClick ?? vi.fn()
  return {
    onClick,
    ...render(
      <AuthContextProvider>
        <EvaluateSessionButton onClick={onClick} {...props} />
      </AuthContextProvider>,
    ),
  }
}

describe('EvaluateSessionButton', () => {
  beforeEach(() => localStorage.clear())

  it('renders nothing for non-admin users', () => {
    const { container } = renderAs('user')
    expect(container.firstChild).toBeNull()
  })

  it('renders an "Evaluate rated answers" button for admin users', () => {
    renderAs('admin')
    expect(
      screen.getByRole('button', { name: /evaluate rated answers/i }),
    ).toBeInTheDocument()
  })

  it('exposes an honest tooltip — never "all" or "entire chat"', () => {
    renderAs('admin')
    const button = screen.getByRole('button', { name: /evaluate rated answers/i })
    const tooltip = button.getAttribute('title') ?? ''
    expect(tooltip.length).toBeGreaterThan(0)
    expect(tooltip).toMatch(/feedback/i)
    expect(tooltip).toMatch(/not.{0,15}scored|not.{0,15}evaluated/i)
    expect(tooltip).not.toMatch(/\ball\b/i)
    expect(tooltip).not.toMatch(/entire chat/i)
  })

  it('fires onClick when admin clicks the button', async () => {
    const user = userEvent.setup()
    const { onClick } = renderAs('admin')
    await user.click(screen.getByRole('button', { name: /evaluate rated answers/i }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when isPending is true and does not fire onClick', async () => {
    const user = userEvent.setup()
    const { onClick } = renderAs('admin', { isPending: true })
    const button = screen.getByRole('button', { name: /evaluate rated answers/i })
    expect(button).toBeDisabled()
    await user.click(button)
    expect(onClick).not.toHaveBeenCalled()
  })
})

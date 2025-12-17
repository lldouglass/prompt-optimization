import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { AgentsPage } from '../Agents'
import { agentApi } from '@/lib/api'
import type { OptimizationResult } from '@/lib/api'

// Mock the API
vi.mock('@/lib/api', () => ({
  agentApi: {
    optimize: vi.fn(),
    evaluate: vi.fn(),
    compare: vi.fn(),
  },
}))

const mockOptimizationResult: OptimizationResult = {
  original_prompt: 'You are a helpful assistant.',
  optimized_prompt: 'You are an expert assistant specializing in providing clear, accurate, and helpful responses.',
  original_score: 5.5,
  optimized_score: 8.2,
  improvements: [
    'Added specific role definition',
    'Clarified expected behavior',
    'Added quality constraints',
  ],
  reasoning: 'The optimized prompt provides clearer guidance and sets better expectations.',
  analysis: {
    issues: [
      { category: 'specificity', description: 'Prompt is too vague', severity: 'high' },
    ],
    strengths: ['Simple and clear'],
    overall_quality: 'fair',
    priority_improvements: ['Add role definition', 'Specify output format'],
  },
}

function renderAgentsPage() {
  return render(
    <BrowserRouter>
      <AgentsPage />
    </BrowserRouter>
  )
}

describe('Agents Page - Optimize Prompt Button', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the Optimize Prompt button with correct text and icon', () => {
    renderAgentsPage()

    const button = screen.getByRole('button', { name: /optimize prompt/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Optimize Prompt')
  })

  it('button is disabled when prompt template field is empty', () => {
    renderAgentsPage()

    const button = screen.getByRole('button', { name: /optimize prompt/i })
    expect(button).toBeDisabled()
  })

  it('button is disabled when task description field is empty', async () => {
    const user = userEvent.setup()
    renderAgentsPage()

    // Fill only the prompt template
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    await user.type(promptInput, 'You are a helpful assistant.')

    const button = screen.getByRole('button', { name: /optimize prompt/i })
    expect(button).toBeDisabled()
  })

  it('button is enabled when both prompt and task fields have content', async () => {
    const user = userEvent.setup()
    renderAgentsPage()

    // Fill both required fields
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    const taskInput = screen.getByPlaceholderText(/what should this prompt accomplish/i)

    await user.type(promptInput, 'You are a helpful assistant.')
    await user.type(taskInput, 'Answer user questions about Python')

    const button = screen.getByRole('button', { name: /optimize prompt/i })
    expect(button).toBeEnabled()
  })

  it('shows loading state when button is clicked', async () => {
    const user = userEvent.setup()

    // Make the API call hang
    vi.mocked(agentApi.optimize).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    renderAgentsPage()

    // Fill required fields
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    const taskInput = screen.getByPlaceholderText(/what should this prompt accomplish/i)

    await user.type(promptInput, 'You are a helpful assistant.')
    await user.type(taskInput, 'Answer user questions')

    // Click the button
    const button = screen.getByRole('button', { name: /optimize prompt/i })
    await user.click(button)

    // Check for loading state
    expect(screen.getByText(/optimizing/i)).toBeInTheDocument()
    expect(button).toBeDisabled()
  })

  it('displays optimization results after successful API call', async () => {
    const user = userEvent.setup()

    vi.mocked(agentApi.optimize).mockResolvedValue(mockOptimizationResult)

    renderAgentsPage()

    // Fill required fields
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    const taskInput = screen.getByPlaceholderText(/what should this prompt accomplish/i)

    await user.type(promptInput, 'You are a helpful assistant.')
    await user.type(taskInput, 'Answer user questions')

    // Click the button
    const button = screen.getByRole('button', { name: /optimize prompt/i })
    await user.click(button)

    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText(/optimization results/i)).toBeInTheDocument()
    })

    // Check that scores are displayed
    expect(screen.getByText('5.5')).toBeInTheDocument()
    expect(screen.getByText('8.2')).toBeInTheDocument()

    // Check that optimized prompt is displayed
    expect(screen.getByText(/expert assistant specializing/i)).toBeInTheDocument()

    // Check that improvements are listed
    expect(screen.getByText(/added specific role definition/i)).toBeInTheDocument()
  })

  it('calls agentApi.optimize with correct parameters', async () => {
    const user = userEvent.setup()

    vi.mocked(agentApi.optimize).mockResolvedValue(mockOptimizationResult)

    renderAgentsPage()

    // Fill all fields including optional samples
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    const taskInput = screen.getByPlaceholderText(/what should this prompt accomplish/i)
    const samplesInput = screen.getByPlaceholderText(/how do i read a file/i)

    await user.type(promptInput, 'You are a helpful assistant.')
    await user.type(taskInput, 'Answer Python questions')
    await user.type(samplesInput, 'How do I read a file?\nWhat is a decorator?')

    // Click the button
    const button = screen.getByRole('button', { name: /optimize prompt/i })
    await user.click(button)

    await waitFor(() => {
      expect(agentApi.optimize).toHaveBeenCalledWith(
        'You are a helpful assistant.',
        'Answer Python questions',
        ['How do I read a file?', 'What is a decorator?']
      )
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    vi.mocked(agentApi.optimize).mockRejectedValue(new Error('API Error'))

    renderAgentsPage()

    // Fill required fields
    const promptInput = screen.getByPlaceholderText(/enter your prompt template/i)
    const taskInput = screen.getByPlaceholderText(/what should this prompt accomplish/i)

    await user.type(promptInput, 'Test prompt')
    await user.type(taskInput, 'Test task')

    // Click the button
    const button = screen.getByRole('button', { name: /optimize prompt/i })
    await user.click(button)

    // Wait for loading to finish
    await waitFor(() => {
      expect(button).toBeEnabled()
    })

    // Error should be logged
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })
})
